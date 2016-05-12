#!/usr/bin/env python3
"""
To upload to PyPI:
   python setup.py sdist upload
"""
import os
from setuptools import setup


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()

setup(
    name='syncset',
    version='1.2.2',
    author='Erik Cederstrand',
    author_email='erik@cederstrand.dk',
    license='BSD',
    description='Extension of Python set() which is able to synchronize sets of comparable objects',
    long_description=read('README.rst'),
    keywords='set dict sync synchronize synchronization',
    packages=['syncset'],
    test_suite='tests',
    zip_safe=False,
    url='https://github.com/ecederstrand/py-syncset',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
    ],
)
