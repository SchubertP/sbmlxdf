"""Abstract Class SBase from core and Uncertainty components from distrib

Replicate of libsbml Class SBase.  Hold information common
to all objects in bgmsim.core.Model.

Peter Schubert, October 2020
Computational Cell Design, HHU Duesseldorf
"""
import re
import sys
from abc import ABC, abstractmethod

import libsbml

from sbmlxdf.annotation import Annotation
from sbmlxdf.misc import extract_params, extract_records, extract_lo_records

# RDF namespace for MIRIAM type annotations
rdf_namespace = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'


class SBase(ABC):
    """Abstract Class SBase, the base Class for any model object.

    Attributes
    ----------
    id: str
        The identifier to associate with the object.
    name: str
        Human readable label for the component.
        Empty string, if not assigned.
    sboterm: str
        Valid SBO Term ID: e.g. 'SBO:0000256'.
        Empty string, if not assigned.
    metaid: str
        Metaid required to link object with annotations.
        Empty string, if not assigned.
    annotation: list of bgmsim.core.CVTerms
        MIRIAM annotations connected with the object.
        Empty list, if not assigned.
    notes: dict
        Optional dict of note (used on Model Level)
    No checks of validity are done.
    """

    @abstractmethod
    def __init__(self):
        self.id = None
        self.name = None
        self.metaid = None
        self.sboterm = None
        self.annotation = None
        self.notes = None
        self.lo_uncertainties = None
        pass

    @abstractmethod
    def import_sbml(self, sbml_obj):
        if sbml_obj.isSetIdAttribute():
            self.id = sbml_obj.getIdAttribute()
        if sbml_obj.isSetName():
            self.name = sbml_obj.getName()
        if sbml_obj.isSetSBOTerm():
            self.sboterm = sbml_obj.getSBOTermID()
        if sbml_obj.isSetMetaId():
            self.metaid = sbml_obj.getMetaId()
        if sbml_obj.isSetAnnotation():
            self.annotation = Annotation()
            self.annotation.import_sbml(sbml_obj)
        if sbml_obj.isSetNotes():
            self.notes = sbml_obj.getNotesString()
        distrib_plugin = sbml_obj.getPlugin('distrib')
        if (distrib_plugin is not None
                and sbml_obj.getElementName() != 'sbml'
                and distrib_plugin.getNumUncertainties()):
            self.lo_uncertainties = ListOfUncertainties()
            self.lo_uncertainties.import_sbml(sbml_obj)

    @abstractmethod
    def export_sbml(self, sbml_obj):
        if self.id is not None:
            sbml_obj.setId(self.id)
        if self.name is not None:
            sbml_obj.setName(self.name)
        if self.sboterm is not None:
            sbml_obj.setSBOTerm(self.sboterm)
        if self.metaid is not None:
            sbml_obj.setMetaId(self.metaid)
        if self.annotation is not None:
            self.annotation.export_sbml(sbml_obj)
        if self.notes is not None:
            sbml_obj.setNotes(self.notes)
        if self.lo_uncertainties is not None:
            self.lo_uncertainties.export_sbml(sbml_obj)

    @abstractmethod
    def to_df(self):
        sb_dict = {}
        if self.id is not None:
            sb_dict['id'] = self.id
        if self.name is not None:
            sb_dict['name'] = self.name
        if self.metaid is not None:
            sb_dict['metaid'] = self.metaid
        if self.sboterm is not None:
            sb_dict['sboterm'] = self.sboterm
        if self.annotation is not None:
            sb_dict.update(self.annotation.to_df())
        if self.notes is not None:
            xnotes = libsbml.XMLNode.convertStringToXMLNode(self.notes)
            if isinstance(xnotes, libsbml.XMLNode) and xnotes.getNumChildren():
                sb_dict['notes'] = ''
                xbody = xnotes.getChild(0)
                for child in range(xbody.getNumChildren()):
                    sb_dict['notes'] += xbody.getChild(child).toXMLString().strip()
        if self.lo_uncertainties is not None:
            sb_dict['uncertainties'] = self.lo_uncertainties.to_df()
        return sb_dict

    @abstractmethod
    def from_df(self, obj_dict):
        if 'id' in obj_dict:
            self.id = obj_dict['id']
        if 'name' in obj_dict:
            self.name = obj_dict['name']
        if 'sboterm' in obj_dict:
            self.sboterm = obj_dict['sboterm']
        if 'metaid' in obj_dict:
            self.metaid = obj_dict['metaid']
        if Annotation.is_annotation(obj_dict):
            self.annotation = Annotation()
            self.annotation.from_df(obj_dict)
        if 'notes' in obj_dict:
            notes = ('<notes>'
                     '  <body xmlns="http://www.w3.org/1999/xhtml">'
                     '  </body>'
                     '</notes>')
            xnotes = libsbml.XMLNode.convertStringToXMLNode(notes)
            xbody = xnotes.getChild('body')
            xcontent = libsbml.XMLNode.convertStringToXMLNode(
                           ' ' + obj_dict['notes'] + ' ')
            if not xcontent.isEOF():
                xbody.addChild(xcontent)
            else:
                for i in range(xcontent.getNumChildren()):
                    xbody.addChild(xcontent.getChild(i))
            self.notes = xnotes.toXMLString()
        if 'uncertainties' in obj_dict:
            self.lo_uncertainties = ListOfUncertainties()
            self.lo_uncertainties.from_df(obj_dict['uncertainties'])


