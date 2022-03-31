#!/bin/bash -eu

# Dockerfile.devの実行後、コンテナ起動直後に実行される（bind後に処理を行うため）
# 設定は.devcontainer/devcontainer.jsonに記載

cd /opt/coias-back-app
conda env create -n coias -f ./env/env.yml
conda config --set auto_activate_base false

echo -en "# coiasに切り替え\nconda activate coias" >> ~/.bashrc

# condaのcoias-back-app環境下で、ビルド
. /opt/coias-back-app/script/a_coias.sh

# 環境の出力
conda info -e

# 権限の付与
chmod -R 700 /opt/coias-back-app

# Cythonのビルド
python setup12.py build_ext --inplace

# C++のビルド
cd /opt/coias-back-app/findOrb
make -f linlunar.mak
make -f linmake