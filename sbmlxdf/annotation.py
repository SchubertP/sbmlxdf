"""Implementation of Annotations.

Peter Schubert, June 2021
Computational Cell Design, HHU Duesseldorf
"""
import time

import libsbml

from sbmlxdf.misc import extract_params

# RDF namespace for MIRIAM type annotations
rdf_namespace = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'


class Annotation:
    """Handle different kinds of annotations.

    there can be RDF type annotations, model history and miriam,
    which are handled by libsbml already

    there can be other annotations, which are must be handled handled via
    libsbml.XMLNode object. These other annotations allow the the modeller
    to extend the annotations that can be processed by his software. E.g.
    one could add molecular weights to species object. This requires
    a separate namespace, prefix and XML elements.

    Attributes
    ----------
        history: History or None
        cvterms: list of CVTerm objects
        xml_annots: list of XMLAnnotation objects

    """
    accepted_cols = {'miriam-annotation', 'xml-annotation'}

    @staticmethod
    def is_annotation(obj_dict):
        return (not Annotation.accepted_cols.isdisjoint(obj_dict.keys()) or
                History.is_history(obj_dict))

    def __init__(self):
        self.history = None
        self.cvterms = []
        self.xml_annots = []

    def import_sbml(self, sbml_obj):
        xml_annot_node = sbml_obj.getAnnotation()
        for n in range(xml_annot_node.getNumChildren()):
            xml_node = xml_annot_node.getChild(n)
            if xml_node.getURI() == rdf_namespace:
                if sbml_obj.isSetModelHistory():
                    self.history = History()
                    self.history.import_sbml(sbml_obj)
                if sbml_obj.getNumCVTerms() > 0:
                    for sbml_cv in sbml_obj.getCVTerms():
                        cv = CVTerm()
                        cv.import_sbml(sbml_cv)
                        self.cvterms.append(cv)
            else:
                xa = XMLAnnotation()
                xa.import_sbml(xml_node)
                self.xml_annots.append(xa)

    def export_sbml(self, sbml_obj):
        if self.history is not None:
            self.history.export_sbml(sbml_obj)
        for cv in self.cvterms:
            cv.export_sbml(sbml_obj)
        for xa in self.xml_annots:
            xa.export_sbml(sbml_obj)

    def to_df(self):
        annots_dict = {}
        if self.history is not None:
            annots_dict.update(self.history.to_df())
        if len(self.cvterms) > 0:
            annots_dict['miriam-annotation'] = '; '.join(cv.to_df()
                                                         for cv in self.cvterms)
        if len(self.xml_annots) > 0:
            annots_dict['xml-annotation'] = '; '.join(xa.to_df()
                                                      for xa in self.xml_annots)
        return annots_dict

    def from_df(self, obj_dict):
        if History.is_history(obj_dict):
            self.history = History()
            self.history.from_df(obj_dict)
        if 'miriam-annotation' in obj_dict:
            for cv_str in obj_dict['miriam-annotation'].split(';'):
                cv = CVTerm()
                cv.from_df(cv_str)
                self.cvterms.append(cv)
        if 'xml-annotation' in obj_dict:
            for xa_str in obj_dict['xml-annotation'].split(';'):
                xa = XMLAnnotation()
                xa.from_df(xa_str)
                self.xml_annots.append(xa)


