sbmlxdf Methods
===============


Create Model object:
--------------------

.. autoclass:: sbmlxdf.Model
   :members: __init__

Model import/exports
--------------------

**Interface SBML models:**

.. autofunction:: sbmlxdf.Model.import_sbml
.. autofunction:: sbmlxdf.Model.export_sbml

**Interface spreadsheet documents:**

.. autofunction:: sbmlxdf.Model.from_excel
.. autofunction:: sbmlxdf.Model.to_excel

**Interface .csv files:**

.. autofunction:: sbmlxdf.Model.from_csv
.. autofunction:: sbmlxdf.Model.to_csv

**Interface with pandas dataframes:**

.. autofunction:: sbmlxdf.Model.from_df
.. autofunction:: sbmlxdf.Model.to_df


Model validation
----------------

**Validate compliance with SBML specification:**

.. autofunction:: sbmlxdf.Model.validate_sbml

Miscellanious
-------------

**Data extraction helper functions.**

.. autofunction:: sbmlxdf.Model.get_s_matrix
.. autofunction:: sbmlxdf.misc.extract_xml_attrs
.. autofunction:: sbmlxdf.misc.extract_params
.. autofunction:: sbmlxdf.misc.extract_records
.. autofunction:: sbmlxdf.misc.extract_lo_records
.. autofunction:: sbmlxdf.misc.mathml2numpy
