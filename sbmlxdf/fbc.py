"""Implementation of fbc ext. package components.

Peter Schubert, HHU Dusseldorf, October 2020
"""
import pandas as pd

from sbmlxdf.sbase import SBase
from sbmlxdf.misc import extract_params, get_bool_val


class FbcListOfObjectives(SBase):

    def __init__(self):
        self.objectives = []
        self.active = None
        super().__init__()

    def import_sbml(self, sbml_model):
        fbc_mplugin = sbml_model.getPlugin('fbc')
        sbml_lo = fbc_mplugin.getListOfObjectives()
        self.active = sbml_lo.getActiveObjective()
        for sbml_o in sbml_lo:
            o = FbcObjective()
            o.import_sbml(sbml_o)
            self.objectives.append(o)
        super().import_sbml(sbml_lo)

    def export_sbml(self, sbml_model):
        fbc_mplugin = sbml_model.getPlugin('fbc')
        for o in self.objectives:
            o.export_sbml(fbc_mplugin)
        sbml_lo = fbc_mplugin.getListOfObjectives()
        sbml_lo.setActiveObjective(self.active)
        super().export_sbml(sbml_lo)

    def to_df(self):
        df_obj = pd.DataFrame([o.to_df() for o in self.objectives])\
                              .set_index('id')
        df_obj.insert(1, 'active', df_obj.index == str(self.active))
        return df_obj

    def from_df(self, lo_df):
        for obj, active in lo_df['active'].iteritems():
            if get_bool_val(active):
                self.active = obj
                break
        for idx, o_s in lo_df.reset_index().iterrows():
            o = FbcObjective()
            o.from_df(o_s.dropna().to_dict())
            self.objectives.append(o)


class FbcObjective(SBase):
    # note: list_of_flux_objectives object not implemented

    def __init__(self):
        self.flux_objectives = []
        self.type = ''
        super().__init__()

    def import_sbml(self, sbml_o):
        self.type = sbml_o.getType()
        sbml_lfo = sbml_o.getListOfFluxObjectives()
        for sbml_fo in sbml_lfo:
            fo = FbcFluxObjective()
            fo.import_sbml(sbml_fo)
            self.flux_objectives.append(fo)
        super().import_sbml(sbml_o)

    def export_sbml(self, fbc_mplugin):
        sbml_o = fbc_mplugin.createObjective()
        sbml_o.setType(self.type)
        for fo in self.flux_objectives:
            fo.export_sbml(sbml_o)
        super().export_sbml(sbml_o)

    def to_df(self):
        o_dict = super().to_df()
        o_dict['type'] = self.type
        o_dict['fluxObjectives'] = '; '.join([fo.to_df()
                                              for fo in self.flux_objectives])
        return o_dict

    def from_df(self, o_dict):
        self.type = o_dict['type']
        for fo_str in o_dict['fluxObjectives'].split(';'):
            fo = FbcFluxObjective()
            fo.from_df(fo_str.strip())
            self.flux_objectives.append(fo)
        super().from_df(o_dict)


class FbcFluxObjective(SBase):

    def __init__(self):
        self.reaction = ''
        self.coefficient = float('nan')
        super().__init__()

    def import_sbml(self, sbml_fo):
        self.reaction = sbml_fo.getReaction()
        self.coefficient = sbml_fo.getCoefficient()
        super().import_sbml(sbml_fo)

    def export_sbml(self, sbml_o):
        sbml_fo = sbml_o.createFluxObjective()
        sbml_fo.setReaction(self.reaction)
        sbml_fo.setCoefficient(self.coefficient)
        super().export_sbml(sbml_fo)

    def to_df(self):
        attr = []
        if self.id is not None:
            attr.append('id=' + self.id)
        if self.name is not None:
            attr.append('name=' + self.name)
        attr.append('reac=' + self.reaction)
        attr.append('coef=' + str(self.coefficient))
        if self.sboterm is not None:
            attr.append('sboterm=' + self.sboterm)
        return ', '.join(attr)

    def from_df(self, fo_str):
        fo_dict = extract_params(fo_str)
        if 'reac' in fo_dict:
            self.reaction = fo_dict['reac']
        if 'coef' in fo_dict:
            self.coefficient = float(fo_dict['coef'])
        super().from_df(fo_dict)


class FbcListOfGeneProducts(SBase):

    def __init__(self):
        self.gene_products = []
        super().__init__()

    def import_sbml(self, sbml_model):
        fbc_mplugin = sbml_model.getPlugin('fbc')
        sbml_lgp = fbc_mplugin.getListOfGeneProducts()
        for sbml_gp in sbml_lgp:
            gp = FbcGeneProduct()
            gp.import_sbml(sbml_gp)
            self.gene_products.append(gp)
        super().import_sbml(sbml_lgp)

    def export_sbml(self, sbml_model):
        fbc_mplugin = sbml_model.getPlugin('fbc')
        for gp in self.gene_products:
            gp.export_sbml(fbc_mplugin)
        sbml_lgp = fbc_mplugin.getListOfGeneProducts()
        super().export_sbml(sbml_lgp)

    def to_df(self):
        return pd.DataFrame([gp.to_df() for gp in self.gene_products])\
                           .set_index('id')

    def from_df(self, lgp_df):
        for idx, gp_s in lgp_df.reset_index().iterrows():
            gp = FbcGeneProduct()
            gp.from_df(gp_s.dropna().to_dict())
            self.gene_products.append(gp)


class FbcGeneProduct(SBase):

    def __init__(self):
        self.label = ''
        self.associated = None
        super().__init__()

    def import_sbml(self, sbml_gp):
        self.label = sbml_gp.getLabel()
        if sbml_gp.isSetAssociatedSpecies():
            self.associated = sbml_gp.getAssociatedSpecies()
        super().import_sbml(sbml_gp)

    def export_sbml(self, fbc_mplugin):
        sbml_gp = fbc_mplugin.createGeneProduct()
        sbml_gp.setLabel(self.label)
        if self.associated is not None:
            sbml_gp.setAssociatedSpecies(self.associated)
        super().export_sbml(sbml_gp)

    def to_df(self):
        gp_dict = super().to_df()
        gp_dict['label'] = self.label
        if self.associated is not None:
            gp_dict['associatedSpec'] = self.associated
        return gp_dict

    def from_df(self, gp_dict):
        self.label = gp_dict['label']
        if 'associatedSpec' in gp_dict:
            self.associated = gp_dict['associatedSpec']
        super().from_df(gp_dict)
