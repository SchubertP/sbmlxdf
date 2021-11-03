"""Implementation of Reaction components.

   including fbc extention

Peter Schubert, HHU Duesseldorf, October 2020
"""
import pandas as pd
import sys

import libsbml

from sbmlxdf.sbase import SBase
from sbmlxdf.misc import extract_params, get_bool_val


class ListOfReactions(SBase):

    def __init__(self):
        self.reactions = []
        super().__init__()

    def import_sbml(self, sbml_model):
        sbml_lr = sbml_model.getListOfReactions()
        for sbml_r in sbml_lr:
            r = Reaction()
            r.import_sbml(sbml_r)
            self.reactions.append(r)
        super().import_sbml(sbml_lr)

    def export_sbml(self, sbml_model):
        for r in self.reactions:
            r.export_sbml(sbml_model)
        super().export_sbml(sbml_model.getListOfReactions())

    def to_df(self):
        return pd.DataFrame([r.to_df() for r in self.reactions])\
                           .set_index('id')

    def from_df(self, lr_df):
        for idx, r_s in lr_df.reset_index().iterrows():
            r = Reaction()
            r.from_df(r_s.dropna().to_dict())
            self.reactions.append(r)


class Reaction(SBase):

    def __init__(self):
        self.reactants = []
        self.products = []
        self.modifiers = []
        self.reversible = None
        self.fast = None
        self.compartment = None
        self.kinetic_law = None
        self.fbc_enabled = None
        self.fbc_lb = None
        self.fbc_ub = None
        self.fbc_gpa = None
        super().__init__()

    def import_sbml(self, sbml_r):
        self.reversible = sbml_r.getReversible()
        if sbml_r.isSetFast():
            self.fast = sbml_r.getFast()
        if sbml_r.isSetCompartment():
            self.compartment = sbml_r.getCompartment()
        if sbml_r.getNumReactants():
            sbml_lsr = sbml_r.getListOfReactants()
            for sbml_sr in sbml_lsr:
                sr = ReacSpeciesRef()
                sr.import_sbml(sbml_sr)
                self.reactants.append(sr)
        if sbml_r.getNumProducts():
            sbml_lsr = sbml_r.getListOfProducts()
            for sbml_sr in sbml_lsr:
                sr = ProdSpeciesRef()
                sr.import_sbml(sbml_sr)
                self.products.append(sr)
        if sbml_r.getNumModifiers():
            sbml_lmsr = sbml_r.getListOfModifiers()
            for sbml_msr in sbml_lmsr:
                msr = ModSpeciesRef()
                msr.import_sbml(sbml_msr)
                self.modifiers.append(msr)
        if sbml_r.isSetKineticLaw():
            self.kinetic_law = KineticLaw()
            self.kinetic_law.import_sbml(sbml_r)
        if sbml_r.isPackageEnabled('fbc'):
            self.fbc_enabled = True
            fbc_rplugin = sbml_r.getPlugin('fbc')
            if fbc_rplugin.isSetLowerFluxBound():
                self.fbc_lb = fbc_rplugin.getLowerFluxBound()
            if fbc_rplugin.isSetUpperFluxBound():
                self.fbc_ub = fbc_rplugin.getUpperFluxBound()
            if fbc_rplugin.isSetGeneProductAssociation():
                self.fbc_gpa = FbcGeneProdAssociation()
                self.fbc_gpa.import_sbml(sbml_r)
        super().import_sbml(sbml_r)

    def export_sbml(self, sbml_model):
        sbml_r = sbml_model.createReaction()
        sbml_r.setReversible(self.reversible)
        if ((sbml_model.getLevel() < 3.0) or
                (sbml_model.getLevel() == 3.0 and sbml_model.getVersion() == 1.0)):
            sbml_r.setFast(getattr(self, 'fast', False))
        if self.compartment is not None:
            sbml_r.setCompartment(self.compartment)
        for r in self.reactants:
            r.export_sbml(sbml_r)
        for p in self.products:
            p.export_sbml(sbml_r)
        for m in self.modifiers:
            m.export_sbml(sbml_r)
        if self.kinetic_law is not None:
            self.kinetic_law.export_sbml(sbml_r)
        if self.fbc_enabled is not None:
            fbc_rplugin = sbml_r.getPlugin('fbc')
            if self.fbc_lb is not None:
                fbc_rplugin.setLowerFluxBound(self.fbc_lb)
            if self.fbc_ub is not None:
                fbc_rplugin.setUpperFluxBound(self.fbc_ub)
            if self.fbc_gpa is not None:
                self.fbc_gpa.export_sbml(sbml_r)
        super().export_sbml(sbml_r)

    def to_df(self):
        r_dict = super().to_df()
        r_dict['reversible'] = self.reversible
        if self.compartment is not None:
            r_dict['compartment'] = self.compartment
        if len(self.reactants):
            r_dict['reactants'] = '; '.join(r.to_df() for r in self.reactants)
        if len(self.products):
            r_dict['products'] = '; '.join(p.to_df() for p in self.products)
        if len(self.modifiers):
            r_dict['modifiers'] = '; '.join(m.to_df() for m in self.modifiers)
        if self.kinetic_law is not None:
            kl_dict = self.kinetic_law.to_df()
            r_dict['kineticLaw'] = kl_dict['math']
            if 'localParams' in kl_dict:
                r_dict['localParams'] = kl_dict['localParams']
        if self.fbc_enabled is not None:
            if self.fbc_lb is not None:
                r_dict['fbcLowerFluxBound'] = self.fbc_lb
            if self.fbc_ub is not None:
                r_dict['fbcUpperFluxBound'] = self.fbc_ub
            if self.fbc_gpa is not None:
                r_dict['fbcGeneProdAssoc'] = self.fbc_gpa.to_df()
        return r_dict

    def from_df(self, r_dict):
        self.reversible = get_bool_val(r_dict['reversible'])
        if 'compartment' in r_dict:
            self.compartment = r_dict['compartment']
        if 'reactants' in r_dict:
            for r_str in r_dict['reactants'].split(';'):
                sr = ReacSpeciesRef()
                sr.from_df(r_str.strip())
                self.reactants.append(sr)
        if 'products' in r_dict:
            for p_str in r_dict['products'].split(';'):
                sr = ProdSpeciesRef()
                sr.from_df(p_str.strip())
                self.products.append(sr)
        if 'modifiers' in r_dict:
            for m_str in r_dict['modifiers'].split(';'):
                msr = ModSpeciesRef()
                msr.from_df(m_str.strip())
                self.modifiers.append(msr)
        if 'kineticLaw' in r_dict:
            self.kinetic_law = KineticLaw()
            self.kinetic_law.from_df(r_dict)
        if 'fbcLowerFluxBound' in r_dict:
            self.fbc_enabled = True
            self.fbc_lb = r_dict['fbcLowerFluxBound']
        if 'fbcUpperFluxBound' in r_dict:
            self.fbc_enabled = True
            self.fbc_ub = r_dict['fbcUpperFluxBound']
        if 'fbcGeneProdAssoc' in r_dict:
            self.fbc_enabled = True
            self.fbc_gpa = FbcGeneProdAssociation()
            self.fbc_gpa.from_df(r_dict['fbcGeneProdAssoc'].strip())
        super().from_df(r_dict)


