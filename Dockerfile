FROM ubuntu:20.04

LABEL author="Haruki Anbai" 

SHELL ["/bin/bash", "-c"]

#optを作業ディレクトリとする
WORKDIR /opt

#必要なパッケージをubuntuにインストール
RUN apt update && apt install -y \
    git \
    wget \
    build-essential \
    libncurses-dev \
    unzip

#miniconda3をインストール
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    chmod 700 ./Miniconda3-latest-Linux-x86_64.sh && \
    bash ./Miniconda3-latest-Linux-x86_64.sh -b && \
    ~/miniconda3/bin/conda init bash && \
    rm ./Miniconda3-latest-Linux-x86_64.sh && \
    echo "conda activate COIAS_program_github" >> ~/.bashrc

#miniconda3のPATHを通す
ENV PATH $PATH:/root/miniconda3/bin

#クローンをして、COIASのための環境構築（この処理には500秒前後かかる）
RUN git clone https://github.com/Mizunanari/COIAS_program_github.git && \
    cd COIAS_program_github && \    
    conda env create -f env.yml

# conda activate COIAS_program_githubと同じ
ENV CONDA_DEFAULT_ENV COIAS_program_github

# condaのCOIAS_program_github環境下で、ビルド
WORKDIR /opt/COIAS_program_github

# todo debug moduleを見る
RUN conda list | grep numpy >> /root/log.txt

RUN chmod -R 700  ./* && \
    python setup12.py build_ext --inplace 2>> /root/log.txt ; exit 0

    # todo errorを握りつぶす

# Cythonのビルド
WORKDIR /opt/COIAS_program_github/findOrb
RUN make -f linlunar.mak && \
    make -f linmake
    
# COIAS_program_githubとfindOrbのPATHを通す
ENV PATH $PATH:/opt/COIAS_program_github
ENV PATH $PATH:/opt/COIAS_program_github/findOrb

# APIを作業ディレクトリとする
WORKDIR /opt/COIAS_program_github/API

# API server を開始
ENTRYPOINT /root/miniconda3/envs/COIAS_program_github/bin/uvicorn main:app --host 0.0.0.0 --reload