#!/bin/sh

# Generating
cd MODELS/wavenet001
tar -xzvf trained_network.jsn.tar.gz


cd ../../
# Configuration has been written into config.py
python ../SCRIPTS/02_genwaveform.py config
