#!/usr/bin/env python
# encoding: utf-8

from setuptools import setup, find_packages

readme = open('README.md', 'rt').read()

classifiers = ""
version = '1.0.2'

setup(
    name='viirsmend',
    version=version,
    description="Python package for mending bowtie removed pixels in a VIIRS image",
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
    entry_points={
        'console_scripts':
            ['viirsmend=viirsmend.mender:main']
    }

)
