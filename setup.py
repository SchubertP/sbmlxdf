# -*- coding: utf-8 -*-
import os
import re
from setuptools import setup, find_packages


setup_kwargs = {}

with open('README.md') as f:
    setup_kwargs['long_description'] = f.read()

# version from file
with open(os.path.join('sbmlxdf', '_version.py')) as f:
    mo = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                   f.read(), re.MULTILINE)
    if mo:
        setup_kwargs['version'] = mo.group(1)

setup(
    name='sbmlxdf',
    description='convert between SBML and tabular structures',
    author='Peter Schubert',
    author_email='peter.schubert@hhu.de',
    url='https://www.cs.hhu.de/lehrstuehle-und-arbeitsgruppen/computational-cell-biology',
    project_urls={
        "Source Code": 'https://github.com/SchubertP/sbmlxdf',
        "Documentation": 'https://sbmlxdf.readthedocs.io',
        "Bug Tracker": 'https://github.com/SchubertP/sbmlxdf/issues'},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
    license='GPL-3.0-or-later',
    long_description_content_type='text/markdown',
    packages=find_packages(exclude='docs'),
    install_requires=['numpy >= 2.5.0',
                      'pandas>=3.0.0',
                      'scipy>=1.18.0',
                      'python-libsbml>=5.19.0'],
    python_requires=">=3.12",
    keywords=['systems biology', 'metabolic modeling', 'SBML'],
    **setup_kwargs
)
