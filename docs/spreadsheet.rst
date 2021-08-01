Spreadsheet
===========

This section describes the spreadsheet document in more detail. Comparable
information applies to .csv file and pandas dataframe interfaces.

Model configuration is given with respect to SBML Level 3 Version 2
[SBML_L3V2]_ and related package specifications [SBML_fbc]_, [SBML_groups]_
and [SBML_distrib]_.
Please check these SBML specifications for more details.
SBML models coded in other levels/versions may have different attributes
and different requirements with respect to mandatory attributes.

.. contents:: Table of contents
   :local:
   :backlinks: none
   :depth: 3

Value types
-----------

These 'types' are used in the parameter description.

- **boolean**: ``True/False`` or ``1/0``, OpenOffice uses ``1/0``
- **numeric**: integer and floats
- **string**: single parameter value
- **key-value pair**: ``key=value``, whitespaces are removed by sbmlxdf
- **record**: several key-value pair items separated by ``,``, order does not matter
- **records**: several record items separated by ``;``
- **groups of records**: several records items enclosed by ``[...]``
  and separated by ``;``
- **special_record**: values concatenated with ``,``
- **special_records**: several special_record items concatenated with ``;``


Common attributes
-----------------

SBML defines common attributes of SBML objects. These common attributes
are mandatory **(M)** (required) or optional, depending on the SBML object.
sbmlxdf implements all **mandatory** attributes as per SBML L3V2.
**optional** common attributes are supported on the top level SBML
components like ``species``, ``compartments``, ``reactions``, etc.
However, **optional** common attributes are not supported on all lower levels
of the SBML object composition to keep the solution lightweight.

Example:

- optional attribute ``miriam-nnotation`` is supported on the top level of
  ``reaction``, however not on the lower level of **kineticLaw**.

- optional attribute ``sboterm``, on the other hand, is supported on the
  top level of ``reaction`` and also on the lower levels
  **reactants** and **products**.

id
~~

Type: **string**

Identifier of SBML objects. Must be unique in the model.
Usually **first column** in a sheet, as it is used as an index.
``id`` values must start with a letter or underscore '_'. Only letters,
digits and underscores are allowed.

Example::

  M_14glucan_c

name
~~~~

Type: **string**

A human-readable label of the component and less restrictive on the allowed
characters.

Example::

  1,4-alpha-D-glucan


metaid
~~~~~~

Type: **string**

Identifier to link ``xxx-history`` and ``miriam-annotation`` to a component.
Values are in a separate namespace. I.e. they can overlap with ``id`` values.

Example::

  M_14glucan_c

.. _sboterm:

sboterm
~~~~~~~

Type: **string**

Format is 'SBO:' followed by 7 digits. See also
`Systems Biology Ontology website <http://www.ebi.ac.uk/sbo/main/tree>`_.
SBML puts restrictions on which range of SBO terms may be used
for individual components, see Table 6 in [SBML_L3V2]_.

Example::

  SBO:0000290

created-history
~~~~~~~~~~~~~~~

Type: **string**

One of three attributes of model history. Requires ``metaid``.
String is coded in `W3C date format <https://www.w3.org/TR/NOTE-datetime>`_.
When creating the new model you can use the string **localtime** instead.

Example::

  2005-02-06T23:39:40Z


modified-history
~~~~~~~~~~~~~~~~

Type: **special_records**

One of three attributes of model history. Requires ``metaid``.
Each special_record holds a string coded in W3C date format.
You may use the string **localtime** when adding the current timestamp.

Example::

  2020-09-25T10:00:00+01:00; localtime


creators-history
~~~~~~~~~~~~~~~~

Type: **records**

One of three attributes of model history. Requires ``metaid``.

Each record contains following attributes:

- **fn**: family name
- **gn**: given name
- **org**: organization name
- **email**: e-mail address

Example::

  fn=Schubert, gn=Peter, org=Heinrich-Heine-University Duesseldorf, email=Peter.Schubert@hhu.de

miriam-annotation
~~~~~~~~~~~~~~~~~

Type: **special_records**

Each special_record starts with a qualifier element
(see Table 8 in [SBML_L3V2]_ for allowed qualifier elements),
followed by values specifying resources.
The resource strings do not contain the prefixed
'http://identifiers.org/', which is removed/added by sbmlxdf internally
when reading/writing a SBML model.

