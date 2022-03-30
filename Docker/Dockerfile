FROM ubuntu:20.04

LABEL author="Haruki Anbai" 

SHELL ["/bin/bash", "-c"]

ENV TZ=Asia/Tokyo\
    DEBIAN_FRONTEND=noninteractive

#optを作業ディレクトリとする
WORKDIR /opt

#必要なパッケージをubuntuにインストール
RUN apt update && apt install -y\
    git\
    wget\
    build-essential\
    libncurses-dev\
    unzip\
    source-extractor\
    && rm -rf /var/lib/apt/lists/*

#miniconda3をインストール
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    chmod 700 ./Miniconda3-latest-Linux-x86_64.sh && \
    bash ./Miniconda3-latest-Linux-x86_64.sh -b && \
    ~/miniconda3/bin/conda init bash && \
    rm ./Miniconda3-latest-Linux-x86_64.sh

#miniconda3のPATHを通す
ENV PATH $PATH:/root/miniconda3/bin

#クローンをして、COIASのための環境構築
RUN git clone https://github.com/aizulab/COIAS_program_github.git --depth 1

# condaのCOIAS_program_github環境下で、ビルド
WORKDIR /opt/COIAS_program_github
RUN conda env create -n coias -f ./env/env.yml
RUN conda config --set auto_activate_base false

# conda activate coiasと同じ
SHELL ["conda", "run", "-n", "coias", "/bin/bash", "-c"]

# Cythonのビルド
RUN chmod -R 700 ./* && \
    /root/miniconda3/envs/coias/bin/python setup12.py build_ext --inplace

# C++のビルド
WORKDIR /opt/COIAS_program_github/findOrb
RUN make -f linlunar.mak && \
    make -f linmake

# COIAS_program_githubとfindOrbのPATHを通す
ENV PATH $PATH:/opt/COIAS_program_github
ENV PATH $PATH:/opt/COIAS_program_github/findOrb

# API server を開始
WORKDIR /opt/COIAS_program_github
ENTRYPOINT [ "bash", "/opt/COIAS_program_github/script/startup.sh" ]