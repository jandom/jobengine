#! /usr/bin/python

from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, Extension
from distutils.ccompiler import new_compiler

import sys, os
import glob
import shutil
import tempfile

#import spur, paramiko, scp, sqlalchemy

# REQUIREMENTS
# - spur
# - paramiko
# - gromacs wrapper
# - mdanalysis
# - sql alchemy	

required = ['spur', 'paramiko', 'scp', 'sqlalchemy', 'tempfile']

if __name__ == '__main__':

    extensions = []

    setup(name              = 'jobengine',
          version           = "alpha",
          packages          = [ 'jobengine',],
          package_dir       = {'jobengine': 'jobengine'},
          setup_requires   = required,
          install_requires = required,
          scripts           = glob.glob('jobengine/scripts/*.py'),
          ext_package       = 'jobengine',
          ext_modules       = extensions,
          zip_safe = False,     # as a zipped egg the *.so files are not found (at least in Ubuntu/Linux)
          )
