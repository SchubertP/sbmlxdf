# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

setup(
    name='sbmlxdf',
    version='0.1.0',
    description='convert between SBML coded models and DataFrames/Excel/.csv',
    long_description=readme,
    author='Peter Schubert',
    author_email='peter.schubert@hhu.de',
    url='https://gitlab.com/pschubert/samplexdfmod',
    license='LGPL',
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires = ['pandas>=0.25.0',
                        'xlrd>=1.1.0',
                        'openpyxl>=2.6.0',
                        'python-libsbml-experimental>=5.18.0']
)
