Install:
========

$ python3 -m pip install git+https://gitlab.cs.uni-duesseldorf.de/schubert/sbmlxdf

or, for access to sample SBML files in /test/data/

$ git clone https://gitlab.cs.uni-duesseldorf.de/schubert/sbmlxdf


Convert between SBML coded files and Pandas DataFrames
======================================================

sbmlxdf supports, with few exceptions, all functionality of
**SBML L3V2 core** package and extension packages **Flux Balance
Constraints (fbc)**, **Groups (groups)** and **Distributions
(distrib)**.


using **libSBML API** for accessing SBML.

Bornstein, B. J., Keating, S. M., Jouraku, A., and Hucka M. (2008)
LibSBML: An API Library for SBML. Bioinformatics, 24(6):880–881,
doi:10.1093/bioinformatics/btn051.

Note: **python-libsbml-experimental** package is used to support features in
distrib package. It is imported with ``import libsbml``. If python-libsbml
package is installed subsequently, e.g. as requirement for another tool,
some functionality might get lost. In such case python-libsbml-experimental
should be re-installed using pip install.


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
        print('model exported to dict of Pandas dataframes')
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


Workflow for creating SBML files:
---------------------------------
1. Create and Excel model. e.g. 'mymodel.xlsx'

   You may start with an Excel model template, which you
   modify/configure to your needs. Excel model templates can be
   created by converting existing SBML models to Excel, e.g.
   using models from *./test/data/* directory

   ``model = sbmlxdf.Model('ReferenceSBMLmodel.xml')``

   ``model.to_excel('templateModel.xlsx')``

2. Import Excel model

   ``mymodel = sbmlxdf.Model('mymodel.xlsx')``

3. Validate compliance with SBML standard

   A compliance report \*.txt will be created in the *./results*
   directory, with detailed warning and error messages generated
   by libSBML validation. A corresponding \*.xlm document can be
   used to cross reference the line numbers.

   ``mymodel.validate_sbml('tmp.xml')``

4. Correct warnings/errors by updating your Excel model and go
back to step 2.

5. Upon successful validation write out your SBML model

   ``mymodel.export_sbml('mySBMLmodel.xml')``


Peter Schubert, October 2020
