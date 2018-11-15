#!/bin/sh

# generating
cd MODELS
if [ ! -e "./NSF" ];then
    tar -xzvf models.tar.gz
fi

cd ../
python ../SCRIPTS/02_genwaveform.py config
