#!/bin/bash -eu

# Dockerfile.devの実行後、コンテナ起動直後に実行される（bind後に処理を行うため）
# 設定は.devcontainer/devcontainer.jsonに記載

cd /opt/COIAS_program_github
conda env create -n coias -f ./env/env.yml
conda config --set auto_activate_base false

echo -en "# coiasに切り替え\nconda activate coias" >> ~/.bashrc

# condaのCOIAS_program_github環境下で、ビルド
. /opt/COIAS_program_github/Docker/a_coias.sh

# 環境の出力
conda info -e

# 権限の付与
chmod -R 700 /opt/COIAS_program_github

# Cythonのビルド
cythonize mktraclet.pyx

# C++のビルド
cd /opt/COIAS_program_github/findOrb
make -f linlunar.mak
make -f linmake