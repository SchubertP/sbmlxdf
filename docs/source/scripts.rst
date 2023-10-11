Command Line Scripts
====================

Two very basic command line scripts can support conversion between
SBML coded models and the tabular format.

Supported spreadsheet formats are MS Excel (\*.xlsx) and OpenOffice (\*.ods).
These spreadsheet documents contain sheets for SBML components.
Comma-separated-value files (\*.csv) are supported as well, one file for
each SBML component.

In case you are not a Python programmer, ask a colleague to set up Python 3
on your system, install sbmlxdf, create the two Python scripts given below
and show you how these command line scripts can be used.

.. note::

   Only sheets / csv-files for SBML components used in your model
   design are required. Same holds for column names in tables.

   Names of sheets / csv-file are significant. Your spreadsheet may
   contain additional sheets not recognized by smblxdf. Such sheets may be
   of help when creating/modifying models.

.. tip::

   Use version control when modifying models. Once your model has passed
   validation, generate the SBML file and commit the SBML file
   to your repository.


SBML -> Excel
-------------

This command line script takes as input an SMBL model
and converts it to the corresponding spreadsheet document.

This could be your first step in creating a spreadsheet template from
an existing SBML model.

Example (assuming the SBML model ``other_model.xml`` in
directory ``./SBML_models``):

.. code-block:: bash

  $ python3 sbml2xlsx.py SBML_models/other_model.xml
  spreadsheet created: SBML_models/other_model.xlsx

Python code for script ``sbml2xlsx.py``:

.. code-block:: python

    # sbml2xlsx.py
    import sys
    import os.path
    import sbmlxdf

    # basic command line argument handling
    if len(sys.argv) == 2:
        sbml_in = sys.argv[1]
        xlsx_out = sbml_in.replace('.xml', '.xlsx')
    else:
        print('use:', os.path.basename(sys.argv[0]), 'sbml_file')
        sys.exit()

    model = sbmlxdf.Model(sbml_in)
    model.to_excel(xlsx_out)
    print('spreadsheet created:', xlsx_out)


Excel -> SBML
-------------

This command line script takes as input a spreadsheet document and
converts it to the corresponding SBML model.

It is a two-step process:

- First, the model is checked against SBML standards, using libsbml
  functionality.
  In case validation passes, the SBML model is created (2nd step).

- In case the validation fails, SBML warnings and/or errors messages
  are printed to the console. The SBML model is not created.

  It is your task to first correct the warnings/errors in your spreadsheet
  document and re-run the conversion script.
  Warning and error messages give
  an indication what needs to be corrected.
  Warning and error messages are stored in the text file
  ``./results/tmp.txt``. (Line numbers refer to xml file ``./results/tmp.xml``)

.. note::

    While not recommended, you could run the script with the
    optional parameter ``-f`` to force creation of the
    SBML model despite warning messages.
    (Error messages require correction in any case.)

Example (assuming a spreadsheet document ``my_model.xlsx`` in
directory ``./SBML_models``):

.. code-block:: bash

  $ python3 xlsx2sbml.py SBML_models/my_model.xlsx
  Validation result: {'Errors': 2}
  Please correct spreadsheet and re-run converter

  {'Errors': 2} NOK: not SBML compliant, see results file!
  line 752: (21111 [Error]) The value of a <speciesReference> 'species'
  attribute must be the identifier of an existing <species> in the model.
  Reference: L3V2 Section 4.11.3
   The <speciesReference> in the <reaction> with id 'mr_t8'
   references species 'L', which is undefined.

  line 778: (21111 [Error]) The value of a <speciesReference> 'species'
  attribute must be the identifier of an existing <species> in the model.
  Reference: L3V2 Section 4.11.3
   The <speciesReference> in the <reaction> with id 'mr_e9'
   references species 'L', which is undefined.

During validation two errors were detected. The SBML file is not created.
The error messages indicate that species ``L`` is used in two reactions,
however species ``L`` is not yet defined.

Add species ``L`` to your spreadsheet document (sheet ``species``) and
run the converter again.

.. code-block:: bash

   $ python3 xlsx2sbml.py SBML_models/my_model.xlsx
   Validation result: {}
   SBML model created: SBML_models/my_model.xml

This time validation was successful and the SBML model was created.


Python code for script ``sbml2xlsx.py``:

.. code-block:: python

    # xslx2sbml.py
    import sys
    import os.path
    import sbmlxdf

    # basic command line argument handling
    if len(sys.argv) > 1:
       excel_in = sys.argv[1]
       sbml_out = excel_in.replace('.xlsx', '.xml')
    else:
       print('use:', os.path.basename(sys.argv[0]), 'xlsx_file [-f]')
       print('     -f: forced; write SBML despite warnings')
       sys.exit()
    forced = (len(sys.argv) > 2) and (sys.argv[2] == '-f')

    # read in excel file
    model = sbmlxdf.Model(excel_in)
    # check compliance with SBML specification
    val_result = model.validate_sbml('tmp.xml')
    print('validation result:', val_result)
    if ((len(val_result) == 0) or
       (forced and ('Errors' not in val_result.keys()))):
       model.export_sbml(sbml_out)
       print('SBML model created:', sbml_out)
    else:
       print('correct spreadsheet and run converter again\n')
       print(open(os.path.join('.', 'results', 'tmp.txt'), 'r').read())