Example::

  bqbiol:is, bigg.metabolite/14glucan, biocyc/META:1-4-alpha-D-Glucan, metanetx.chemical/MNXM2905, seed.compound/cpd21754

xml-annotation
~~~~~~~~~~~~~~

Type: **records**

Currently only simple XML elements are supported. These specify
namespace, a prefix, the token of the XML-element and contain one or more
XML-attributes.

Each record contains following attributes:

- **ns_ur**: (M), namespace uri
- **prefix**: (M), namespace prefix used
- **token**: (M), token of XML element
- **key-value pairs**: XML attributes

Example::

  ns_uri=http://www.hhu.de/ccb/bgm/ns, prefix=bgm, token=molecule, weight_Da=71960, prot_len=638


notes
~~~~~

Type: **string**

String coded in HTML intended for humans.

Examples::

  In condition XYZ this protein is always phosphorylated (active).

  <h2>Hugo model based on Hugo R code GMw_v8, Mar, 2021</h2> <p>Protein synthesis reactions as per Deniz formulation</p>

uncertainty
~~~~~~~~~~~

Type: **groups of records**

Uncertainties can be added to elements with a mathematical
meaning, like ``compartments``, ``parameters``, ``species``.
Requires ``distrib`` package, see :ref:`sbml`.
For more details, please check [SBML_distrib]_.

Each record contains following attributes:

- **param**: (M), parameter type
- **val**: value (float)
- **vall**: lower value (float)
- **valu**: upper value (float)
- **var**: variable (reference to an ``id``)
- **varl**: lower variable (reference to an ``id``)
- **varu**: upper variable (reference to an ``id``)
- **units**: units of measurement
- **url**: reference to an external parameter
- **math**: mathml string
- **lup**: encapsulating a list of parameter records

