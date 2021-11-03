"""Implementation of Compartment components.

Peter Schubert, HHU Duesseldorf, October 2020
"""
import pandas as pd

from sbmlxdf.sbase import SBase
from sbmlxdf.misc import get_bool_val


class ListOfCompartments(SBase):

    def __init__(self):
        self.compartments = []
        super().__init__()

    def import_sbml(self, sbml_model):
        sbml_lc = sbml_model.getListOfCompartments()
        for sbml_c in sbml_lc:
            c = Compartment()
            c.import_sbml(sbml_c)
            self.compartments.append(c)
        super().import_sbml(sbml_lc)

    def export_sbml(self, sbml_model):
        for c in self.compartments:
            c.export_sbml(sbml_model)
        super().export_sbml(sbml_model.getListOfCompartments())

    def to_df(self):
        return pd.DataFrame([c.to_df() for c in self.compartments])\
                           .set_index('id')

    def from_df(self, lc_df):
        for idx, c_s in lc_df.reset_index().iterrows():
            c = Compartment()
            c.from_df(c_s.dropna().to_dict())
            self.compartments.append(c)


class Compartment(SBase):

    def __init__(self):
        self.spatial_dim = None
        self.size = None
        self.units = None
        self.constant = None
        super().__init__()

    def import_sbml(self, sbml_c):
        if sbml_c.isSetSpatialDimensions():
            self.spatial_dim = sbml_c.getSpatialDimensionsAsDouble()
        if sbml_c.isSetSize():
            self.size = sbml_c.getSize()
        if sbml_c.isSetUnits():
            self.units = sbml_c.getUnits()
        self.constant = sbml_c.getConstant()
        super().import_sbml(sbml_c)

    def export_sbml(self, sbml_model):
        sbml_c = sbml_model.createCompartment()
        if self.spatial_dim is not None:
            sbml_c.setSpatialDimensions(self.spatial_dim)
        if self.size is not None:
            sbml_c.setSize(self.size)
        if self.units is not None:
            sbml_c.setUnits(self.units)
        sbml_c.setConstant(self.constant)
        super().export_sbml(sbml_c)

    def to_df(self):
        c_dict = super().to_df()
        if self.spatial_dim is not None:
            c_dict['spatialDimension'] = self.spatial_dim
        if self.size is not None:
            c_dict['size'] = self.size
        if self.units is not None:
            c_dict['units'] = self.units
        c_dict['constant'] = self.constant
        return c_dict

    def from_df(self, c_dict):
        if 'spatialDimension' in c_dict:
            self.spatial_dim = float(c_dict['spatialDimension'])
        if 'size' in c_dict:
            self.size = float(c_dict['size'])
        if 'units' in c_dict:
            self.units = c_dict['units']
        self.constant = get_bool_val(c_dict['constant'])

        super().from_df(c_dict)