class ListOfUncertainties(SBase):

    def __init__(self):
        self.uncertainties = []
        super().__init__()

    def import_sbml(self, sbml_obj):
        distrib_plugin = sbml_obj.getPlugin('distrib')
        if distrib_plugin is not None:
            sbml_lu = distrib_plugin.getListOfUncertainties()
            for sbml_u in sbml_lu:
                u = Uncertainty()
                u.import_sbml(sbml_u)
                self.uncertainties.append(u)
            super().import_sbml(sbml_lu)

    def export_sbml(self, sbml_obj):
        distrib_plugin = sbml_obj.getPlugin('distrib')
        if distrib_plugin is not None:
            for u in self.uncertainties:
                sbml_u = distrib_plugin.createUncertainty()
                u.export_sbml(sbml_u)
            super().export_sbml(distrib_plugin.getListOfUncertainties())

    def to_df(self):
        return '; '.join(u.to_df() for u in self.uncertainties)

    def from_df(self, lou_str):
        for u_str in extract_lo_records(lou_str):
            if len(u_str):
                u = Uncertainty()
                u.from_df(u_str)
                self.uncertainties.append(u)


class Uncertainty(SBase):

    def __init__(self):
        self.uncert_parameters = []
        super().__init__()

    def import_sbml(self, sbml_u):
        sbml_lup = sbml_u.getListOfUncertParameters()
        for sbml_up in sbml_lup:
            if sbml_up.getElementName() == 'uncertParameter':
                up = UncertParameter()
            else:
                up = UncertScan()
            up.import_sbml(sbml_up)
            self.uncert_parameters.append(up)
        super().import_sbml(sbml_u)

    def export_sbml(self, sbml_u):
        for up in self.uncert_parameters:
            if isinstance(up, UncertScan):
                sbml_up = sbml_u.createUncertSpan()
            else:
                sbml_up = sbml_u.createUncertParameter()
            up.export_sbml(sbml_up)
        super().export_sbml(sbml_u.getListOfUncertParameters())

    def to_df(self):
        ups_str = []
        for up in self.uncert_parameters:
            ups_str.append(', '.join(up.to_df()))
        return '[' + '; '.join(ups_str) + ']'

    def from_df(self, u_str):
        for up_str in extract_records(u_str):
            if re.search(r'^\s*param', up_str):
                up = UncertParameter()
            else:
                up = UncertScan()
            up.from_df(up_str)
            self.uncert_parameters.append(up)


