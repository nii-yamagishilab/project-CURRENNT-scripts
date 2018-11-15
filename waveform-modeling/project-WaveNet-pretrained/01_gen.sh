#!/bin/sh

# generating
cd MODELS/wavenet001
tar -xzvf trained_network.jsn.tar.gz
cd ../../
python ../SCRIPTS/02_genwaveform.py config