class SimpleSpeciesRef(SBase):

    def __init__(self):
        self.species = None
        super().__init__()

    def import_sbml(self, sbml_sr):
        self.species = sbml_sr.getSpecies()
        super().import_sbml(sbml_sr)

    def export_sbml(self, sbml_sr):
        sbml_sr.setSpecies(self.species)
        super().export_sbml(sbml_sr)

    def to_df(self):
        attr = []
        if self.id is not None:
            attr.append('id=' + self.id)
        if self.name is not None:
            attr.append('name=' + self.name)
        attr.append('species=' + self.species)
        if self.sboterm is not None:
            attr.append('sboterm=' + self.sboterm)
        return attr

    def from_df(self, sr_dict):
        if 'id' in sr_dict:
            self.id = sr_dict['id']
        if 'species' in sr_dict:
            self.species = sr_dict['species']
        if 'sboterm' in sr_dict:
            self.sboterm = sr_dict['sboterm']


class ReacSpeciesRef(SimpleSpeciesRef):

    def __init__(self):
        self.stoichiometry = None
        self.constant = None
        super().__init__()

    def import_sbml(self, sbml_sr):
        if sbml_sr.isSetStoichiometry():
            self.stoichiometry = sbml_sr.getStoichiometry()
        if sbml_sr.isSetConstant():
            self.constant = sbml_sr.getConstant()
        super().import_sbml(sbml_sr)

    def export_sbml(self, sbml_r):
        sbml_sr = sbml_r.createReactant()
        if self.stoichiometry is not None:
            sbml_sr.setStoichiometry(self.stoichiometry)
        if self.constant is not None:
            sbml_sr.setConstant(self.constant)
        super().export_sbml(sbml_sr)

    def to_df(self):
        attr = super().to_df()
        if self.stoichiometry is not None:
            attr.append('stoic=' + str(self.stoichiometry))
        if self.constant is not None:
            attr.append('const=' + str(self.constant))
        return ', '.join(attr)

    def from_df(self, sr_str):
        sr_dict = extract_params(sr_str)
        if 'stoic' in sr_dict:
            self.stoichiometry = float(sr_dict['stoic'])
        if 'const' in sr_dict:
            self.constant = get_bool_val(sr_dict['const'])
        super().from_df(sr_dict)


