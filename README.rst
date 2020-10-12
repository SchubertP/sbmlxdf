Install:
========

$ pip install git+https://gitlab.cs.uni-duesseldorf.de/schubert/sbmlxdf




Convert between SBML coded files and Pandas DataFrames
======================================================

Example::

    import sbmlxdf

    input_xml = 'protein_translation_model-2020-09-08.xml'

    # import SBML model and export to Excel
    model = sbmlxdf.Model()
    model.import_sbml(input_xml)
    model.to_excel('model.xlsx')

    # read model from Excel and export, valdiate, export to SBML
    upd_model = sbmlxdf.Model()
    upd_model.from_excel('model.xlsx')
    print("is valid SBML (check also ./results): ", upd_model.validate_sbml('check_upd_model.xml'))
    upd_model.export_sbml('upd_model.xml')
    
    # access model data, including value-pair fields
    model_dfs = upd_model.to_df()
    reaction = r_df.iloc[2]
    print('reaction ID:', reaction.id, '   kinetic law:', reaction.kineticLaw )
    for record in reaction['reactants'].split(';'):
        record_dict = sbmlxdf.extract_vps(record)
        print(record_dict)


Peter Schubert, October 2020