class CVTerm:

    def __init__(self):
        self.qual_type = ''
        self.sub_type = ''
        self.resource_uri = []

    def import_sbml(self, sbml_cv):
        qual_type_id = sbml_cv.getQualifierType()
        if qual_type_id == libsbml.BIOLOGICAL_QUALIFIER:
            self.qual_type = 'bqbiol'
            self.sub_type = libsbml.BiolQualifierType_toString(
                                sbml_cv.getBiologicalQualifierType())
        if qual_type_id == libsbml.MODEL_QUALIFIER:
            self.qual_type = 'bqmodel'
            self.sub_type = libsbml.ModelQualifierType_toString(
                                sbml_cv.getModelQualifierType())
        for r_idx in range(sbml_cv.getNumResources()):
            self.resource_uri.append(sbml_cv.getResourceURI(r_idx))

    def export_sbml(self, sbml_obj):
        sbml_cv = libsbml.CVTerm()
        if self.qual_type == 'bqbiol':
            sbml_cv.setQualifierType(libsbml.BIOLOGICAL_QUALIFIER)
            sbml_cv.setBiologicalQualifierType(self.sub_type)
        if self.qual_type == 'bqmodel':
            sbml_cv.setQualifierType(libsbml.MODEL_QUALIFIER)
            sbml_cv.setModelQualifierType(self.sub_type)
        for uri in self.resource_uri:
            sbml_cv.addResource(uri)
            sbml_obj.addCVTerm(sbml_cv)

    def to_df(self):
        cv_str = self.qual_type + ':' + self.sub_type
        cv_str += ', ' + ', '.join([s.replace('http://identifiers.org/', '')
                                    for s in self.resource_uri])
        return cv_str

    def from_df(self, cv_str):
        try:
            parts = cv_str.split(',')
            qual = parts[0].split(':')
            self.qual_type = qual[0].strip()
            self.sub_type = qual[1].strip()
            for i in range(1, len(parts)):
                path = parts[i].strip()
                if not (path.find('urn:') == 0 or
                        path.find('http') == 0):
                    path = 'http://identifiers.org/' + path
                self.resource_uri.append(path)
        except IndexError as err:
            print(err)


class XMLAnnotation:
    """Hold information for simple annotations, that are not part RDF namespace.

    Attributes
    ----------
        ns_uri: str
            namespace URI, e.g. 'http://www.hhu.de/ccb/bgm/molecule/ns'
            first configured namespace in the SBML document is used
        prefix: str
            prefix assigned to namespace above. e.g. 'bgm'
        token: str
            name of token of the xml element, without prefix
        attrs: dict of str
            key - value pairs
    """
    def __init__(self):
        self.ns_uri = ''
        self.prefix = ''
        self.token = ''
        self.attrs = {}

    def import_sbml(self, xml_node):
        # we are just using first name space, if several are defined
        nss = xml_node.getNamespaces()
        if nss.getNumNamespaces() > 0:
            self.ns_uri = nss.getURI(0)
            self.prefix = nss.getPrefix(0)
        if xml_node.getPrefix() == self.prefix:
            self.token = xml_node.getName()
        for i in range(xml_node.getAttributesLength()):
            if xml_node.getAttrPrefix(i) == self.prefix:
                self.attrs[xml_node.getAttrName(i)] = xml_node.getAttrValue(i)

    def export_sbml(self, sbml_obj):
        if (self.ns_uri != '') and (self.prefix != '') and (self.token != ''):
            xml_triple = libsbml.XMLTriple(self.token, self.ns_uri, self.prefix)
            xml_nss = libsbml.XMLNamespaces()
            xml_nss.add(self.ns_uri, self.prefix)
            xml_attrs = libsbml.XMLAttributes()
            for k, v in self.attrs.items():
                xml_attrs.add(k, v, self.ns_uri, self.prefix)
            xml_node = libsbml.XMLNode(xml_triple, xml_attrs, xml_nss)
            sbml_obj.appendAnnotation(xml_node)

    def to_df(self):
        return ('ns_uri=' + self.ns_uri + ', ' +
                'prefix=' + self.prefix + ', ' +
                'token=' + self.token + ', ' +
                ', '.join([k + '=' + v for k, v in self.attrs.items()]))

    def from_df(self, xa_str):
        for kvp in xa_str.split(','):
            if '=' in kvp:
                k, v = kvp.split('=')
                k = k.strip()
                v = v.strip()
                if k == 'ns_uri':
                    self.ns_uri = v
                elif k == 'prefix':
                    self.prefix = v
                elif k == 'token':
                    self.token = v
                else:
                    self.attrs[k] = v


