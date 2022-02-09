# Docker commands for COIAS

## Install git

```
apt install git
```
## git clone
```
cd /home
mkdir test
cd test
git clone https://github.com/Mizunanari/COIAS_program_github.git
```
## Install Conda
```
apt install wget

wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh

bash Miniconda3-latest-Linux-x86_64.sh
~/miniconda3/bin/conda init bash
bash
```

## Create conda env
```
conda env create -f env.yml
conda activate COIAS_program_github
````

## compile 

```
apt install build-essential
apt install libncurses-dev
python setup12.py build_ext --inplace
cd findOrb
make -f linlunar.mak
make -f linmake
```

## conda remove env

```
conda remove -n COIAS_program_github --all
```

sudo docker cp SubaruHSC.zip  0b540ce5e620://home/test
