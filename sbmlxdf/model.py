"""Implementation of Main Model.

Peter Schubert, HHU Duesseldorf, October 2020
"""
import sys
import os
import os.path
import glob
import numpy as np
import pandas as pd

import libsbml

from sbmlxdf.compartments import ListOfCompartments
from sbmlxdf.constraints import ListOfConstraints
from sbmlxdf.events import ListOfEvents
from sbmlxdf.fbc import FbcListOfObjectives, FbcListOfGeneProducts
from sbmlxdf.function_defs import ListOfFunctionDefs
from sbmlxdf.groups import GroupsListOfGroups
from sbmlxdf.init_assign import ListOfInitAssign
from sbmlxdf.model_attrs import ModelAttrs
from sbmlxdf.parameters import ListOfParameters
from sbmlxdf.reactions import ListOfReactions
from sbmlxdf.rules import ListOfRules
from sbmlxdf.sbase import SBase
from sbmlxdf.sbml_container import SbmlContainer
from sbmlxdf.species import ListOfSpecies
from sbmlxdf.unit_defs import ListOfUnitDefs
from sbmlxdf.misc import extract_params
from sbmlxdf._version import __version__, program_name

results_dir = 'results'

IS_SERIES = 1
IS_DF_INDEXED = 2
IS_DF_NOTINDEXED = 3
_sheets = {'sbml': IS_SERIES, 'modelAttrs': IS_SERIES,
           'funcDefs': IS_DF_INDEXED , 'unitDefs' : IS_DF_INDEXED,
           'compartments' : IS_DF_INDEXED, 'species': IS_DF_INDEXED,
           'parameters': IS_DF_INDEXED, 'initAssign': IS_DF_INDEXED,
           'reactions': IS_DF_INDEXED, 'S_info' : IS_DF_INDEXED,
           'fbcObjectives': IS_DF_INDEXED, 'fbcGeneProducts': IS_DF_INDEXED,
           'rules': IS_DF_NOTINDEXED, 'constraints': IS_DF_NOTINDEXED,
           'events': IS_DF_NOTINDEXED, 'groups': IS_DF_NOTINDEXED}

class SbmlFileError(Exception):
    """Terminate on SBML read file Error."""
    pass


