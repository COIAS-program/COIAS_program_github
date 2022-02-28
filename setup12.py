#!/usr/bin/env python
# -*- coding: utf-8 -*-
from distutils.core import setup
from distutils.extension import Extension

import numpy
from Cython.Distutils import build_ext

ext_modules = [
    Extension("mktraclet", ["mktraclet.pyx"], include_dirs=[numpy.get_include()])
]

setup(cmdclass={"build_ext": build_ext}, ext_modules=ext_modules)

# python setup12.py build_ext --inplace
