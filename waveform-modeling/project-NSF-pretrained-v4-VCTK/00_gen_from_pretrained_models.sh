#!/bin/sh
# script to download pre-trained model and generate samples
# Usage:
#  $: sh 00_gen_from_pretrained_models.sh
# Note:
#  Acoustic features used by this pre-trained models are
#  extracted using scripts in ../TESTDATA-for-pretrained-v4-VCTK
#  

MODELLINK=https://www.dropbox.com/sh/bua2vks8clnl2ha/AAAu6_XsxI7FQ7MG_2UgfDvCa/project-NSF-pretrained-v4-VCTK.tar.gz
DATALINK=https://www.dropbox.com/sh/bua2vks8clnl2ha/AADFKHaHZDtScqiiL0ukxE4pa/TESTDATA-for-pretrained-v4-VCTK.tar.gz


TARNAME=project-NSF-pretrained-v4-VCTK.tar.gz
TESTDIR=TESTDATA-for-pretrained-v4-VCTK
if [ ! -e "./MODELS" ];then
    wget ${MODELLINK}

    if [ -e "./${TARNAME}" ];then	
	tar -xzvf ${TARNAME}
	rm ${TARNAME}
    else
	echo "Cannot download the pre-trained models. Please contact the author"
    fi
fi

if [ ! -e "../${TESTDIR}" ];then
    wget ${DATALINK}

    if [ -e "./${TESTDIR}.tar.gz" ];then	
	tar -xzvf ${TESTDIR}.tar.gz
	mv ${TESTDIR} ../
	rm ${TESTDIR}.tar.gz
    else
	echo "Cannot download the data. Please contact the author"
    fi
fi


if [ -e "./MODELS" -a -e "../${TESTDIR}"  ]; then
    bash 01_gen_unseen.sh
else
    echo "Cannot find the models or data for generation"
fi
    