class History:
    """Hold information of RDF type history:

    Attributes:
    -----------
        created: str
            date when model was modified in format YYYY-MM-DD HH:MM:SS
        modified: list of str
            dates when model was modified in format YYYY-MM-DD HH:MM:SS
        creators: list of ModelCreator
            information of the model creators

    """
    accepted_cols = {'created-history', 'modified-history', 'creators-history'}

    @staticmethod
    def is_history(obj_dict):
        return not History.accepted_cols.isdisjoint(obj_dict.keys())

    def __init__(self):
        self.created = ''
        self.modified = []
        self.creators = []

    def import_sbml(self, sbml_obj):
        sbml_hist = sbml_obj.getModelHistory()
        if sbml_hist.isSetCreatedDate():
            self.created = sbml_hist.getCreatedDate().getDateAsString()
        for sbml_md in sbml_hist.getListModifiedDates():
            self.modified.append(sbml_md.getDateAsString())
        for sbml_mc in sbml_hist.getListCreators():
            mc = ModelCreator()
            mc.import_sbml(sbml_mc)
            self.creators.append(mc)

    def export_sbml(self, sbml_obj):
        sbml_hist = libsbml.ModelHistory()
        if self.created != '':
            sbml_hist.setCreatedDate(libsbml.Date(self.created))
        for md in self.modified:
            sbml_hist.addModifiedDate(libsbml.Date(md))
#        modified = libsbml.Date(time.strftime("%Y-%m-%dT%H:%M:%S%z"))
#        sbml_hist.addModifiedDate(modified)
        for mc in self.creators:
            mc.export_sbml(sbml_hist)
        sbml_obj.setModelHistory(sbml_hist)

    def to_df(self):
        mh_dict = {}
        if self.created != '':
            mh_dict['created-history'] = self.created
        if len(self.modified) > 0:
            mh_dict['modified-history'] = '; '.join(self.modified)
        if len(self.creators) > 0:
            mh_dict['creators-history'] = '; '.join([mc.to_df()
                                                     for mc in self.creators])
        return mh_dict

    def from_df(self, obj_dict):
        if 'created-history' in obj_dict:
            if obj_dict['created-history'] == 'localtime':
                self.created = time.strftime('%Y-%m-%dT%H:%M:%S%z',
                                             time.localtime())
            else:
                self.created = obj_dict['created-history']
        if 'modified-history' in obj_dict:
            for mod_date in obj_dict['modified-history'].split(';'):
                if mod_date.strip() == 'localtime':
                    self.modified.append(time.strftime('%Y-%m-%dT%H:%M:%S%z',
                                                       time.localtime()))
                else:
                    self.modified.append(mod_date.strip())
        if 'creators-history' in obj_dict:
            for creator in obj_dict['creators-history'].split(';'):
                mc = ModelCreator()
                mc.from_df(creator)
                self.creators.append(mc)


class ModelCreator:

    def __init__(self):
        self.fn = None
        self.gn = None
        self.org = None
        self.email = None
        pass

    def import_sbml(self, sbml_mc):
        if sbml_mc.isSetFamilyName():
            self.fn = sbml_mc.getFamilyName()
        if sbml_mc.isSetGivenName():
            self.gn = sbml_mc.getGivenName()
        if sbml_mc.isSetOrganisation():
            self.org = sbml_mc.getOrganisation()
        if sbml_mc.isSetEmail():
            self.email = sbml_mc.getEmail()

    def export_sbml(self, sbml_hist):
        sbml_mc = libsbml.ModelCreator()
        if self.fn is not None:
            sbml_mc.setFamilyName(self.fn)
        if self.gn is not None:
            sbml_mc.setGivenName(self.gn)
        if self.org is not None:
            sbml_mc.setOrganisation(self.org)
        if self.email is not None:
            sbml_mc.setEmail(self.email)
        sbml_hist.addCreator(sbml_mc)

    def to_df(self):
        attr = []
        if self.fn is not None:
            attr.append('fn=' + self.fn)
        if self.gn is not None:
            attr.append('gn=' + self.gn)
        if self.org is not None:
            attr.append('org=' + self.org)
        if self.email is not None:
            attr.append('email=' + self.email)
        return ', '.join(attr)

    def from_df(self, creator):
        mc_dict = extract_params(creator)
        if 'fn' in mc_dict:
            self.fn = mc_dict['fn']
        if 'gn' in mc_dict:
            self.gn = mc_dict['gn']
        if 'org' in mc_dict:
            self.org = mc_dict['org']
        if 'email' in mc_dict:
            self.email = mc_dict['email']
