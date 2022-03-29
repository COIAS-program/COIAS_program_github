#!/bin/bash -eu

git pull
/root/miniconda3/envs/coias/bin/uvicorn API.main:app --host 0.0.0.0 --reload