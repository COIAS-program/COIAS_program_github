#!/usr/bin/env python
# -*- coding: utf-8 -*-
from distutils.core import setup, Extension
from Cython.Build import cythonize

import numpy

ext_modules = [
    Extension(
        "mktraclet", sources=["mktraclet.pyx"], include_dirs=[".", numpy.get_include()]
    )
]

setup(name="mktraclet", ext_modules=cythonize(ext_modules))

# python setup12.py build_ext --inplace
