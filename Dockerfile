FROM ubuntu:20.04

#optを作業ディレクトリとする
WORKDIR /opt

LABEL author="Haruki Anbai" 

#必要なパッケージをubuntuにインストール
RUN apt update && apt install -y \
    git \
    wget \
    build-essential \
    libncurses-dev \
    unzip

#miniconda3をインストール
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    chmod +x ./Miniconda3-latest-Linux-x86_64.sh && \
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

#condaのCOIAS_program_github環境下で、ビルド
RUN . ~/.bashrc && \
    conda activate COIAS_program_github && \
    cd COIAS_program_github && \
    chmod 700 ./* && \
    chmod 700 ./findOrb/* && \
    python setup12.py build_ext --inplace && \
    cd findOrb && \
    make -f linlunar.mak && \
    make -f linmake
    
#ローカルディレクトリ内のテスト画像をUbuntuへコピー
COPY ./SubaruHSC /opt/SubaruHSC
#COIAS_program_githubとfindOrbのPATHを通す
ENV PATH $PATH:/opt/COIAS_program_github
ENV PATH $PATH:/opt/COIAS_program_github/findOrb

CMD ["/bin/bash"]
