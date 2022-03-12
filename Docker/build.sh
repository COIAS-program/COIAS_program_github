#!/bin/bash -eu

# condaのCOIAS_program_github環境下で、ビルド
chmod -R 700 /opt/COIAS_program_github

# Cythonのビルド
cythonize mktraclet.pyx

# Cのビルド
cd /opt/COIAS_program_github/findOrb
make -f linlunar.mak
make -f linmake