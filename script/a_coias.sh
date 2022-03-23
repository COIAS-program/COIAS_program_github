#!/bin/bash -su

# coiasをデフォルトに設定
source ~/miniconda3/etc/profile.d/conda.sh
conda activate coias

# coias pythonライブラリのPATHを通す
export PATH=$PATH:/root/miniconda3/envs/coias/bin