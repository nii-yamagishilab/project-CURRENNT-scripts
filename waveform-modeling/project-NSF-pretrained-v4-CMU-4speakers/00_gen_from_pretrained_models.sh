#!/bin/sh
# script to download pre-trained model and generate samples
# Usage:
#  $: sh 00_gen_from_pretrained_models.sh
# Note:
#  Acoustic features used by this pre-trained models are
#  extracted using scripts in ../TESTDATA-for-pretrained-v4-CMU-4speakers

MODELLINK=https://www.dropbox.com/sh/bua2vks8clnl2ha/AAB_y4I7W44rzt-D8EUKrthaa/project-NSF-pretrained-v4-CMU-4speakers.tar.gz
DATALINK=https://www.dropbox.com/sh/bua2vks8clnl2ha/AACHErNHFeJ8T83blpXVIkyQa/TESTDATA-for-pretrained-v4-CMU-4speakers.tar.gz

if [ ! -e "./MODELS" ];then
    wget ${MODELLINK}

    if [ -e "./project-NSF-pretrained-v4-CMU-4speakers.tar.gz" ];then	
	tar -xzvf project-NSF-pretrained-v4-CMU-4speakers.tar.gz
	rm project-NSF-pretrained-v4-CMU-4speakers.tar.gz
    else
	echo "Cannot download the pre-trained models. Please contact the author"
    fi
fi

if [ ! -e "../TESTDATA-for-pretrained-v4-CMU-4speakers" ];then
    wget ${DATALINK}

    if [ -e "./TESTDATA-for-pretrained-v4-CMU-4speakers.tar.gz" ];then	
	tar -xzvf TESTDATA-for-pretrained-v4-CMU-4speakers.tar.gz
	mv TESTDATA-for-pretrained-v4-CMU-4speakers ../
	rm TESTDATA-for-pretrained-v4-CMU-4speakers.tar.gz
    else
	echo "Cannot download the data. Please contact the author"
    fi
fi


if [ -e "./MODELS" -a -e "../TESTDATA-for-pretrained-v4-CMU-4speakers"  ]; then
    bash 01_gen.sh
else
    echo "Cannot find the models or data for generation"
fi
    
