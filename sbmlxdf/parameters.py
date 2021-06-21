"""Implementation of Parameter components.

Peter Schubert, HHU Duesseldorf, October 2020
"""
import pandas as pd

import libsbml

from sbmlxdf.sbase import SBase


class ListOfParameters(SBase):

    def __init__(self):
        self.parameters = []
        super().__init__()

    def import_sbml(self, sbml_model):
        sbml_lp = sbml_model.getListOfParameters()
        for sbml_p in sbml_lp:
            p = Parameter()
            p.import_sbml(sbml_p)
            self.parameters.append(p)
        super().import_sbml(sbml_lp)

    def export_sbml(self, sbml_model):
        for p in self.parameters:
            p.export_sbml(sbml_model)
        super().export_sbml(sbml_model.getListOfParameters())

    def to_df(self):
        return pd.DataFrame([p.to_df() for p in self.parameters])\
                           .set_index('id')

    def from_df(self, lp_df):
        for idx, p_s in lp_df.reset_index().iterrows():
            p = Parameter()
            p.from_df(p_s.dropna().to_dict())
            self.parameters.append(p)


class Parameter(SBase):

    def __init__(self):
        super().__init__()

    def import_sbml(self, sbml_p):
        if sbml_p.isSetValue():
            self.value = sbml_p.getValue()
        if sbml_p.isSetUnits():
            self.units = sbml_p.getUnits()
        self.constant = sbml_p.getConstant()
        super().import_sbml(sbml_p)

    def export_sbml(self, sbml_model):
        sbml_p = sbml_model.createParameter()
        if hasattr(self, 'value'):
            sbml_p.setValue(self.value)
        if hasattr(self, 'units'):
            sbml_p.setUnits(self.units)
        sbml_p.setConstant(self.constant)
        super().export_sbml(sbml_p)

    def to_df(self):
        p_dict = super().to_df()
        if hasattr(self, 'value'):
            p_dict['value'] = self.value
        if hasattr(self, 'units'):
            p_dict['units'] = self.units
        p_dict['constant'] = self.constant
        return p_dict

    def from_df(self, p_dict):
        if 'value' in p_dict:
            self.value = float(p_dict['value'])
        if 'units' in p_dict:
            self.units = p_dict['units']
        self.constant = (p_dict['constant']==str(True) or
                         p_dict['constant']=='1')
        super().from_df(p_dict)
