"""Implementation of Rules components.

Peter Schubert, HHU Duesseldorf, October 2020
"""
import pandas as pd
import sys

import libsbml

from sbmlxdf.sbase import SBase


class ListOfRules(SBase):

    def __init__(self):
        self.rules = []
        super().__init__()

    def import_sbml(self, sbml_model):
        sbml_lr = sbml_model.getListOfRules()
        for sbml_r in sbml_lr:
            r = Rule()
            r.import_sbml(sbml_r)
            self.rules.append(r)
        super().import_sbml(sbml_lr)

    def export_sbml(self, sbml_model):
        for r in self.rules:
            r.export_sbml(sbml_model)
        super().export_sbml(sbml_model.getListOfRules())

    def to_df(self):
        return pd.DataFrame([r.to_df() for r in self.rules])

    def from_df(self, lr_df):
        for idx, r_s in lr_df.iterrows():
            r = Rule()
            r.from_df(r_s.dropna().to_dict())
            self.rules.append(r)


class Rule(SBase):

    def __init__(self):
        self.math = None
        self.typecode = None
        self.ruletype = None
        self.variable = None
        super().__init__()

    def import_sbml(self, sbml_r):
        self.math = libsbml.formulaToL3String(sbml_r.getMath())
        self.typecode = sbml_r.getTypeCode()
        self.ruletype = libsbml.SBMLTypeCode_toString(sbml_r.getTypeCode(),
                                                      sbml_r.getPackageName())
        if (self.typecode == libsbml.SBML_ASSIGNMENT_RULE or
                self.typecode == libsbml.SBML_RATE_RULE):
            self.variable = sbml_r.getVariable()
        super().import_sbml(sbml_r)

    def export_sbml(self, sbml_model):
        if self.typecode == libsbml.SBML_ASSIGNMENT_RULE:
            sbml_r = sbml_model.createAssignmentRule()
            sbml_r.setVariable(self.variable)
        elif self.typecode == libsbml.SBML_RATE_RULE:
            sbml_r = sbml_model.createRateRule()
            sbml_r.setVariable(self.variable)
        elif self.typecode == libsbml.SBML_ALGEBRAIC_RULE:
            sbml_r = sbml_model.createAlgebraicRule()
        else:
            return
        math = libsbml.parseL3Formula(self.math)
        if math:
            sbml_r.setMath(math)
        else:
            print(libsbml.getLastParseL3Error())
            sys.exit()
        super().export_sbml(sbml_r)

    def to_df(self):
        r_dict = super().to_df()
        r_dict['rule'] = libsbml.SBMLTypeCode_toString(self.typecode, 'core')
        if self.variable is not None:
            r_dict['variable'] = self.variable
        r_dict['math'] = self.math
        return r_dict

    def from_df(self, r_dict):
        self.ruletype = r_dict['rule']
        if self.ruletype == libsbml.SBMLTypeCode_toString(
                                libsbml.SBML_ASSIGNMENT_RULE, 'core'):
            self.typecode = libsbml.SBML_ASSIGNMENT_RULE
            self.variable = r_dict['variable']
        if self.ruletype == libsbml.SBMLTypeCode_toString(
                                libsbml.SBML_RATE_RULE, 'core'):
            self.typecode = libsbml.SBML_RATE_RULE
            self.variable = r_dict['variable']
        if self.ruletype == libsbml.SBMLTypeCode_toString(
                                libsbml.SBML_ALGEBRAIC_RULE, 'core'):
            self.typecode = libsbml.SBML_ALGEBRAIC_RULE
        self.math = r_dict['math']
        super().from_df(r_dict)
