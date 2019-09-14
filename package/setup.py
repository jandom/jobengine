#! /usr/bin/python

import os
import sys
import tempfile
import shutil
import glob
from distutils.ccompiler import new_compiler
from setuptools import setup, Extension
from ez_setup import use_setuptools
use_setuptools()


required = ['paramiko', 'scp', 'sqlalchemy']

if __name__ == '__main__':

    extensions = []

    setup(name='jobengine',
          version="alpha",
          packages=['jobengine', ],
          package_dir={'jobengine': 'jobengine'},
          setup_requires=required,
          install_requires=required,
          scripts=glob.glob('jobengine/scripts/*.py'),
          ext_package='jobengine',
          ext_modules=extensions,
          zip_safe=False,
          # as a zipped egg the *.so files are not found (at least in
          # Ubuntu/Linux)
          )
