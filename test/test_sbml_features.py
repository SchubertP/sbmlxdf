"""Test routines to check overall behaviour of sbmlxdf

Check handling of SBML configurations extracted from SBML specifications
and configured in SBML models 'test_SBML_L3V2_*.xml'

valdiation workflow:
SBML.xml -> (orig) -> tmp Excel.xlsx -> (xlsx) -> tmp SBML.xml -> (xml)

- SBML.xml models and Excel spreadsheet are file based
- (orig), (xlsx) and (xlm) are memory based
- memory based models are checked against corresponding pickel reference
- (xlsx) is also validated wrt SBML compliance, except for models with known
  warning messages.

- sample models can be used as reference to create excel spreadsheet templates

Execute in package directory:
$ pytest -v

Peter Schubert, Computational Cell Biology, HHU Duesseldorf, June 2021
"""
import pytest
import pandas as pd
import pickle
import os

import sbmlxdf

## pytest test/test_sbml_features.py -v

test_dir = os.path.dirname(__file__)
model_dir = os.path.join(test_dir, 'data')
pickel_dir = os.path.join(model_dir, 'pickel')

def check_vs_reference(model_dfs, ref_dfs):
    for df in ref_dfs:
        if type(ref_dfs[df]) == pd.DataFrame:
            pd.testing.assert_frame_equal(model_dfs[df], ref_dfs[df])
        if type(ref_dfs[df]) == pd.Series:
            pd.testing.assert_series_equal(model_dfs[df], ref_dfs[df])

@pytest.mark.parametrize('model_name', [
    'test_SBML_L3V2_empty_doc',
    'test_SBML_L3V2_unit_defs',
    'test_SBML_L3V2_compartments',
    'test_SBML_L3V2_species',
    'test_SBML_L3V2_initial_assignment',
    'test_SBML_L3V2_annotation',
    'test_SBML_L3V2_model_history',
    'test_SBML_L3V2_constraints',
    'test_SBML_L3V2_function_defs',
    'test_SBML_L3V2_boundaryCondition',
    'test_SBML_L3V2_discrete_stochastic_sim',
    'test_SBML_L3V2_simple_example',
    'test_SBML_L3V2_2D_compartments',
    'test_SBML_L3V2_multi_compartment',
    'test_SBML_L3V2_membrane_reaction',
    'test_SBML_L3V2_conversionFactor_1',
    'test_SBML_L3V2_conversionFactor_2',
    'test_SBML_L3V2_assignment_rule',
    'test_SBML_L3V2_algebraic_rule',
    'test_SBML_L3V2_events',
    'test_SBML_L3V2_delay',
    'test_SBML_L3V2_non-persistent_trigger',
    'test_SBML_L3V2_fbc',
    'test_SBML_L3V2_fbc_groups',
    'test_SBML_L3V2_distrib',
    'test_SBML_L3V2_distrib_warnings',
    'test_SBML_L3V2_xml_annotation',
    'test_SBML_L3V2_annotation_SHK',
    ])

def test_sbml_features(model_name, tmp_path):
    tmp_xlsx = os.path.join(tmp_path, 'tmp.xlsx')
    tmp_xml = os.path.join(tmp_path, 'tmp.xml')

    # reference data
    with open(os.path.join(pickel_dir, model_name + '.pickel'), 'rb') as f:
        ref_dfs = pickle.load(f)

    # import original SBML model
    orig_model = sbmlxdf.Model()
    model_path = os.path.join(model_dir, model_name + '.xml')
    assert orig_model.import_sbml(model_path) == True
    check_vs_reference(orig_model.to_df(), ref_dfs)

    # export to Excel
    orig_model.to_excel(tmp_xlsx)

    # import from Excel
    xlsx_model = sbmlxdf.Model(tmp_xlsx)
    check_vs_reference(xlsx_model.to_df(), ref_dfs)

    # validate the smbl imported
    if not model_name.endswith('_warnings'):
        assert xlsx_model.validate_sbml('tmp_val.xml') == {}

    # export to sbml
    xlsx_model.export_sbml(tmp_xml)

    # import again from sbml
    final_model = sbmlxdf.Model(tmp_xml)
    check_vs_reference(final_model.to_df(), ref_dfs)