Examples::

  [param=standardDeviation, val=0.3]

  [param=distribution, url=http://www.probonto.org/ontology#PROB_k0001263, name=zeta, lup=[param=externalParameter, val=2.37, url=http://purl.obolibrary.org/obo/STATO_0000436, name=shape]]


Sheets
------

This section describes the individual sheets that can appear in a
spreadsheet document and are recognized by sbmlxdf. Sheet names and
attribute names are significant and case sensitive.

Other interfaces:

- **.csv file interface**: sheets names correspond to individual
  file names, ``<sheet>.csv``.
- **pandas DataFrame interface**: sheet names correspond to
  keys of a dictionary with values being pandas dataframes.

Actually ``smbl`` and ``modelAttrs`` relate to pandas series
objects. In the spreadsheet, these two sheets have
attribute names in their first and values in their second column.

Both ``smbl`` and ``modelAttrs`` are required in every model.

The ``id`` attribute of the main SBML component must exist in
``funcDefs``, ``unitDefs``, ``compartments``, ``species``,
``parameters``, ``initAssign``, ``reactions``,
``fbcObjectives`` and ``fbcGeneProducts``,
where it must be used in the first column. ``id`` is used as a unique index.
Other attribute columns can be in any order.

It is the responsibility of the modeler to resolve internal dependencies.
E.g. if a species is used in a ``reaction`` as
reactant or product, this species must exist in ``species`` with same ``id``
value.

Empty cells in a table correspond to unspecified optional values. You should
ensure that empty cells are actually empty and do not contain space characters.
In record items only specify those key-value pair which have
attributes specified.

.. _sbml:

sbml (M)
~~~~~~~~

SBML container information.

Common SBML object attributes are not allowed, e.g. no ``id`` attribute.
Attributes names are in the first column.

Attributes:

- **level**: (M), numeric, SBML core level, e.g: '3'
- **version**: (M), numeric, SBML core version, e.g. '2'
- **packages**: records, each record contains following attributes:

  - **name**: (M), string, package name ('fbc', 'groups' or 'distrib')
  - **version**: (M), numeric, package version
  - **required**: (M), boolean

  Example::

    name=fbc, version=2, required=False; name=groups, version=1, required=False


modelAttrs (M)
~~~~~~~~~~~~~~

General model information, including model default values.
Attributes names are in the first column.

Attributes:

- **substanceUnits**: string, referencing a base unit or an ``id`` in ``unitDefs``
- **timeUnits**: string, referencing a base unit or an ``id`` in ``unitDefs``
  (recommended to specify for kinetic models)
- **volumeUnits**: string, referencing a base unit or an ``id`` in ``unitDefs``
- **areaUnits**: string, referencing a base unit or an ``id`` in ``unitDefs``
- **lengthUnits**: string, referencing a base unit or an ``id`` in ``unitDefs``
- **extentUnits**: string, referencing a base unit or an ``id`` in ``unitDefs``
  (recommended to specify for kinetic models)
- **conversionFactor**: string, referencing an ``id`` in ``parameters``
- **fbcStrict**: boolean, required when package ``fbc`` is used

funcDefs
~~~~~~~~

User defined functions that may be used inside mathematical
expressions.

Attributes:

- **id**: (M), in first column
- **math**: string, coded in mathml notation

  Example::

    lambda(kcat, Enz, P, KmP, kcat * Enz / (1.0 dimensionless + P / KmP))

unitDefs
~~~~~~~~

User defined units that may be used in the model.

Attributes:

- **id**: (M), in first column
- **units**: records, each record contains following attributes:

  - **kind**: (M), string, referencing a base unit, see table 2 in [SBML_L3V2]_
  - **exp**: (M), numeric
  - **scale**: (M), numeric
  - **mult**: (M), numeric

  Example::

    kind=mole, exp=1, scale=0, mult=1.0; kind=litre, exp=-1, scale=0, mult=1.0

compartments
~~~~~~~~~~~~

Compartments used in the model.

Attributes:

- **id**: (M), in first column
- **constant**: (M), boolean
- **spatialDimension**: float, e.g. '3'
- **size**: float
- **units**: string, referencing a base unit or an ``id`` in ``unitDefs``
  (recommended to specify, unless specified in ``modelAttrs`` together
  with **spatialDimension**)

parameters
~~~~~~~~~~

Global parameters used in the model.

Attributes:

- **id**: (M), in first column
- **constant**: (M), boolean
- **value**: float
- **units**: string, referencing a base unit or an ``id`` in ``unitDefs``,
  (recommended to specify)

species
~~~~~~~

Species used in the model.

Attributes:

- **id**: (M), in first column
- **compartment**: (M), string, referencing an ``id`` in ``compartments``
- **constant**: (M), boolean
- **hasOnlySubstanceUnits**: (M), boolean
- **boundaryCondition**: (M), boolean
- **initialAmount**: float, mutual exclusive with **initialConcentration**
- **initialConcentration**: float, mutual exclusive with **initialAmount**
- **substanceUnits**: string, referencing a base unit or an ``id`` in
  ``unitDefs`` (recommended to specify, unless specified in ``modelAttrs``)
- **conversionFactor**: string, referencing an ``id`` in ``parameters``
- **fbcCharge**: signed integer, requires ``fbc`` package, see :ref:`sbml`.
- **fbcChemicalFormula**: string, requires ``fbc`` package

  Example::

    C2H5Br


reactions
~~~~~~~~~

Reactions used in the model.

Attributes:

- **id**: (M), in first column
- **reversible**: (M), boolean
- **compartment**: string, referencing an ``id`` in ``compartments``
- **reactants**: records, each record contains following attributes:

  - **species**: (M), referencing an ``id`` in ``species``
  - **const**: (M), boolean
  - **stoic**: float, stoichiometry (recommended to specify)
  - **id**
  - **sboterm**

  Example::

    species=MKK_P, stoic=1.0, const=True

- **products**: records, same coding as in **reactants**
- **modifiers**: records, each record contains following attributes:

  - **species**: (M) referencing an ``id`` in ``species``
  - **id**
  - **sboterm**

  Example::

    species=MKKK_P

- **kineticLaw**: string, coded in mathml notation, referencing ``id``'s used in
  **reactants**, **products**, **modifiers** and defined in ``compartments``,
  ``parameters``, **localParams** and ``funDefs``.

  Example::

    cell * MM_1P(kcat_t1, t1, G, KmP)

- **localParams**: records, each record contains following attributes:

  - **id**: (M)
  - **value**: float
  - **units**: string, referencing a base unit or an ``id`` in ``unitDefs``
    (recommended to specify)
  - **sboterm**
  - **name**: do not use ',' or ';'

  Example::

    id=KmP, value=0.08, units=M

- **fbcLowerFluxBound**: string, referencing an ``id`` in ``parameters``.
  Requires ``fbc`` package, see :ref:`sbml`.
- **fbcUpperFluxBound**: string, referencing an ``id`` in ``parameters``.
  Requires ``fbc`` package.
- **fbcGeneProdAssoc**: record containing following attributes
  (requires ``fbc`` package):

  - **assoc**: (M), gene product association string, which contains references
    to ``id``'s in ``fbcGeneProducts``, logical operators 'and'/'or'
    and brackets '()'.

  - **id**
  - **name**
  - **sboterm**

  Example::

    assoc=(G_b0902 and G_b0905)


initAssign
~~~~~~~~~~

Initial value definitions, for setting values prior to model simulation.
This overwrites values already specified on component level.

Attributes:

- **symbol**: (M), in first column, string, referencing an ``id`` defined in
  ``compartments``, ``parameters``, ``species``, **reactants** or **products**
- **math**: string, coded in mathml notation

  Example::

    x * 2 dimensionless

rules
~~~~~

Rules used in the model to define relationships and the dynamical behaviors
of variables.

Attributes:

- **rule**: (M), string, defining type of rule ('RateRule', 'AlgebraicRule',
  or 'AssignmentRule')
- **variable**: string, referencing an ``id``
- **math**: string, coded in mathml notation

  Examples::

    Keq * S1


events
~~~~~~

User defined events used in the model.

Attributes:

- **valFromTriggerTime**: (M), boolean
- **id**
- **triggerInitVal**: boolean, required when trigger is used
- **triggerPersistent**: boolean, required when trigger is used
- **triggerMath**: string, coded in mathml notation
- **triggerSboTerm**: string, coded as :ref:`sboterm`
- **priorityMath**: string, coded in mathml notation
- **prioritySboTerm**: string, coded as :ref:`sboterm`
- **delayMath**: string, coded in mathml notation
- **delaySboTerm**: string, coded as :ref:`sboterm`
- **eventAssign**: records, each record contains following attributes:

  - **variable**: (M), referencing an ``id`` defined in ``compartments``,
    ``parameters``, ``species``, **reactants** or **products**
  - **math**: string, coded in mathml notation
  - **sboterm**

  Example::

    variable=n, math=3 dimensionless

constraints
~~~~~~~~~~~

Constraints that state assumptions under which the model is designed to operate.

Attributes:

- **message**: string, coded in HTML

  Example::

    Species S1 is out of range.

- **math**: string, coded in mathml notation. Returing a boolean.

  Example::

    (1.3 mole < S1) && (S1 < 100 mole)


fbcObjectives
~~~~~~~~~~~~~

Flux Balance Objectives of the model. Requires ``fbc`` package,
see :ref:`sbml`. For more detail, please check [SBML_fbc]_.

Attributes:

- **id**: (M), in first column
- **active**: (M), boolean indicating if this objective is active (only
  one ojbective should be active)
- **type**: (M), string, defining FbcType ('maximize', 'minimize')
- **fluxObjectives**: records, each record contains following attributes:

  - **reac**: (M), reaction, referencing a ``id`` in ``reactions``
  - **coef**: (M), coefficient (float)
  - **id**
  - **name**
  - **sboterm**

  Example::

    reac=J8, coef=1.0


fbcGeneProducts
~~~~~~~~~~~~~~~

Gene Products that are used in ``reactions`` for gene product associations.
Requires ``fbc`` packages, see :ref:`sbml`.

Attributes:

- **id**: (M), in first column
- **label**: string
- **associatedSpec**: string, referencing an ``id`` in ``species``


groups
~~~~~~

Relationship among SBML components. Check [SBML_groups]_ for more information.
Requires ``groups`` packages, see :ref:`sbml`.

Attributes:

- **kind**: (M), string, indicate nature of group ('partonomy', 'classification'
  'collection')
- **listMembers**: records, containing following attributes:

  - **id**
  - **name**
  - **sboterm**

  Example::

    id=lom_g3, name=list_of_members g3, sboterm=SBO:0000633

- **members**: records, each record contains following attributes:

  - **idref**: either **idref** or **metaidref** must be defined, string,
    referencing an ``id`` defined in the model.
  - **metaidref**: either **idref** or **metaidref** must be defined, string,
    referencing a ``metaid`` defined in the model.
  - **id**
  - **name**
  - **sboterm**

  Example::

    idRef=R_GLXCL; idRef=R_GLYCK; idRef=R_GLYCLTDx; idRef=R_GLYCLTDy
