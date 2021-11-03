## sbmlxdf - convert between SBML and tabular structures

**sbmlxdf** is lightweight and transparent converter from
SBML to pandas Dataframes (sbml2df) and
from pandas Dataframes to SBML (df2sbml).

sbmlxdf supports, with few exceptions, all functionality of **SBML L3V2
core** package [1] and extension packages **Flux Balance Constraints
(fbc)** [2], **Groups (groups)** [3] and **Distributions
(distrib)** [4].

using **libSBML API** for accessing SBML [5].

Note: **python-libsbml-experimental** Python package is required only,
when using features of SBML extension package `distrib`. 
**python-libsbml** Python package can be used in all other cases.
**python-libsbml** and **python-libsbml-experimental** both share the 
same top level identifier **libsbml** (`import libsbml`). Conflicts can be resolved by
pip uninstalling both packages and subsequntly installing the 
favoured package: e.g.

    $ pip3 uninstall python-libsbml-experimental
    $ pip3 uninstall python-libsbml
    $ pip3 install python-libsbml-experimental

## Benefits

### kinetic modelers with and without programming skills
- overcome hesitation of creating own models in SBML
- have a tool for flexible kinetic modelling using spreadsheets
- inspect SBML models
- create/extend SBML models
- use latest SBML features
- generate ‘correct’ SBML models

### Python programmers
- get access to SBML model data via pandas DataFrames,
  e.g. for use in their optimizers
- can evaluate different model design strategies

## Features
- support of SBML L3V2 core [1], including:

  - model history, miriam-annotations, xml-annotations
  - units of measurement
  - local/global parameters
  - function definitions
  - Flux Balance Constraints package [2]
  - Groups package [3]
  - Distributions package [4]

 **sbmxdf** does not intent to support SBML packages related to graphical
 representations of network models. I.e. packages **Layout** and
 **Rendering** are not supported. Other released SBML packages as of July
 2021, see [package status](http://sbml.org/Documents/Specifications)
 i.e. **Hierarchical Model Composition**,
 **Multistate and Multicomponent Species** and **Qualitative Models** are
 not supported at the moment, but might be included in future versions.

## Small Python examples

(Note: Users without programming experience may use a command line interface
to convert between SBML format and spreadsheet format)

   1. Convert SBML model to spreadsheet
   2. Check SBML compliance of spreadsheet model and convert to SBML
   3. Access SBML model data

```python
>>> import sbmlxdf
>>>
>>> model = sbmlxdf.Model('BIOMD0000000010_url.xml')
>>> model.to_excel('BIOMD0000000010_ulr.xlsx')
```

```python
>>> import sbmlxdf
>>>
>>> upd_model = sbmlxdf.Model('BIO10_upd.xlsx')
>>> print('SBML validation result:', upd_model.validate_sbml('tmp.xml'))
>>> upd_model.export_sbml('BIO10_upd.xml')
```

```python
>>> import sbmlxdf
>>>
>>> model = sbmlxdf.Model('BIO10_upd.xml')
>>> model_df = model.to_df()
>>> print(model_df.keys())
>>>
>>> df_r = model_df['reactions']
>>>
>>> print(len(df_r), 'reactions found, first reaction:' )
>>> print(df_r.iloc[0])
>>>
>>> for id, reaction in df_r.iterrows():
>>>   print('reaction:', id)
>>>   for record in sbmlxdf.extract_records(reaction['reactants']):
>>>      print('  reactant: ', sbmlxdf.extract_params(record))
>>>   for record in sbmlxdf.extract_records(reaction['products']):
>>>      print('  product:  ', sbmlxdf.extract_params(record))
```

## Documentation

Introductory tutorials, how-to's and other useful documentation are available
on [Read the Docs](https://sbmlxdf.readthedocs.io/en/latest/index.html)

## Installing

**sbmlxdf** is available on PyPI:

```console
$ python -m pip install sbmlxdf
```

## License

[GPLv3](LICENSE.txt)


Peter Schubert, October 2020

### References

[1]: The Systems Biology Markup Language (SBML): Language Specification for
Level 3 Version 2 Core (Release 2) Authors: Michael Hucka, Frank T. Bergmann,
Claudine Chaouiya, Andreas Dräger, Stefan Hoops, Sarah M. Keating, Matthias
König, Nicolas Le Novère, Chris J. Myers, Brett G. Olivier, Sven Sahle,
James C. Schaff, Rahuman Sheriff, Lucian P. Smith, Dagmar Waltemath,
Darren J. Wilkinson, and Fengkai Zhang

[2]: Olivier, B. G., & Bergmann, F. T. (2018). SBML Level 3 Package:
Flux Balance Constraints version 2. Journal of Integrative Bioinformatics,
15(1), 20170082.

[3]: Hucka, M., & Smith, L. P. (2016). SBML Level 3 package: Groups,
Version 1 Release 1. Journal of Integrative Bioinformatics, 13(3), 290.

[4]: Smith, L. P., Moodie, S. L., Bergmann, F. T., Gillespie, C., Keating,
S. M., König, M., Myers, C. J., Swat, M. J., Wilkinson, D.J.,
and Hucka, M. (2020). The Distributions Package for SBML Level 3.
Retrieved from from COMBINE, https://identifiers.org/combine.specifications/
sbml.level-3.version-1.distrib.version-1.release-1
