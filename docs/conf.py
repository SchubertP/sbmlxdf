# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))


# -- Project information -----------------------------------------------------

import os
import re
import sys


# retrieve version number
def get_version(project):
    """Return package version from <project>/_version.py"""
    version_path = os.path.join('..', project, '_version.py')
    if not os.path.exists(version_path):
        print('Version file not found: ' + version_path)
        sys.exit(-1)
    with open(version_path) as f:
        mo = re.search(r"^__version__\s*=\s*['\"]([^'\"]*)['\"]",
                       f.read(), re.MULTILINE)
        try:
            return mo.group(1)
        except AttributeError as e:
            print('Attribute "__version__" not found')
            sys.exit(-1)


# general information about the project
project = 'sbmlxdf'
copyright = '2021, Peter Schubert'
author = 'Peter Schubert'
release = get_version(project)

# insert link to project for autodoc
sys.path.insert(0, os.path.abspath('..'))

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.githubpages",
    ]

# Add any paths that contain templates here, relative to this directory.
# templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
# html_theme = 'alabaster'
html_theme = "sphinx_rtd_theme"
