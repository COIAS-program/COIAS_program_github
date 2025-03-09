#!/bin/bash

## This script is to set the environment to run COIAS programs ##
## Last modified: 2022.1.12 N.Maeda=> 2025.3.9  S.Urakawa

## Usage 
## (Prepare) Install Anaconda on your environment
## Execute the following command on your terminal:
## $ bash env_setting.sh

## create a virtual environment
echo "create a virtual environment for COIAS"
conda create -n coias25py311 python=3.11
conda activate coias

## install the packages for coias
conda install -y astropy
conda install -y matplotlib
conda install -y scipy
#conda install -y -c astropy astroquery==0.4.4
conda install -y -c astropy photutils
conda install -y ephem
conda install -y cython
conda install -y pandas
conda install -y bokeh
conda install -y -c conda-forge astromatic-source-extractor
conda install -c anaconda beautifulsoup4
conda install -c anaconda lxml

pip install --upgrade pip
pip install  julian
pip install  astroquery

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
echo "$ conda activate coias25py311"
