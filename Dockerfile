# FROM
# centos Image (centos6 タグ付き) を docker pull して使う
FROM ubuntu:20.04
 
# MAINTAINER
# Dockerfile 作成者を明記する
LABEL author="Haruki Anbai" 
# RUN
# Image を Container として build するときに実行する Linux コマンドを定義
RUN apt install update && apt install -y \
    git \
    wget \
    build-essential \
    libncurses-dev

RUN mkdir test && cd test && bash && \
    git clone https://github.com/Mizunanari/COIAS_program_github.git && \
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    ~/miniconda3/bin/conda init  &&\
    conda env create -f env.yml &&\
    conda activate COIAS_program_github && \
    python setup12.py build_ext --inplace &&\
    cd findOrb &&\
    make -f linlunar.mak &&\
    make -f linmake

# CMD
# Container を run するたびに実行する Linux コマンドを定義
CMD ["echo", "now runnnig ..."]