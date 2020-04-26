#!/bin/sh

MODELLINK=https://www.dropbox.com/sh/bua2vks8clnl2ha/AADJ5RI5xc-vlRxEmwqpS0Hma/project-WaveNet-pretrained-v4-VCTK.tar.gz
DATALINK=https://www.dropbox.com/sh/bua2vks8clnl2ha/AADFKHaHZDtScqiiL0ukxE4pa/TESTDATA-for-pretrained-v4-VCTK.tar.gz


TARNAME=project-WaveNet-pretrained-v4-VCTK.tar.gz
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
    
