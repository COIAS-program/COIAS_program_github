#!/bin/bash

## This script is to set the environment to run COIAS programs ##
## Last modified: 2022.1.12 N.Maeda

## Usage 
## (Prepare) Install Anaconda on your environment
## Execute the following command on your terminal:
## $ bash env_setting.sh

## create a virtual environment
echo "create a virtual environment for COIAS"
conda create -n coias python=3.8
source activate coias

## install the packages for coias
conda install -y astropy==4.3.1
conda install -y matplotlib==3.4.3
conda install -y scipy==1.7.1
#conda install -y -c astropy astroquery==0.4.4
conda install -y -c astropy photutils==1.0.1
conda install -y ephem==4.0.0.2
conda install -y cython==0.29.24
conda install -y pandas==1.3.4
conda install -y bokeh==2.4.1
conda install -y -c conda-forge astromatic-source-extractor==2.25.0
conda install -c anaconda beautifulsoup4==4.11.1
conda install -c anaconda lxml==4.8.0

pip install --upgrade pip
pip install -y julian==0.14
pip install -y astroquery==0.4.4

## COIAS Download
Install_Location=`pwd`
echo "COIAS will be installed into this location:"
echo $Install_Location
echo -n "OK? [Y/n] >> "
read ANS
case $ANS in
	"" | [Yy]* )
		echo ">> Yes"
		;;
	* )
		echo "Specify a different location below"
		read -r Install_Location
		echo "COIAS will be installed into " $Install_Location
		;;
	esac

COIAS_PATH=$Install_Location
#echo $COIAS_PATH

## Download COIAS programs from github
git clone https://github.com/COIAS-program/COIAS_program_github $COIAS_PATH

## Make PATH
echo "Making PATH..."
echo export PATH="$COIAS_PATH:$PATH" >> ~/.bashrc
echo export PATH="$COIAS_PATH/findOrb:$PATH" >> ~/.bashrc
echo export PATH="$COIAS_PATH/COIASlibs:$PATH" >> ~/.bashrc
echo export PATH="$COIAS_PATH/src1_preprocess:$PATH" >> ~/.bashrc
echo export PATH="$COIAS_PATH/src2_startsearch2R:$PATH" >> ~/.bashrc
echo export PATH="$COIAS_PATH/src3_prempsearchC-before:$PATH" >> ~/.bashrc
echo export PATH="$COIAS_PATH/src4_prempsearchC-after:$PATH" >> ~/.bashrc
echo export PATH="$COIAS_PATH/src5_astsearch_new:$PATH" >> ~/.bashrc
echo export PATH="$COIAS_PATH/src6_between_COIAS_and_ReCOIAS:$PATH" >> ~/.bashrc
echo export PATH="$COIAS_PATH/src7_AstsearchR_afterReCOIAS:$PATH" >> ~/.bashrc
echo export PATH="$COIAS_PATH/src8_astsearch_manual:$PATH" >> ~/.bashrc
echo export PYTHONPATH="$COIAS_PATH/COIASlibs:$PYTHONPATH" >> ~/.bashrc
source ~/.bashrc

## Build cython
echo "Building cython..."
cd $COIAS_PATH/src5_astsearch_new
python setup12.py build_ext --inplace

## Compile findOrb
echo "Compling findOrb..."
cd $COIAS_PATH/findOrb

FileList=("dos_find" "lunar.a" "*.o")
for file in $FILEList; do
	[ -e $file ] rm $file
	echo "Removed" $file
done

# If you catch the Error '"curses.h" not found', install package "ncurses-devel" using yum or apt-get.
make -f linlunar.mak
make -f linmake

echo "Finished."

echo "Virtual environment of COIAS is active."
echo "When you run COIAS on another terminal, perform this command initially."
echo "$ source activate coias"
