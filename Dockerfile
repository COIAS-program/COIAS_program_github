FROM ubuntu:20.04
 
LABEL author="Haruki Anbai" 
RUN apt update && apt-get install -y \
    git \
    wget \
    build-essential \
    libncurses-dev
    
RUN cd opt && mkdir test && cd test  && bash
    
RUN git clone https://github.com/Mizunanari/COIAS_program_github.git &&\
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    chmod +x ./Miniconda3-latest-Linux-x86_64.sh && \
    bash ./Miniconda3-latest-Linux-x86_64.sh -b && \
    ~/miniconda3/bin/conda init  &&\
    . ~/.bashrc &&\
    cd COIAS_program_github &&\
    bash && \
    conda env create -f env.yml &&\
    conda activate COIAS_program_github &&\
    python setup12.py build_ext --inplace &&\
    cd findOrb &&\
    make -f linlunar.mak &&\
    make -f linmake

COPY ./SubaruHSC/ /root/opt/test/SubaruHSC

RUN ls ~/opt/test/ &&\
    cd ~/opt/test/SubaruHSC/ &&\
    echo "PATH=$PATH:/root/opt/test/COIAS_program_github" >> ~/.bashrc &&\
    echo "PATH=$PATH:/root/opt/test/COIAS_program_github/findOrb" >> ~/.bashrc 

CMD ["echo", "finish"]

#["AstsearchR"] 