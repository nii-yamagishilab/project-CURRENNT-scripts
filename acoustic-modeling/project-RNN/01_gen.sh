#!/bin/sh


# --------
# Method 1: configure config and run
#python ../SCRIPTS/03_syn.py config


# -------
# Method 2: set system environment variables  and run
#  this may be more convenient

# input feature directories
export TEMP_ACOUSTIC_MODEL_INPUT_DIRS=/work/smg/wang/TEMP/tmp/DATA/lab_bin,/work/smg/wang/DATA/speech/VCTK68/temp_test/onehot/
# model directory
export TEMP_ACOUSTIC_MODEL_DIRECTORY=$PWD/MODELS/RNN_001
# network file
export TEMP_ACOUSTIC_NETWORK_PATH=$PWD/MODELS/RNN_001/trained_network.jsn
# directory to save output waveforms
export TEMP_ACOUSTIC_OUTPUT_DIRECTORY=./tmp_out
# directory to save intermediate files
export TEMP_ACOUSTIC_TEMP_OUTPUT_DIRECTORY=./tmp_int_out

python ../SCRIPTS/03_syn.py config
rm -r ${TEMP_ACOUSTIC_TEMP_OUTPUT_DIRECTORY}
