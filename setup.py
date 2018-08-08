#!/usr/bin/env python3
"""
Release notes:
* Bump version in syncset/__init__.py
* Commit and push changes
* Build package: rm dist/* && python setup.py sdist bdist_wheel
* Push to PyPI: twine upload dist/*
* Create release on GitHub
"""
import io
import os
from setuptools import setup


__version__ = None
with io.open(os.path.join(os.path.dirname(__file__), 'syncset/__init__.py'), encoding='utf-8') as f:
    for l in f:
        if not l.startswith('__version__'):
            continue
        __version__ = l.split('=')[1].strip(' "\'\n')
        break


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()

setup(
    name='syncset',
    version=__version__,
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
