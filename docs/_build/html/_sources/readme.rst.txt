
Tutorial
========

Example::

    import sbmlxdf

    input_xml = 'SBML_Models/e_coli_core.xml'

    model = sbmlxdf.Model()
    if model.import_sbml(input_xml):
        print('SBML model imported:', input_xml)
        model.to_excel('model.xlsx')
        print('SBML model written to Excel: model.xlsx')
        model.to_csv('model')
        print('also SBML model written to .csv: ./model/*.csv')

        # read model from Excel spreadsheet
        outm = sbmlxdf.Model('model.xlsx')
        print('SBML model imported from model.xlsx')
        is_valid_sbml = outm.validate_sbml('checkModel.xml')
        print('SBML file valid:', is_valid_sbml)

        model_dfs = outm.to_df()
        print('model exported to dict of pandas dataframes')
        print(model_dfs.keys())

        df_r = model_dfs['reactions']
        print(len(df_r), 'reactions found, first reaction:' )
        print(df_r.iloc[0])
        print('reactants and products for some reactions:')
        for id, reaction in df_r.head().iterrows():
            print('reaction:', id)
            for record in sbmlxdf.extract_records(reaction['reactants']):
                print('  reactant: ', sbmlxdf.extract_params(record))
            for record in sbmlxdf.extract_records(reaction['products']):
                print('  product:  ', sbmlxdf.extract_params(record))


Methods
-------
| create Model object, empty or from file
|   sbmlxdf.Model()
|   sbmlxdf.Model('model.xml')
|   sbmlxdf.Model('model.xlsx')
|   sbmlxdf.Model('model.ods')
|   sbmlxdf.Model('model_dir')
|
| read/write SBML file
|   sbmlxdf.Model.import_sbml('model.xml')
|   sbmlxdf.Model.export_sbml('model.xml')
|
| read/write Excel spreadsheet with model data
|  sbmlxdf.Model.from_excel('model.xlsx')
|  sbmlxdf.Model.to_excel('model.xlsx')
|
| read/write OpenOffice spreadsheet with model data
|  sbmlxdf.Model.from_excel('model.ods')
|  sbmlxdf.Model.to_excel('model.ods')
|
| read/write model coded in set of .csv files
|   sbmlxdf.Model.from_csv('model_dir')
|   sbmlxdf.Model.to_csv('model_dir')
|
| convert model data to/from dict of pandas dataframes
|   sbmlxdf.Model.to_df()
|   sbmlxdf.Model.from_df(model_dict)
|
| validate compliance with SBML specification (units check enabled/disabled)
|   sbmlxdf.Model.validate_sbml('tmp.xml', units_check=True)
|
| miscellanious - data extraction helper functions
|   sbmlxdf.misc.extract_params(record_str)
|     extract dict of parameters from record
|   sbmlxdf.misc.extract_records(lo_record_str)
|     extract record from a list of records
|   sbmlxdf.misc.extract_lo_records(lo_lo_records_str)
|     extract list of records from a list of list of records
|   sbmlxdf.misc.extract_xml_attrs(xml_annots, ns=None, token=None)
|     extract attributes from xml-annots str for given namespace and/or token


Workflow for creating SBML files:
---------------------------------
1. Create and Excel model. e.g. 'my_model.xlsx'

   You may start with an Excel model template, which you
   modify/configure to your needs. Excel model templates can be
   created by converting existing SBML models to Excel, e.g.
   using models from *./test/data directory

   ``model = sbmlxdf.Model('ReferenceSBMLmodel.xml')``

   ``model.to_excel('templateModel.xlsx')``

2. Import Excel coded model

   ``my_model = sbmlxdf.Model('my_model.xlsx')``

3. Validate compliance with SBML standard

   A compliance report \*.txt will be created in the *./results*
   directory, with detailed warning and error messages generated
   by libSBML validation. A corresponding \*.xml document can be
   used to cross reference the line numbers.

   ``my_model.validate_sbml('tmp.xml')``

4. Correct warnings/errors by updating your Excel coded model and go
back to step 2.

5. Upon successful validation create your SBML coded model

   ``my_model.export_sbml('my_model.xml')``
