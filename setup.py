#!/usr/bin/env python
# encoding: utf-8

from setuptools import setup, find_packages

readme = open('README.txt', 'rt').read()

classifiers = ""
version = '1.0.0'

setup(
    name='viirsmend',
    version=version,
    description="Library and scripts to remap imager data to a grid",
    long_description=readme,
    classifiers=filter(None, classifiers.split("\n")),
    keywords='',
    author='Nick Bearson',
    author_email='nickb@ssec.wisc.edu',
    license='LGPLv3',
    packages=['viirsmend'],
    package_dir={'viirsmend' : 'viirsmend'},
    install_requires=[
        'numpy',
        'scipy',
#        'matplotlib',  # Used for verification purposes, not required
        ],
)
