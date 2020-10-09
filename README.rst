Convert between SBML coded files and Pandas DataFrames
======================================================

Example:

import sbmlxdf

model = sbmlxdf.Model()
model.import_sbml('orig_model.xml')
model.validate_sbml('orig_model.xml')
model.to_excel('model.xlsx')
#model.to_csv('model')

# modify, update model using MS Excel

upd_model=sbmlxdf.Model()
upd_model.from_excel('model.xlsx')
upd_model.export_sbml('upd_model.xml')
#upd_dict = upd_model.to_df()

Peter Schubert, October 2020
