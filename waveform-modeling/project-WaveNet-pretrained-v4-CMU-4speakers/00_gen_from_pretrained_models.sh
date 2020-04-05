#!/bin/sh

MODELLINK=https://www.dropbox.com/sh/bua2vks8clnl2ha/AAAmv4JIIGV1w7ePcnomjB4ba/project-WaveNet-pretrained-v4-CMU-4speakers.tar.gz

DATALINK=https://www.dropbox.com/sh/bua2vks8clnl2ha/AACHErNHFeJ8T83blpXVIkyQa/TESTDATA-for-pretrained-v4-CMU-4speakers.tar.gz

if [ ! -e "./MODELS" ];then
    wget ${MODELLINK}

    if [ -e "./project-WaveNet-pretrained-v4-CMU-4speakers.tar.gz" ];then	
	tar -xzvf project-WaveNet-pretrained-v4-CMU-4speakers.tar.gz
	rm project-WaveNet-pretrained-v4-CMU-4speakers.tar.gz
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
    
