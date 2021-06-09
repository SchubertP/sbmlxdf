"""Implementation of Model Attributes.

Peter Schubert, HHU Duesseldorf, October 2020
"""
import pandas as pd
import time

import libsbml

from sbmlxdf.sbase import SBase
from sbmlxdf.misc import extract_params


class ModelAttrs(SBase):

    def __init__(self):
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
        if sbml_model.isSetModelHistory():
            self.history = ModelHistory()
            self.history.import_sbml(sbml_model)
        if sbml_model.isPackageEnabled('fbc'):
            self.fbc_strict = sbml_model.getPlugin('fbc').getStrict()
        super().import_sbml(sbml_model)

    def export_sbml(self, sbml_model):
        if hasattr(self, 'substance_units'):
            sbml_model.setSubstanceUnits(self.substance_units)
        if hasattr(self, 'time_units'):
            sbml_model.setTimeUnits(self.time_units)
        if hasattr(self, 'volume_units'):
            sbml_model.setVolumeUnits(self.volume_units)
        if hasattr(self, 'area_units'):
            sbml_model.setAreaUnits(self.area_units)
        if hasattr(self, 'length_units'):
            sbml_model.setLengthUnits(self.length_units)
        if hasattr(self, 'extent_units'):
            sbml_model.setExtentUnits(self.extent_units)
        if hasattr(self, 'conversion_factor'):
            sbml_model.setConversionFactor(self.conversion_factor)
        if hasattr(self, 'fbc_strict'):
            sbml_model.getPlugin('fbc').setStrict(self.fbc_strict)
        super().export_sbml(sbml_model)
        # set model history after setting other annotations
        if hasattr(self, 'history'):
            self.history.export_sbml(sbml_model)

    def to_df(self):
        ma_dict = super().to_df()
        if hasattr(self, 'substance_units'):
            ma_dict['substanceUnits'] = self.substance_units
        if hasattr(self, 'time_units'):
            ma_dict['timeUnits'] = self.time_units
        if hasattr(self, 'volume_units'):
            ma_dict['volumeUnits'] = self.volume_units
        if hasattr(self, 'area_units'):
            ma_dict['areaUnits'] = self.area_units
        if hasattr(self, 'length_units'):
            ma_dict['lengthUnits'] = self.length_units
        if hasattr(self, 'extent_units'):
            ma_dict['extentUnits'] = self.extent_units
        if hasattr(self, 'conversion_factor'):
            ma_dict['conversionFactor'] = self.conversion_factor
        if hasattr(self, 'fbc_strict'):
            ma_dict['fbcStrict'] = self.fbc_strict
        if hasattr(self, 'history'):
            for key, val in self.history.to_df().items():
                ma_dict[key] = val
        return pd.Series(ma_dict)

    def from_df(self, ma_s):
        ma_dict = ma_s.dropna().to_dict()
        if 'substanceUnits' in ma_dict:
            self.substance_units= ma_dict['substanceUnits']
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
            self.fbc_strict = (ma_dict['fbcStrict']==str(True))
        if ModelHistory.is_in_df(ma_dict):
            self.history = ModelHistory()
            self.history.from_df(ma_dict)
        super().from_df(ma_dict)


class ModelHistory():

    def __init__(self):
        self.modified = []
        self.creators = []

    def import_sbml(self, sbml_model):
        sbml_hist = sbml_model.getModelHistory()
        if sbml_hist.isSetCreatedDate():
            self.created = sbml_hist.getCreatedDate().getDateAsString()
        for sbml_md in sbml_hist.getListModifiedDates():
            self.modified.append(sbml_md.getDateAsString())
        for sbml_mc in sbml_hist.getListCreators():
            mc = ModelCreator()
            mc.import_sbml(sbml_mc)
            self.creators.append(mc)

    def export_sbml(self, sbml_model):
        sbml_hist = libsbml.ModelHistory()
        if hasattr(self, 'created'):
            sbml_hist.setCreatedDate(libsbml.Date(self.created))
        for md in self.modified:
            sbml_hist.addModifiedDate(libsbml.Date(md))
#        modified = libsbml.Date(time.strftime("%Y-%m-%dT%H:%M:%S%z"))
#        sbml_hist.addModifiedDate(modified)
        for mc in self.creators:
            mc.export_sbml(sbml_hist)
        sbml_model.setModelHistory(sbml_hist)

    def to_df(self):
        mh_dict = {'created': getattr(self, 'created', '')}
        mh_dict['modified'] = '; '.join(self.modified)
        mh_dict['creators'] = '; '.join([mc.to_df() for mc in self.creators])
        return mh_dict

    def is_in_df(ma_dict):
        return len({'created', 'modified', 'creators'}.intersection(
                                                           ma_dict.keys()))

    def from_df(self, ma_dict):
        if 'created' in ma_dict:
            self.created = ma_dict['created']
        if 'modified' in ma_dict:
            for mod_date in ma_dict['modified'].split(';'):
                self.modified.append(mod_date.strip())
        if 'creators' in ma_dict:
            for creator in ma_dict['creators'].split(';'):
                mc = ModelCreator()
                mc.from_df(creator)
                self.creators.append(mc)


class ModelCreator():

    def __init__(self):
        pass

    def import_sbml(self, sbml_mc):
        if sbml_mc.isSetFamilyName():
            self.fn = sbml_mc.getFamilyName()
        if sbml_mc.isSetGivenName():
            self.gn = sbml_mc.getGivenName()
        if sbml_mc.isSetOrganisation():
            self.org = sbml_mc.getOrganisation()
        if sbml_mc.isSetEmail():
            self.email = sbml_mc.getEmail()

    def export_sbml(self, sbml_hist):
        sbml_mc = libsbml.ModelCreator()
        if hasattr(self, 'fn'):
            sbml_mc.setFamilyName(self.fn)
        if hasattr(self, 'gn'):
            sbml_mc.setGivenName(self.gn)
        if hasattr(self, 'org'):
            sbml_mc.setOrganisation(self.org)
        if hasattr(self, 'email'):
            sbml_mc.setEmail(self.email)
        sbml_hist.addCreator(sbml_mc)

    def to_df(self):
        attr = []
        if hasattr(self, 'fn'):
            attr.append('fn=' + self.fn)
        if hasattr(self, 'gn'):
            attr.append('gn=' + self.gn)
        if hasattr(self, 'org'):
            attr.append('org=' + self.org)
        if hasattr(self, 'email'):
            attr.append('email=' + self.email)
        return ', '.join(attr)

    def from_df(self, creator):
        mc_dict = extract_params(creator)
        if 'fn' in mc_dict:
            self.fn = mc_dict['fn']
        if 'gn' in mc_dict:
            self.gn = mc_dict['gn']
        if 'org' in mc_dict:
            self.org = mc_dict['org']
        if 'email' in mc_dict:
            self.email = mc_dict['email']
