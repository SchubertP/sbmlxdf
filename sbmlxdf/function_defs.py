"""Implementation of Function Definition components.

Peter Schubert, HHU Duesseldorf, October 2020
"""
import pandas as pd
import sys

import libsbml

from sbmlxdf.sbase import SBase


class ListOfFunctionDefs(SBase):

    def __init__(self):
        self.function_defs = []
        super().__init__()

    def import_sbml(self, sbml_model):
        sbml_lfd = sbml_model.getListOfFunctionDefinitions()
        for sbml_fd in sbml_lfd:
            fd = FunctionDef()
            fd.import_sbml(sbml_fd)
            self.function_defs.append(fd)
        super().import_sbml(sbml_lfd)

    def export_sbml(self, sbml_model):
        for fd in self.function_defs:
            fd.export_sbml(sbml_model)
        sbml_lfd = sbml_model.getListOfFunctionDefinitions()
        super().export_sbml(sbml_lfd)

    def to_df(self):
        return pd.DataFrame([fd.to_df() for fd in self.function_defs])\
                           .set_index('id')

    def from_df(self, lfd_df):
        for idx, fd_s in lfd_df.reset_index().iterrows():
            fd = FunctionDef()
            fd.from_df(fd_s.dropna().to_dict())
            self.function_defs.append(fd)


class FunctionDef(SBase):

    def __init__(self):
        self.math = None
        super().__init__()

    def import_sbml(self, sbml_fd):
        self.math = libsbml.formulaToL3String(sbml_fd.getMath())
        super().import_sbml(sbml_fd)

    def export_sbml(self, sbml_model):
        sbml_fd = sbml_model.createFunctionDefinition()
        math = libsbml.parseL3Formula(self.math)
        if math:
            sbml_fd.setMath(math)
        else:
            print(libsbml.getLastParseL3Error())
            sys.exit()
        super().export_sbml(sbml_fd)

    def to_df(self):
        fd_dict = super().to_df()
        fd_dict['math'] = self.math
        return fd_dict

    def from_df(self, fd_dict):
        self.math = fd_dict['math']
        super().from_df(fd_dict)
