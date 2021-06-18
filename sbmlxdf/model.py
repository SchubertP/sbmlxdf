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

# directory where to write result files of validate_sbml()
results_dir = 'results'

IS_SERIES = 1
IS_DF_INDEXED = 2
IS_DF_NOTINDEXED = 3
_sheets = {
    'sbml': IS_SERIES, 'modelAttrs': IS_SERIES, 'funcDefs': IS_DF_INDEXED,
    'unitDefs' : IS_DF_INDEXED, 'compartments' : IS_DF_INDEXED,
    'species': IS_DF_INDEXED, 'parameters': IS_DF_INDEXED,
    'initAssign': IS_DF_INDEXED, 'rules': IS_DF_NOTINDEXED,
    'constraints': IS_DF_NOTINDEXED, 'reactions': IS_DF_INDEXED,
    'events': IS_DF_NOTINDEXED, 'fbcObjectives': IS_DF_INDEXED,
    'fbcGeneProducts': IS_DF_INDEXED, 'groups': IS_DF_NOTINDEXED
    }

_lists_of = {
    'modelAttrs': [libsbml.Model.hasRequiredElements, ModelAttrs],
    'funcDefs': [libsbml.Model.getNumFunctionDefinitions, ListOfFunctionDefs],
    'unitDefs': [libsbml.Model.getNumUnitDefinitions, ListOfUnitDefs],
    'compartments': [libsbml.Model.getNumCompartments, ListOfCompartments],
    'species': [libsbml.Model.getNumSpecies, ListOfSpecies],
    'parameters': [libsbml.Model.getNumParameters, ListOfParameters],
    'initAssign': [libsbml.Model.getNumInitialAssignments, ListOfInitAssign],
    'rules': [libsbml.Model.getNumRules, ListOfRules],
    'constraints': [libsbml.Model.getNumConstraints, ListOfConstraints],
    'reactions': [libsbml.Model.getNumReactions, ListOfReactions],
    'events': [libsbml.Model.getNumEvents, ListOfEvents],
    'fbcObjectives': [libsbml.FbcModelPlugin.getNumObjectives,
                      FbcListOfObjectives],
    'fbcGeneProducts': [libsbml.FbcModelPlugin.getNumGeneProducts,
                        FbcListOfGeneProducts],
    'groups': [None, GroupsListOfGroups],
    }


class SbmlFileError(Exception):
    """Terminate on SBML read file Error."""
    pass


