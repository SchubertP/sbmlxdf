sbmlxdf Methods
===============


Create Model object
-------------------

.. autoclass:: sbmlxdf.Model
   :members: __init__

Model import/exports
--------------------

**Interface SBML models**

.. automethod:: sbmlxdf.Model.import_sbml
.. automethod:: sbmlxdf.Model.export_sbml

**Interface spreadsheet documents**

.. automethod:: sbmlxdf.Model.from_excel
.. automethod:: sbmlxdf.Model.to_excel

**Interface .csv files**

.. automethod:: sbmlxdf.Model.from_csv
.. automethod:: sbmlxdf.Model.to_csv

**Interface with pandas dataframes**

.. automethod:: sbmlxdf.Model.from_df
.. automethod:: sbmlxdf.Model.to_df


Model validation
----------------

**Validate compliance with SBML specification**

.. automethod:: sbmlxdf.Model.validate_sbml

Miscellaneous
-------------

**Data extraction helper functions**

.. automethod:: sbmlxdf.Model.get_s_matrix
.. autofunction:: sbmlxdf.misc.record_generator
.. autofunction:: sbmlxdf.misc.extract_params
.. autofunction:: sbmlxdf.misc.extract_xml_attrs
.. autofunction:: sbmlxdf.misc.mathml2numpy
