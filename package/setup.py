#! /usr/bin/python

from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, Extension
from distutils.ccompiler import new_compiler

import sys, os
import glob
import shutil
import tempfile

if __name__ == '__main__':

    extensions = []

    setup(name              = 'jobengine',
          version           = "alpha",
          packages          = [ 'jobengine',],
          package_dir       = {'jobengine': 'jobengine'},
          scripts=['jobengine/scripts/qsubmit.py', 'jobengine/scripts/qserver.py'],
          ext_package       = 'jobengine',
          ext_modules       = extensions,
          zip_safe = False,     # as a zipped egg the *.so files are not found (at least in Ubuntu/Linux)
          )