class ProdSpeciesRef(SimpleSpeciesRef):

    def __init__(self):
        self.stoichiometry = None
        self.constant = None
        super().__init__()

    def import_sbml(self, sbml_sr):
        if sbml_sr.isSetStoichiometry():
            self.stoichiometry = sbml_sr.getStoichiometry()
        if sbml_sr.isSetConstant():
            self.constant = sbml_sr.getConstant()
        super().import_sbml(sbml_sr)

    def export_sbml(self, sbml_r):
        sbml_sr = sbml_r.createProduct()
        if self.stoichiometry is not None:
            sbml_sr.setStoichiometry(self.stoichiometry)
        if self.constant is not None:
            sbml_sr.setConstant(self.constant)
        super().export_sbml(sbml_sr)

    def to_df(self):
        attr = super().to_df()
        if self.stoichiometry is not None:
            attr.append('stoic=' + str(self.stoichiometry))
        if self.constant is not None:
            attr.append('const=' + str(self.constant))
        return ', '.join(attr)

    def from_df(self, sr_str):
        sr_dict = extract_params(sr_str)
        if 'stoic' in sr_dict:
            self.stoichiometry = float(sr_dict['stoic'])
        if 'const' in sr_dict:
            self.constant = get_bool_val(sr_dict['const'])
        super().from_df(sr_dict)


class ModSpeciesRef(SimpleSpeciesRef):

    def __init__(self):
        super().__init__()

    def import_sbml(self, sbml_sr):
        super().import_sbml(sbml_sr)

    def export_sbml(self, sbml_r):
        sbml_sr = sbml_r.createModifier()
        super().export_sbml(sbml_sr)

    def to_df(self):
        return ', '.join(super().to_df())

    def from_df(self, msr_str):
        super().from_df(extract_params(msr_str))


class KineticLaw(SBase):

    def __init__(self):
        self.local_params = []
        self.math = None
        self.sboTerm = None
        super().__init__()

    def import_sbml(self, sbml_r):
        sbml_kl = sbml_r.getKineticLaw()
        self.math = libsbml.formulaToL3String(sbml_kl.getMath())
        if sbml_kl.getLevel() > 2:
            sbml_llp = sbml_kl.getListOfLocalParameters()
        else:
            sbml_llp = sbml_kl.getListOfParameters()
        for sbml_lp in sbml_llp:
            lp = LocalParameter()
            lp.import_sbml(sbml_lp)
            self.local_params.append(lp)
        super().import_sbml(sbml_kl)

    def export_sbml(self, sbml_r):
        sbml_kl = sbml_r.createKineticLaw()
        math = libsbml.parseL3Formula(self.math)
        if math:
            sbml_kl.setMath(math)
        else:
            print(libsbml.getLastParseL3Error())
            sys.exit()
        for lp in self.local_params:
            lp.export_sbml(sbml_kl)
        super().export_sbml(sbml_kl)

    def to_df(self):
        kl_dict = {'math': self.math}
        if len(self.local_params) > 0:
            kl_dict['localParams'] = '; '.join([lp.to_df() for lp in self.local_params])
        if self.sboterm is not None:
            kl_dict['sboTerm'] = self.sboterm
        return kl_dict

    def from_df(self, r_dict):
        self.math = r_dict['kineticLaw']
        if 'localParams' in r_dict:
            for lp_str in r_dict['localParams'].split(';'):
                lp = LocalParameter()
                lp.from_df(lp_str.strip())
                self.local_params.append(lp)
        if 'sboTerm' in r_dict:
            self.sboTerm = r_dict['sboTerm']


