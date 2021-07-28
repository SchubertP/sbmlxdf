Installation
============

You need python3 installed on your system.

**sbmlxdf** can be installed via standard pip command

.. prompt:: bash $

   pip install sbmlxdf

.. note ::

   **python-libsbml-experimental** package will be installed during
   installation, if not installed already, to support features of the
   Distribution package.
   In case **python-libsbml** gets installed subsequently, e.g. by
   another Python package related to SBML, some sbmlxdf functionality
   might get lost, as both packages get imported with ``import libsbml``.
   Should this happen, support of distrib features can be recovered by
   installing **python-libsbml-experimental** manually using
   ``pip install``.

Should you be interested in sample SBML files, extracted from the
SBML specification documentation, you could clone the
repository.

.. prompt:: bash $

   git clone https://gitlab.cs.uni-duesseldorf.de/schubert/sbmlxdf
