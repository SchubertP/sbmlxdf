"""Implementation of SBML container attributes.

Peter Schubert, HHU Duesseldorf, October 2020
"""
import pandas as pd

import libsbml

from .sbase import SBase

# Explore_SBML_import_export_2020-10-05.ipynb

class SbmlContainer(SBase):

    def __init__(self):
        self.packages = {}
        super().__init__()

    def import_sbml(self, sbml_doc):
        super().import_sbml(sbml_doc)
        self.level = sbml_doc.getLevel()
        self.version = sbml_doc.getVersion()
        for idx in range(sbml_doc.getNumPlugins()):
            p = sbml_doc.getPlugin(idx)
            pname = p.getPackageName()
            self.packages[pname] = {'version': p.getPackageVersion(),
                                    'required': sbml_doc.getPkgRequired(pname)}

    def create_sbml_doc(self):
        sbml_container = libsbml.SBMLNamespaces(self.level, self.version)
        for pname in self.packages:
            sbml_container.addPackageNamespace(
                pname, self.packages[pname]['version'])
        sbml_doc = libsbml.SBMLDocument(sbml_container)
        self.export_sbml(sbml_doc)
        return sbml_doc

    def export_sbml(self, sbml_doc):
        super().export_sbml(sbml_doc)
        for pname in self.packages:
            sbml_doc.setPackageRequired(pname, self.packages[pname]['required'])

    def to_df(self):
        sc_dict = {}
        sc_dict['level'] = self.level
        sc_dict['version'] = self.version
        attr = []
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
            for pgk_vals in sc_dict['packages'].split(';'):
                pkg_dict = {}
                for attr in pgk_vals.split(','):
                    val = attr.split('=')
                    pkg_dict[val[0].strip()] = val[1].strip()
                self.packages[pkg_dict['name']] = {
                    'version': int(pkg_dict['version']),
                    'required': pkg_dict['required']==str(True)
                    }
        except KeyError as err:
            print("KeyError: {0} in {1}".format(err, __name__))