class Model(SBase):
    """Main Model class to represent the SBML model.

    Methods
    -------
        __init__() : constructor, empty model or from file (e.g. SBML, Excel)

        import_sbml() : import model from sbml-file
        validate_sbml() : validate model against SBML specification
        export_sbml() : export model to sbml-file

        to_df() : export model to dict of Pandas dataframes
        from_df() : import model from dict of Pandas dataframes

        to_excel() : export model to Excel or OpenOffice spreadsheet
        from_excel() : import model from Excel or OpenOffice spreadsheet

        to_csv() : export model to a set of .csv files
        from_csv : import model from a directory with a set of .csv files

        get_s_matrix() : retrieve stoichiometric matrix of the model.
    """

    def __init__(self, import_file=None):
        """Constructor.

        Parameters
        ----------
        import_file : str (optional)
            During instantiation, model can be imported from file.
            can be valid sbml file (.xml), Excel spreadsheet (.xlsx),
            OpenOffice spreadsheet (.ods) or directory holding .csv files.

        """
        self.isModel = False
        self.list_of = {}
        super().__init__()
        if type(import_file) == str:
            if import_file.endswith('.xml'):
                self.import_sbml(import_file)
            elif (import_file.endswith('.xlsx') or
                  import_file.endswith('.ods')):
                self.from_excel(import_file)
            elif os.path.exists(import_file):
                self.from_csv(import_file)

    def import_sbml(self, sbml_filename):
        if not os.path.exists(sbml_filename):
            print('SBML file not found: ' + sbml_filename)
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
        for k, v in _lists_of.items():
            sbml_func, assigned_class = v
            if k.startswith('fbc'):
                if sbml_model.isPackageEnabled('fbc'):
                    fbc_mplugin = sbml_model.getPlugin('fbc')
                    if sbml_func(fbc_mplugin):
                        self.list_of[k] = assigned_class()
            elif k == 'groups':
                if sbml_model.isPackageEnabled('groups'):
                    self.list_of[k] = assigned_class()
            else:
                if sbml_func(sbml_model):
                      self.list_of[k] = assigned_class()

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

    def get_s_matrix(self, sparse=False):
        """Retrieve stoichiometric matrix of the modell.

        requires both species and reactions to be defined

        Parameters
        ----------
            sparse : boolen (optional, default=False)
                specify if S-matrix should be returned in sparse format (True)

        Returns
        -------
            Pandas DataFrame
                stoichiometric matrix normal or in sparse format (sparse=True)

        """
        if ('species' in self.list_of) and ('reactions' in self.list_of):
            df_species = self.list_of['species'].to_df()
            df_reactions = self.list_of['reactions'].to_df()

            df_S = pd.DataFrame(np.zeros((len(df_species), len(df_reactions))),
                                index=df_species.index.values,
                                columns=df_reactions.index.values)
            for idx, r in df_reactions.iterrows():
                if type(r['reactants']) == str:
                  for reac in r['reactants'].split(';'):
                    s_d = extract_params(reac)
                    df_S.at[s_d['species'], idx] -= float(s_d.get('stoic', 1.0))
                if type(r['products']) == str:
                  for prod in r['products'].split(';'):
                    s_d = extract_params(prod)
                    df_S.at[s_d['species'], idx] += float(s_d.get('stoic', 1.0))
        else:
            df_S = pd.DataFrame(np.zeros((0,0)))

        if sparse==True:
            return df_S.astype(pd.SparseDtype('float', 0.0))
        else:
            return df_S

    def to_df(self):
        model_dict = {'sbml': self.sbml_container.to_df() }
        for key, lo in self.list_of.items():
            model_dict[key] = lo.to_df()
        if ('reactions' in model_dict) and ('parameters' in model_dict):
            if 'fbcLowerFluxBound' in model_dict['reactions'].columns:
                params = model_dict['parameters']['value'].to_dict()
                model_dict['reactions']['fbcLb'] = \
                  model_dict['reactions']['fbcLowerFluxBound'].replace(params)
                model_dict['reactions']['fbcUb'] = \
                  model_dict['reactions']['fbcUpperFluxBound'].replace(params)
        return model_dict

    def from_df(self, model_dict):
        if ('sbml' not in model_dict) or ('modelAttrs' not in model_dict):
            print('no valid model dict; sbml and modelAttrs required!')
            return False
        self.sbml_container = SbmlContainer()
        self.sbml_container.from_df(model_dict['sbml'])
        self.isModel = True
        for k, v in _lists_of.items():
            assigned_class = v[1]
            if k in model_dict:
                self.list_of[k] = assigned_class()
        try:
            for component, lo in self.list_of.items():
                lo.from_df(model_dict[component])
        except KeyError as err:
            print('KeyError: {0} in {1} while processing {2}'
                  .format(err, __name__, component))
            return False
        return True

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
        if not os.path.exists(file_name):
            print('Excel document not found: ' + file_name)
            return False
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
                    df_raw = pd.read_excel(xlsx, **params)
                    m_dict[sheet] = df_raw.loc[df_raw.index.dropna()]
        return self.from_df(m_dict)

    def to_csv(self, dir_name):
        """ create and check directory, remove existing *.csv files """
        if os.path.exists(dir_name):
            for csv_file in glob.glob(os.path.join(dir_name, '*.csv')):
                try:
                    os.remove(csv_file)
                except:
                    print("Error while deleting *.csv file : ", csv_file)
        else:
            os.mkdir(dir_name)
        for sheet, component in self.to_df().items():
            params = {'path_or_buf': os.path.join(dir_name, sheet + '.csv')}
            if _sheets[sheet] == IS_SERIES:
                params['header'] = False
            if _sheets[sheet] == IS_DF_NOTINDEXED:
                params['index'] = False
            component.to_csv(**params)

    def from_csv(self, dir_name):
        if not os.path.exists(dir_name):
            print('csv directory not found: ' + dir_name)
            return False
        m_dict = {}
        for csv_file in glob.glob(os.path.join(dir_name, '*.csv')):
            sheet = os.path.basename(csv_file).replace('.csv', '')
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
