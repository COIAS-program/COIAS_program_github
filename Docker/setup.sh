#!/bin/bash

cd /opt/COIAS_program_github
conda env create -f env.yml

export CONDA_DEFAULT_ENV=COIAS_program_github

# condaのCOIAS_program_github環境下で、ビルド
chmod -R 700  ./*
/root/miniconda3/envs/COIAS_program_github/bin/python setup12.py build_ext --inplace

# Cythonのビルド
cd /opt/COIAS_program_github/findOrb
make -f linlunar.mak
make -f linmake

exec $SHELL -l

# APIを作業ディレクトリとする
cd /opt/COIAS_program_github/API

# API server を開始
/root/miniconda3/envs/COIAS_program_github/bin/uvicorn main:app --host 0.0.0.0 --reload