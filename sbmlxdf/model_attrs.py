"""Implementation of Model Attributes.

Peter Schubert, HHU Duesseldorf, October 2020
"""
import pandas as pd

from sbmlxdf.sbase import SBase
from sbmlxdf.misc import get_bool_val


class ModelAttrs(SBase):

    def __init__(self):
        self.substance_units = None
        self.time_units = None
        self.volume_units = None
        self.area_units = None
        self.area_units = None
        self.length_units = None
        self.extent_units = None
        self.conversion_factor = None
        self.fbc_strict = None
        super().__init__()

    def import_sbml(self, sbml_model):
        if sbml_model.isSetSubstanceUnits():
            self.substance_units = sbml_model.getSubstanceUnits()
        if sbml_model.isSetTimeUnits():
            self.time_units = sbml_model.getTimeUnits()
        if sbml_model.isSetVolumeUnits():
            self.volume_units = sbml_model.getVolumeUnits()
        if sbml_model.isSetAreaUnits():
            self.area_units = sbml_model.getAreaUnits()
        if sbml_model.isSetLengthUnits():
            self.length_units = sbml_model.getLengthUnits()
        if sbml_model.isSetExtentUnits():
            self.extent_units = sbml_model.getExtentUnits()
        if sbml_model.isSetConversionFactor():
            self.conversion_factor = sbml_model.getConversionFactor()
        if sbml_model.isPackageEnabled('fbc'):
            self.fbc_strict = sbml_model.getPlugin('fbc').getStrict()
        super().import_sbml(sbml_model)

    def export_sbml(self, sbml_model):
        if self.substance_units is not None:
            sbml_model.setSubstanceUnits(self.substance_units)
        if self.time_units is not None:
            sbml_model.setTimeUnits(self.time_units)
        if self.volume_units is not None:
            sbml_model.setVolumeUnits(self.volume_units)
        if self.area_units is not None:
            sbml_model.setAreaUnits(self.area_units)
        if self.length_units is not None:
            sbml_model.setLengthUnits(self.length_units)
        if self.extent_units is not None:
            sbml_model.setExtentUnits(self.extent_units)
        if self.conversion_factor is not None:
            sbml_model.setConversionFactor(self.conversion_factor)
        if self.fbc_strict is not None:
            sbml_model.getPlugin('fbc').setStrict(self.fbc_strict)
        super().export_sbml(sbml_model)

    def to_df(self):
        ma_dict = super().to_df()
        if self.substance_units is not None:
            ma_dict['substanceUnits'] = self.substance_units
        if self.time_units is not None:
            ma_dict['timeUnits'] = self.time_units
        if self.volume_units is not None:
            ma_dict['volumeUnits'] = self.volume_units
        if self.area_units is not None:
            ma_dict['areaUnits'] = self.area_units
        if self.length_units is not None:
            ma_dict['lengthUnits'] = self.length_units
        if self.extent_units is not None:
            ma_dict['extentUnits'] = self.extent_units
        if self.conversion_factor is not None:
            ma_dict['conversionFactor'] = self.conversion_factor
        if self.fbc_strict is not None:
            ma_dict['fbcStrict'] = self.fbc_strict
        return pd.Series(ma_dict)

    def from_df(self, ma_s):
        ma_dict = ma_s.dropna().to_dict()
        if 'substanceUnits' in ma_dict:
            self.substance_units = ma_dict['substanceUnits']
        if 'timeUnits' in ma_dict:
            self.time_units = ma_dict['timeUnits']
        if 'volumeUnits' in ma_dict:
            self.volume_units = ma_dict['volumeUnits']
        if 'areaUnits' in ma_dict:
            self.area_units = ma_dict['areaUnits']
        if 'lengthUnits' in ma_dict:
            self.length_units = ma_dict['lengthUnits']
        if 'extentUnits' in ma_dict:
            self.extent_units = ma_dict['extentUnits']
        if 'conversionFactor' in ma_dict:
            self.conversion_factor = ma_dict['conversionFactor']
        if 'fbcStrict' in ma_dict:
            self.fbc_strict = get_bool_val(ma_dict['fbcStrict'])
        super().from_df(ma_dict)
