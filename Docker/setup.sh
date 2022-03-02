#!/bin/bash -eu

# Dockerfile.devの実行後、コンテナ起動直後に実行される（bind後に処理を行うため）
# 設定は.devcontainer/devcontainer.jsonに記載

cd /opt/COIAS_program_github
conda env create -n coias -f ./env/ubuntu_env.yml

conda activate coias

# coiasをデフォルトに設定
echo "conda activate coias" >> ~/.bashrc

# condaのCOIAS_program_github環境下で、ビルド
chmod -R 700 /opt/COIAS_program_github
/root/miniconda3/envs/coias/bin/python setup12.py build_ext --inplace

# Cythonのビルド
cd /opt/COIAS_program_github/findOrb
make -f linlunar.mak
make -f linmake