class Model(SBase):

    def __init__(self):
        self.isModel = False
        self.list_of = {}
        super().__init__()

    def import_sbml(self, sbml_filename):
        if not os.path.exists(sbml_filename):
            print("SBML file not found: " + sbml_filename)
            return False
        try:
            self.in_sbml = sbml_filename
            reader = libsbml.SBMLReader()
            sbml_doc = reader.readSBML(sbml_filename)
            errors = sbml_doc.getNumErrors()
            if errors > 0:
                print(sbml_doc.getErrorLog().toString())
                error_log = sbml_doc.getErrorLog()
                for i in range(errors):
                    e = error_log.getError(i)
                    if e.getErrorId() >= libsbml.LIBSBML_SEV_ERROR:
                        raise SbmlFileError(e.getShortMessage())
            self.sbml_container = SbmlContainer()
            self.sbml_container.import_sbml(sbml_doc)
            if sbml_doc.isSetModel():
                self.isModel = True
                sbml_model = sbml_doc.getModel()
                self._import_components(sbml_model)
                return True
        except:
            print('Exception occured:', sys.exc_info()[1])
            return False

    def _import_components(self, sbml_model):
        self.list_of['modelAttrs'] = ModelAttrs()
        if sbml_model.getNumFunctionDefinitions():
            self.list_of['funcDefs'] = ListOfFunctionDefs()
        if sbml_model.getNumUnitDefinitions():
            self.list_of['unitDefs'] = ListOfUnitDefs()
        if sbml_model.getNumCompartments():
            self.list_of['compartments'] = ListOfCompartments()
        if sbml_model.getNumSpecies():
            self.list_of['species'] = ListOfSpecies()
        if sbml_model.getNumParameters():
            self.list_of['parameters'] = ListOfParameters()
        if sbml_model.getNumInitialAssignments():
            self.list_of['initAssign'] = ListOfInitAssign()
        if sbml_model.getNumRules():
            self.list_of['rules'] = ListOfRules()
        if sbml_model.getNumConstraints():
            self.list_of['constraints'] = ListOfConstraints()
        if sbml_model.getNumReactions():
            self.list_of['reactions'] = ListOfReactions()
        if sbml_model.getNumEvents():
            self.list_of['events'] = ListOfEvents()
        if sbml_model.isPackageEnabled('fbc'):
            fbc_mplugin = sbml_model.getPlugin('fbc')
            if fbc_mplugin.getNumObjectives():
                self.list_of['fbcObjectives'] = FbcListOfObjectives()
            if fbc_mplugin.getNumGeneProducts():
                self.list_of['fbcGeneProducts'] = FbcListOfGeneProducts()
        if sbml_model.isPackageEnabled('groups'):
            self.list_of['groups'] = GroupsListOfGroups()
        for lo in self.list_of.values():
            lo.import_sbml(sbml_model)

    def validate_sbml(self, sbml_filename, units_check=True):
        sbml_compliance = False
        if not os.path.exists(results_dir):
            os.makedirs(results_dir)
        basename = os.path.basename(sbml_filename).split('.')[0]
        xml_file = os.path.join('results', basename + '.xml')
        result_file = os.path.join('results', basename + '.txt')
        if hasattr(self, 'sbml_container'):
            self.export_sbml(xml_file)
            reader = libsbml.SBMLReader()
            sbml_doc = libsbml.readSBML(xml_file)
            sbml_doc.getErrorLog().clearLog()
            if not units_check:
                sbml_doc.setConsistencyChecks(
                    libsbml.LIBSBML_CAT_IDENTIFIER_CONSISTENCY, False)
            sbml_doc.setConsistencyChecks(
                    libsbml.LIBSBML_CAT_MODELING_PRACTICE, False)
            sbml_doc.checkConsistency()
            err_tot = {}
            num_errors = sbml_doc.getNumErrors()
            for i in range(num_errors):
                e = sbml_doc.getError(i)
                if e.isInfo():
                    err_tot['Infos'] = err_tot.get('Infos', 0) + 1
                if e.isWarning():
                    err_tot['Warnings'] = err_tot.get('Warnings', 0) + 1
                if e.isError():
                    err_tot['Errors'] = err_tot.get('Errors', 0) + 1
                if e.isFatal():
                    err_tot['Fatals'] = err_tot.get('Fatals', 0) + 1
            with open(result_file, 'w') as f:
                f.write(str(err_tot))
                if ('Errors' in err_tot ) or ('Fatals' in err_tot):
                    f.write(' NOK: not SBML compliant, see results file!\n')
                else:
                    f.write(' OK: SBML compliant\n')
                if not units_check:
                    f.write('Units not checked\n')
                f.write(sbml_doc.getErrorLog().toString())
            return err_tot

    def export_sbml(self, sbml_filename):
        if hasattr(self, 'sbml_container'):
            sbml_doc = self.sbml_container.create_sbml_doc()
            if self.isModel:
                sbml_model = sbml_doc.createModel()
                for lo in self.list_of.values():
                    lo.export_sbml(sbml_model)
            writer = libsbml.SBMLWriter()
            writer.setProgramName(program_name)
            writer.setProgramVersion(__version__)
            writer.writeSBML(sbml_doc, sbml_filename)

    def _get_stoich_matrix(self, df_species, df_reactions, sparse=False):
        df_N = pd.DataFrame(np.zeros((len(df_species), len(df_reactions))),
                            index=df_species.index.values,
                            columns=df_reactions.index.values)
        for idx, r in df_reactions.iterrows():
            if type(r['reactants']) == str:
              for reac in r["reactants"].split(';'):
                reac_dict = extract_params(reac)
                df_N.at[reac_dict['species'], idx] -= float(reac_dict["stoic"])
            if type(r['products']) == str:
              for prod in r["products"].split(';'):
                prod_dict = extract_params(prod)
                df_N.at[prod_dict['species'], idx] += float(prod_dict["stoic"])
        if sparse:
            return df_N.astype(pd.SparseDtype("float", 0.0))
        else:
            return df_N

    def to_df(self):
        model_dict = {'sbml': self.sbml_container.to_df() }
        for key, lo in self.list_of.items():
            model_dict[key] = lo.to_df()
        if 'species' in model_dict and 'reactions' in model_dict:
            model_dict['S_info'] = self._get_stoich_matrix(
                model_dict['species'], model_dict['reactions'])
        return model_dict

    def from_df(self, model_dict):
        if ('sbml' not in model_dict) or ('modelAttrs' not in model_dict):
            print('no valid model dict; sbml and modelAttrs required!')
            return
        self.sbml_container = SbmlContainer()
        self.sbml_container.from_df(model_dict['sbml'])
        self.isModel = True
        self.list_of['modelAttrs'] = ModelAttrs()
        if 'funcDefs' in model_dict:
            self.list_of['funcDefs'] = ListOfFunctionDefs()
        if 'unitDefs' in model_dict:
            self.list_of['unitDefs'] = ListOfUnitDefs()
        if 'compartments' in model_dict:
            self.list_of['compartments'] = ListOfCompartments()
        if 'species' in model_dict:
            self.list_of['species'] = ListOfSpecies()
        if 'parameters' in model_dict:
            self.list_of['parameters'] = ListOfParameters()
        if 'initAssign' in model_dict:
            self.list_of['initAssign'] = ListOfInitAssign()
        if 'rules' in model_dict:
            self.list_of['rules'] = ListOfRules()
        if 'constraints' in model_dict:
            self.list_of['constraints'] = ListOfConstraints()
        if 'reactions' in model_dict:
            self.list_of['reactions'] = ListOfReactions()
        if 'events' in model_dict:
            self.list_of['events'] = ListOfEvents()
        if 'fbcObjectives' in model_dict:
            self.list_of['fbcObjectives'] = FbcListOfObjectives()
        if 'fbcGeneProducts' in model_dict:
            self.list_of['fbcGeneProducts'] = FbcListOfGeneProducts()
        if 'groups' in model_dict:
            self.list_of['groups'] = GroupsListOfGroups()
        try:
            for component, lo in self.list_of.items():
                lo.from_df(model_dict[component])
        except KeyError as err:
            print("KeyError: {0} in {1} while processing {2}"
                  .format(err, __name__, component))
            return -1
        return 0

    def to_excel(self, file_name):
        with pd.ExcelWriter(file_name) as writer:
            for sheet, component in self.to_df().items():
                params = {'sheet_name': sheet}
                if _sheets[sheet] == IS_SERIES:
                    params['header'] = False
                if _sheets[sheet] == IS_DF_NOTINDEXED:
                    params['index'] = False
                component.to_excel(writer, **params)

    def from_excel(self, file_name):
        m_dict = {}
        with pd.ExcelFile(file_name) as xlsx:
            for sheet in xlsx.sheet_names:
                if sheet in _sheets:
                    params = {'sheet_name': sheet, 'dtype': str}
                    if _sheets[sheet] == IS_SERIES:
                        params['header'] = None
                        params['index_col'] = 0
                        params['squeeze'] = True
                    if _sheets[sheet] == IS_DF_INDEXED:
                        params['index_col'] = 0
                    m_dict[sheet] = pd.read_excel(xlsx, **params)
        return self.from_df(m_dict)

    def to_csv(self, dir_name):
        """ create and check directory, remove existing *.csv files """
        if os.path.exists(dir_name):
            for csv_file in glob.glob(os.path.join(dir_name, "*.csv")):
                try:
                    os.remove(csv_file)
                except:
                    print("Error while deleting *.csv file : ", csv_file)
        else:
            os.mkdir(dir_name)
        for sheet, component in self.to_df().items():
            params = {'path_or_buf': os.path.join(dir_name, sheet+'.csv')}
            if _sheets[sheet] == IS_SERIES:
                params['header'] = False
            if _sheets[sheet] == IS_DF_NOTINDEXED:
                params['index'] = False
            component.to_csv(**params)

    def from_csv(self, dir_name):
        m_dict = {}
        if os.path.exists(dir_name):
            for csv_file in glob.glob(os.path.join(dir_name, "*.csv")):
                sheet = os.path.basename(csv_file).replace('.csv','')
                if sheet in _sheets:
                    params = {'dtype': str}
                    if _sheets[sheet] == IS_SERIES:
                        params['header'] = None
                        params['index_col'] = 0
                        params['squeeze'] = True
                    if _sheets[sheet] == IS_DF_INDEXED:
                        params['index_col'] = 0
                    m_dict[sheet] = pd.read_csv(csv_file, **params)
        return self.from_df(m_dict)
