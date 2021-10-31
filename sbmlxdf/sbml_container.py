"""Implementation of SBML container attributes.

Peter Schubert, HHU Duesseldorf, October 2020
"""
import pandas as pd

import libsbml

from sbmlxdf.sbase import SBase
from sbmlxdf.misc import extract_records, extract_params, get_bool_val


class SbmlContainer(SBase):

    def __init__(self):
        self.packages = {}
        self.level = None
        self.version = None
        super().__init__()

    def import_sbml(self, sbml_doc):
        super().import_sbml(sbml_doc)
        self.level = sbml_doc.getLevel()
        self.version = sbml_doc.getVersion()

        for idx in range(sbml_doc.getNumPlugins()):
            p = sbml_doc.getPlugin(idx)
            pname = p.getPackageName()
            pversion = p.getPackageVersion()
            # there seems to be a bug, that l3v2extendedmath is returned
            if (idx == 0) and (pname == 'l3v2extendedmath') and (pversion == 0):
                continue

            # for SBML L2V4 layout and render are autoamtically imported
            if pname in ('layout', 'render'):
                continue
            self.packages[pname] = {'version': pversion,
                                    'required': sbml_doc.getPkgRequired(pname)}

    def create_sbml_doc(self):
        sbml_container = libsbml.SBMLNamespaces(self.level, self.version)
        for pname in self.packages:
            success = sbml_container.addPackageNamespace(
                      pname, self.packages[pname]['version'])
            if success != libsbml.LIBSBML_OPERATION_SUCCESS:
                print('Error adding package: [{}]. Try '
                      '"pip install python-libsbml-experimental".'.format(pname))
        sbml_doc = libsbml.SBMLDocument(sbml_container)
        self.export_sbml(sbml_doc)
        return sbml_doc

    def export_sbml(self, sbml_doc):
        super().export_sbml(sbml_doc)
        for pname in self.packages:
            sbml_doc.setPackageRequired(pname, self.packages[pname]['required'])

    def to_df(self):
        sc_dict = {'level': self.level,
                   'version': self.version}
        attr = []
        if len(self.packages) > 0:
            for pname, val in self.packages.items():
                attr.append(', '.join(['name=' + pname,
                                       'version=' + str(val['version']),
                                       'required=' + str(val['required'])]))
            sc_dict['packages'] = '; '.join(attr)
        return pd.Series(sc_dict)

    def from_df(self, sc_s):
        sc_dict = sc_s.dropna().to_dict()
        try:
            self.level = int(sc_dict['level'])
            self.version = int(sc_dict['version'])
            if 'packages' in sc_dict:
                for record in extract_records(sc_dict['packages']):
                    pkg_dict = extract_params(record)
                    self.packages[pkg_dict['name']] = {
                        'version': int(pkg_dict['version']),
                        'required': get_bool_val(pkg_dict['required'])
                        }
        except KeyError as err:
            print("KeyError: {0} in {1}".format(err, __name__))
