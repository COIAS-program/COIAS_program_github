FROM continuumio/miniconda3:latest

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
    locales\
    bash-completion

#言語を日本語に設定
RUN apt-get update && apt-get install -y locales && rm -rf /var/lib/apt/lists/* \
    && localedef -i ja_JP -c -f UTF-8 -A /usr/share/locale/locale.alias ja_JP.UTF-8
ENV LANG ja_JP.utf8

# COIAS_program_githubとfindOrbのPATHを通す
ENV PATH $PATH:/opt/COIAS_program_github
ENV PATH $PATH:/opt/COIAS_program_github/findOrb

RUN echo ". /etc/bash_completion" >> ~/.bashrc