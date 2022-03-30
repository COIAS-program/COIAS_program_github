#!/bin/bash -su

# coiasをデフォルトに設定
source ~/miniconda3/etc/profile.d/conda.sh
conda activate coias

git pull
/root/miniconda3/envs/coias/bin/uvicorn API.main:app --host 0.0.0.0 --reload