#!/bin/bash -eu

# Dockerfile.devの実行後、コンテナ起動直後に実行される（bind後に処理を行うため）
# 設定は.devcontainer/devcontainer.jsonに記載

cd /opt/COIAS_program_github
conda env create -n coias -f ./env/env.yml

# coiasをデフォルトに設定
echo "conda activate coias" >> ~/.bashrc

#miniconda3のPATHを通す
echo "export PATH=$PATH:/root/miniconda3/envs/coias/bin" >> ~/.bashrc
. ~/.bashrc

# script上でcoiasに切り替え
source ~/miniconda3/etc/profile.d/conda.sh
conda activate coias

# 環境の確認
conda info -e

