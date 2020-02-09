#!/bin/sh

# Directories of the input features, which are separated by ','
export TEMP_WAVEFORM_MODEL_INPUT_DIRS=$PWD/../TESTDATA-for-pretrained/mfbsp,$PWD/../TESTDATA-for-pretrained/f0

# Path to the model directory
export TEMP_WAVEFORM_MODEL_DIRECTORY=$PWD/MODELS/h-sinc-NSF

# Path to the directory that will save the generated waveforms
export TEMP_WAVEFORM_OUTPUT_DIRECTORY=${TEMP_WAVEFORM_MODEL_DIRECTORY}/output_trained

# Path to the trained_network.jsn (or epoch*.autosave)
export TEMP_WAVEFORM_MODEL_NETWORK_PATH=${TEMP_WAVEFORM_MODEL_DIRECTORY}/trained_network.jsn

# Path to a temporary directory to save intermediate files (which will be deleted after generation)
export TEMP_WAVEFORM_TEMP_OUTPUT_DIRECTORY=${TEMP_WAVEFORM_MODEL_DIRECTORY}/output_trained_tmp

# generating
python ../SCRIPTS/02_genwaveform.py config

rm -r ${TEMP_WAVEFORM_TEMP_OUTPUT_DIRECTORY}


