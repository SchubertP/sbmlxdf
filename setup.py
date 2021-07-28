# -*- coding: utf-8 -*-
import os
import re
from setuptools import setup, find_packages


setup_kwargs = {}

with open('README.md') as f:
    setup_kwargs['long_description'] = f.read()
setup_kwargs['long_description_content_type']="text/markdown",

# version from file
with open(os.path.join('sbmlxdf','_version.py')) as f:
    mo = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                   f.read(), re.MULTILINE)
    if mo:
        setup_kwargs['version'] = mo.group(1)

setup(
    name='sbmlxdf',
    description='convert between SBML and tabular structures',
    author='Peter Schubert',
    author_email='peter.schubert@hhu.de',
    url='https://gitlab.cs.uni-duesseldorf.de/schubert/sbmlxdf',
    project_urls={ "Bug Tracker":
        'https://gitlab.cs.uni-duesseldorf.de/schubert/sbmlxdf/-/issues'},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: OS Independent",
    ],
    license='GPLv3',
    packages=find_packages(exclude=('docs')),
    install_requires = ['pandas>=0.25.0',
                        'xlrd>=1.1.0',
                        'openpyxl>=2.6.0',
                        'python-libsbml-experimental>=5.18.0'],
    python_requires=">=3.7",
    **setup_kwargs
)