class UncertParameter(SBase):

    def __init__(self):
        self.element = None
        self.type = None
        self.value = None
        self.var = None
        self.units = None
        self.url = None
        self.math = None
        self.lo_uncert_parameters = None
        super().__init__()

    def import_sbml(self, sbml_up):
        self.element = sbml_up.getElementName()
        self.type = sbml_up.getTypeAsString()
        if sbml_up.isSetValue():
            self.value = sbml_up.getValue()
        if sbml_up.isSetVar():
            self.var = sbml_up.getVar()
        if sbml_up.isSetUnits():
            self.units = sbml_up.getUnits()
        if sbml_up.isSetDefinitionURL():
            self.url = sbml_up.getDefinitionURL()
        if sbml_up.isSetMath():
            self.math = libsbml.formulaToL3String(sbml_up.getMath())
        if sbml_up.getNumUncertParameters():
            self.lo_uncert_parameters = Uncertainty()
            self.lo_uncert_parameters.import_sbml(sbml_up)
        super().import_sbml(sbml_up)

    def export_sbml(self, sbml_up):
        sbml_up.setType(self.type)
        if self.value is not None:
            sbml_up.setValue(self.value)
        if self.var is not None:
            sbml_up.setVar(self.var)
        if self.units is not None:
            sbml_up.setUnits(self.units)
        if self.url is not None:
            sbml_up.setDefinitionURL(self.url)
        if self.math is not None:
            math = libsbml.parseL3Formula(self.math)
            if math:
                sbml_up.setMath(math)
            else:
                print(libsbml.getLastParseL3Error())
                sys.exit()
        if self.lo_uncert_parameters is not None:
            self.lo_uncert_parameters.export_sbml(sbml_up)
        super().export_sbml(sbml_up)

    def to_df(self):
        attr = ['param=' + self.type]
        if self.value is not None:
            attr.append('val=' + str(self.value))
        if self.var is not None:
            attr.append('var=' + self.var)
        if self.units is not None:
            attr.append('units=' + self.units)
        if self.url is not None:
            attr.append('url=' + self.url)
        if self.math is not None:
            attr.append('math=' + self.math)
        for key, val in super().to_df().items():
            if val:
                attr.append(key + '=' + val)
        if self.lo_uncert_parameters is not None:
            lup_str = self.lo_uncert_parameters.to_df()
            attr.append('lup=' + lup_str)
        return attr

    def from_df(self, up_str):
        up_dict = extract_params(up_str)
        if 'param' in up_dict:
            self.element = 'param'
            self.type = up_dict['param']
        else:
            self.element = 'scan'
            self.type = up_dict['scan']
        if 'lup' in up_dict:
            self.lo_uncert_parameters = Uncertainty()
            self.lo_uncert_parameters.from_df(up_dict['lup'])
        if 'val' in up_dict:
            self.value = float(up_dict['val'])
        if 'var' in up_dict:
            self.var = up_dict['var']
        if 'units' in up_dict:
            self.units = up_dict['units']
        if 'url' in up_dict:
            self.url = up_dict['url']
        if 'math' in up_dict:
            self.math = up_dict['math']
        super().from_df(up_dict)


class UncertScan(UncertParameter):

    def __init__(self):
        self.value_lower = None
        self.value_upper = None
        self.var_lower = None
        self.var_upper = None
        super().__init__()

    def import_sbml(self, sbml_up):
        if sbml_up.isSetValueLower():
            self.value_lower = sbml_up.getValueLower()
        if sbml_up.isSetValueUpper():
            self.value_upper = sbml_up.getValueUpper()
        if sbml_up.isSetVarLower():
            self.var_lower = sbml_up.getVarLower()
        if sbml_up.isSetVarUpper():
            self.var_upper = sbml_up.getVarUpper()
        super().import_sbml(sbml_up)

    def export_sbml(self, sbml_up):
        if self.value_lower is not None:
            sbml_up.setValueLower(self.value_lower)
        if self.value_upper is not None:
            sbml_up.setValueUpper(self.value_upper)
        if self.var_lower is not None:
            sbml_up.setVarLower(self.var_lower)
        if self.var_upper is not None:
            sbml_up.setVarUpper(self.var_upper)
        super().export_sbml(sbml_up)

    def to_df(self):
        attr = super().to_df()
        attr[0] = attr[0].replace('param', 'scan', 1)
        if self.value_lower is not None:
            attr.append('vall=' + str(self.value_lower))
        if self.value_upper is not None:
            attr.append('valu=' + str(self.value_upper))
        if self.var_lower is not None:
            attr.append('varl=' + self.var_lower)
        if self.var_upper is not None:
            attr.append('varu=' + self.var_upper)
        return attr

    def from_df(self, up_str):
        us_dict = extract_params(up_str)
        if 'vall' in us_dict:
            self.value_lower = float(us_dict['vall'])
        if 'valu' in us_dict:
            self.value_upper = float(us_dict['valu'])
        if 'varl' in us_dict:
            self.var_lower = us_dict['varl']
        if 'varu' in us_dict:
            self.var_upper = us_dict['varu']
        super().from_df(up_str)
