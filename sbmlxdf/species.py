"""Implementation of Species components.

   including fbc extensions
Peter Schubert, HHU Duesseldorf, October 2020
"""
import pandas as pd

import libsbml

from sbmlxdf.sbase import SBase


class ListOfSpecies(SBase):

    def __init__(self):
        self.species = []
        super().__init__()

    def import_sbml(self, sbml_model):
        sbml_ls = sbml_model.getListOfSpecies()
        for sbml_s in sbml_ls:
            s = Species()
            s.import_sbml(sbml_s)
            self.species.append(s)
        super().import_sbml(sbml_ls)

    def export_sbml(self, sbml_model):
        for s in self.species:
            s.export_sbml(sbml_model)
        super().export_sbml(sbml_model.getListOfSpecies())

    def to_df(self):
        return pd.DataFrame([s.to_df() for s in self.species])\
                           .set_index('id')

    def from_df(self, ls_df):
        for idx, s_s in ls_df.reset_index().iterrows():
            s = Species()
            s.from_df(s_s.dropna().to_dict())
            self.species.append(s)


class Species(SBase):

    def __init__(self):
        super().__init__()

    def import_sbml(self, sbml_s):
        self.compartment = sbml_s.getCompartment()
        if sbml_s.isSetInitialAmount():
            self.initial_amount = sbml_s.getInitialAmount()
        if sbml_s.isSetInitialConcentration():
            self.initial_concentration = sbml_s.getInitialConcentration()
        if sbml_s.isSetSubstanceUnits():
            self.substance_units = sbml_s.getSubstanceUnits()
        self.has_only_substance_units = sbml_s.getHasOnlySubstanceUnits()
        self.boundary_condition = sbml_s.getBoundaryCondition()
        self.constant = sbml_s.getConstant()
        if sbml_s.isSetConversionFactor():
            self.conversion_factor = sbml_s.getConversionFactor()
        if sbml_s.isPackageEnabled('fbc'):
            fbc_splugin = sbml_s.getPlugin('fbc')
            if fbc_splugin.isSetChemicalFormula():
                self.fbc_chem_formula = fbc_splugin.getChemicalFormula()
            if fbc_splugin.isSetCharge():
                self.fbc_charge = fbc_splugin.getCharge()
        super().import_sbml(sbml_s)

    def export_sbml(self, sbml_model):
        sbml_s = sbml_model.createSpecies()
        sbml_s.setCompartment(self.compartment)
        if hasattr(self, 'initial_amount'):
            sbml_s.setInitialAmount(self.initial_amount)
        if hasattr(self, 'initial_concentration'):
            sbml_s.setInitialConcentration(self.initial_concentration)
        if hasattr(self, 'substance_units'):
            sbml_s.setSubstanceUnits(self.substance_units)
        sbml_s.setHasOnlySubstanceUnits(self.has_only_substance_units)
        sbml_s.setBoundaryCondition(self.boundary_condition)
        sbml_s.setConstant(self.constant)
        if hasattr(self, 'conversion_factor'):
            sbml_s.setConversionFactor(self.conversion_factor)
        if hasattr(self, 'fbc_charge'):
            sbml_s.getPlugin('fbc').setCharge(self.fbc_charge)
        if hasattr(self, 'fbc_chem_formula'):
            sbml_s.getPlugin('fbc').setChemicalFormula(self.fbc_chem_formula)
        super().export_sbml(sbml_s)

    def to_df(self):
        s_dict = super().to_df()
        s_dict['compartment'] = self.compartment
        if hasattr(self, 'initial_amount'):
            s_dict['initialAmount'] = self.initial_amount
        if hasattr(self, 'initial_concentration'):
            s_dict['initialConcentration'] = self.initial_concentration
        if hasattr(self, 'substance_units'):
            s_dict['substanceUnits'] = self.substance_units
        s_dict['has_only_substance_units'] = self.has_only_substance_units
        s_dict['boundary_condition'] = self.boundary_condition
        s_dict['constant'] = self.constant
        if hasattr(self, 'conversion_factor'):
            s_dict['conversionFactor'] = self.conversion_factor
        if hasattr(self, 'fbc_charge'):
            s_dict['fbcCharge'] = self.fbc_charge
        if hasattr(self, 'fbc_chem_formula'):
            s_dict['fbcChemicalFormula'] = self.fbc_chem_formula
        return s_dict

    def from_df(self, s_dict):
        self.compartment = s_dict['compartment']
        if 'initialAmount' in s_dict:
            self.initial_amount = float(s_dict['initialAmount'])
        if 'initialConcentration' in s_dict:
            self.initial_concentration = float(s_dict['initialConcentration'])
        if 'substanceUnits' in s_dict:
            self.substance_units = s_dict['substanceUnits']
        self.has_only_substance_units = (
            s_dict['has_only_substance_units']==str(True) or
            s_dict['has_only_substance_units']=='1')
        self.boundary_condition = (s_dict['boundary_condition']==str(True) or
                                   s_dict['boundary_condition']=='1')
        self.constant = (s_dict['constant']==str(True) or
                         s_dict['constant']=='1')
        if 'conversionFactor' in s_dict:
            self.conversion_factor = s_dict['conversionFactor']
        if 'fbcCharge' in s_dict:
            self.fbc_charge = int(float(s_dict['fbcCharge']))
        if 'fbcChemicalFormula' in s_dict:
            self.fbc_chem_formula = s_dict['fbcChemicalFormula']
        super().from_df(s_dict)
