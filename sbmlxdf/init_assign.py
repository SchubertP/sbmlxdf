"""Implementation of Initial Assignment components.

Peter Schubert, HHU Duesseldorf, October 2020
"""
import pandas as pd
import sys

import libsbml

from sbmlxdf.sbase import SBase


class ListOfInitAssign(SBase):

    def __init__(self):
        self.init_assigns = []
        super().__init__()

    def import_sbml(self, sbml_model):
        sbml_lia = sbml_model.getListOfInitialAssignments()
        for sbml_ia in sbml_lia:
            ia = InitAssign()
            ia.import_sbml(sbml_ia)
            self.init_assigns.append(ia)
        super().import_sbml(sbml_lia)

    def export_sbml(self, sbml_model):
        for ia in self.init_assigns:
            ia.export_sbml(sbml_model)
        super().export_sbml(sbml_model.getListOfInitialAssignments())

    def to_df(self):
        return pd.DataFrame([ia.to_df() for ia in self.init_assigns])\
                           .set_index('symbol')

    def from_df(self, lia_df):
        for idx, ia_s in lia_df.reset_index().iterrows():
            ia = InitAssign()
            ia.from_df(ia_s.dropna().to_dict())
            self.init_assigns.append(ia)


class InitAssign(SBase):

    def __init__(self):
        self.symbol = None
        self.math = None
        super().__init__()

    def import_sbml(self, sbml_ia):
        self.symbol = sbml_ia.getSymbol()
        self.math = libsbml.formulaToL3String(sbml_ia.getMath())
        super().import_sbml(sbml_ia)

    def export_sbml(self, sbml_model):
        sbml_ia = sbml_model.createInitialAssignment()
        sbml_ia.setSymbol(self.symbol)
        math = libsbml.parseL3Formula(self.math)
        if math:
            sbml_ia.setMath(math)
        else:
            print(libsbml.getLastParseL3Error())
            sys.exit()
        super().export_sbml(sbml_ia)

    def to_df(self):
        ia_dict = super().to_df()
        ia_dict['symbol'] = self.symbol
        ia_dict['math'] = self.math
        return ia_dict

    def from_df(self, ia_dict):
        self.symbol = ia_dict['symbol']
        self.math = ia_dict['math']
        super().from_df(ia_dict)
