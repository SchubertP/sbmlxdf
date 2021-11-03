"""Implementation of Parameter components.

Peter Schubert, HHU Duesseldorf, October 2020
"""
import pandas as pd

from sbmlxdf.sbase import SBase
from sbmlxdf.misc import get_bool_val


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
        self.value = None
        self.units = None
        self.constant = None
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
        if self.value is not None:
            sbml_p.setValue(self.value)
        if self.units is not None:
            sbml_p.setUnits(self.units)
        sbml_p.setConstant(self.constant)
        super().export_sbml(sbml_p)

    def to_df(self):
        p_dict = super().to_df()
        if self.value is not None:
            p_dict['value'] = self.value
        if self.units is not None:
            p_dict['units'] = self.units
        p_dict['constant'] = self.constant
        return p_dict

    def from_df(self, p_dict):
        if 'value' in p_dict:
            self.value = float(p_dict['value'])
        if 'units' in p_dict:
            self.units = p_dict['units']
        self.constant = get_bool_val(p_dict['constant'])
        super().from_df(p_dict)