class LocalParameter(SBase):

    def __init__(self):
        self.value = None
        self.units = None
        super().__init__()

    def import_sbml(self, sbml_lp):
        if sbml_lp.isSetValue():
            self.value = sbml_lp.getValue()
        if sbml_lp.isSetUnits():
            self.units = sbml_lp.getUnits()
        super().import_sbml(sbml_lp)

    def export_sbml(self, sbml_kl):
        if sbml_kl.getLevel() > 2:
            sbml_lp = sbml_kl.createLocalParameter()
        else:
            sbml_lp = sbml_kl.createParameter()
        if self.value is not None:
            sbml_lp.setValue(self.value)
        if self.units is not None:
            sbml_lp.setUnits(self.units)
        super().export_sbml(sbml_lp)

    def to_df(self):
        attr = ['id=' + self.id]
        if self.name is not None:
            attr.append('name=' + self.name)
        if self.value is not None:
            attr.append('value=' + str(float(self.value)))
        if self.units is not None:
            attr.append('units=' + self.units)
        if self.sboterm is not None:
            attr.append('sboterm=' + self.sboterm)
        return ', '.join(attr)

    def from_df(self, lp_str):
        lp_dict = extract_params(lp_str)
        if 'id' in lp_dict:
            self.id = lp_dict['id']
        if 'name' in lp_dict:
            self.name = lp_dict['name']
        if 'value' in lp_dict:
            self.value = float(lp_dict['value'])
        if 'units' in lp_dict:
            self.units = lp_dict['units']
        if 'sboterm' in lp_dict:
            self.sboterm = lp_dict['sboterm']


class FbcGeneProdAssociation(SBase):

    def __init__(self):
        self.infix = None
        super().__init__()

    def import_sbml(self, sbml_r):
        sbml_gpa = sbml_r.getPlugin('fbc').getGeneProductAssociation()
        self.infix = sbml_gpa.getAssociation().toInfix(usingId=True)
        super().import_sbml(sbml_gpa)

    def export_sbml(self, sbml_r):
        fbc_rplugin = sbml_r.getPlugin('fbc')
        fbc_mplugin = sbml_r.getModel().getPlugin('fbc')
        sbml_gpa = libsbml.GeneProductAssociation(
                            fbc_rplugin.getLevel(),
                            fbc_rplugin.getVersion(),
                            fbc_rplugin.getPackageVersion())
        sbml_a = libsbml.FbcAssociation.parseFbcInfixAssociation(
                            self.infix,
                            fbc_mplugin,
                            usingId=True,
                            addMissingGP=False)
        sbml_gpa.setAssociation(sbml_a)
        fbc_rplugin.setGeneProductAssociation(sbml_gpa)

    def to_df(self):
        attr = []
        if self.id is not None:
            attr.append('id=' + self.id)
        if self.name is not None:
            attr.append('name=' + self.name)
        if self.sboterm is not None:
            attr.append('sboterm=' + self.sboterm)
        attr.append('assoc=' + self.infix)
        return ', '.join(attr)

    def from_df(self, gpa_str):
        gpa_dict = extract_params(gpa_str)
        if 'id' in gpa_dict:
            self.id = gpa_dict['id']
        if 'name' in gpa_dict:
            self.name = gpa_dict['name']
        if 'assoc' in gpa_dict:
            self.infix = gpa_dict['assoc']
        if 'sboterm' in gpa_dict:
            self.sboterm = gpa_dict['sboterm']
