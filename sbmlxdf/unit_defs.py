"""Implementation of Unit Definition components.

Peter Schubert, HHU Duesseldorf, October 2020
"""
import pandas as pd

import libsbml

from sbmlxdf.sbase import SBase
from sbmlxdf.misc import extract_params


class ListOfUnitDefs(SBase):

    def __init__(self):
        self.unit_defs = []
        super().__init__()

    def import_sbml(self, sbml_model):
        sbml_lud = sbml_model.getListOfUnitDefinitions()
        for sbml_ud in sbml_lud:
            ud = UnitDefinition()
            ud.import_sbml(sbml_ud)
            self.unit_defs.append(ud)
        super().import_sbml(sbml_lud)

    def export_sbml(self, sbml_model):
        for ud in self.unit_defs:
            ud.export_sbml(sbml_model)
        super().export_sbml(sbml_model.getListOfUnitDefinitions())

    def to_df(self):
        return pd.DataFrame([ud.to_df() for ud in self.unit_defs])\
                           .set_index('id')

    def from_df(self, lud_df):
        for idx, ud_s in lud_df.reset_index().iterrows():
            ud = UnitDefinition()
            ud.from_df(ud_s.dropna().to_dict())
            self.unit_defs.append(ud)


class UnitDefinition(SBase):

    def __init__(self):
        self.units = []
        super().__init__()

    def import_sbml(self, sbml_ud):
        for sbml_u in sbml_ud.getListOfUnits():
            unit = Unit()
            unit.import_sbml(sbml_u)
            self.units.append(unit)
        super().import_sbml(sbml_ud)

    def export_sbml(self, sbml_model):
        sbml_ud = sbml_model.createUnitDefinition()
        for u in self.units:
            u.export_sbml(sbml_ud)
        super().export_sbml(sbml_ud)

    def to_df(self):
        ud_dict = super().to_df()
        ud_dict['units'] = '; '.join(u.to_df() for u in self.units)
        return ud_dict

    def from_df(self, ud_dict):
        if 'units' in ud_dict:
            for unit_str in ud_dict['units'].split(';'):
                unit = Unit()
                unit.from_df(unit_str.strip())
                self.units.append(unit)
        super().from_df(ud_dict)


class Unit(SBase):

    def __init__(self):
        self.kind = None
        self.exponent = None
        self.scale = None
        self.multiplier = None
        super().__init__()
        pass

    def import_sbml(self, sbml_u):
        self.kind = libsbml.UnitKind_toString(sbml_u.getKind())
        self.exponent = sbml_u.getExponentAsDouble()
        self.scale = sbml_u.getScale()
        self.multiplier = sbml_u.getMultiplier()
        super().import_sbml(sbml_u)

    def export_sbml(self, sbml_ud):
        sbml_u = sbml_ud.createUnit()
        sbml_u.setKind(libsbml.UnitKind_forName(self.kind))
        sbml_u.setExponent(self.exponent)
        sbml_u.setScale(self.scale)
        sbml_u.setMultiplier(self.multiplier)
        super().export_sbml(sbml_u)

    def to_df(self):
        attr = ['kind=' + self.kind,
                'exp=' + str(self.exponent),
                'scale=' + str(self.scale),
                'mult=' + str(self.multiplier)]
        return ', '.join(attr)

    def from_df(self, unit_str):
        u_dict = extract_params(unit_str)
        self.kind = u_dict['kind']
        self.exponent = float(u_dict['exp'])
        self.scale = int(float(u_dict['scale']))
        self.multiplier = float(u_dict['mult'])
