#!/bin/sh
# Copied from init.sh
export TEMP_CURRENNT_PROJECT_PYTOOLS_PATH=/work/smg/wang/GIT/TEAM/project-CURRENNT-public/pyTools/
export TEMP_CURRENNT_PROJECT_CURRENNT_PATH=/work/smg/wang/GIT/TEAM/project-CURRENNT-public/CURRENNT_codes/build/currennt
export PYTHONPATH=${PYTHONPATH}:${TEMP_CURRENNT_PROJECT_PYTOOLS_PATH}
export TEMP_CURRENNT_PROJECT_SOX_PATH=None
export TEMP_CURRENNT_PROJECT_SV56_PATH=None

# ----- Method 1 
# For generation, you can configure config.py and run
python ../SCRIPTS/02_genwaveform.py config

# ----- Method 2
# Equivalently, you can set the environment variables below
#  rather than manually changing config.py

# input feature directory (equivalent to path_test_acous_feats in config.py)
export TEMP_WAVEFORM_MODEL_INPUT_DIRS=$PWD/../TESTDATA-for-pretrained/mfbsp,$PWD/../TESTDATA-for-pretrained/f0
# equivalent to gen_model_dir in config.py
export TEMP_WAVEFORM_MODEL_DIRECTORY=$PWD/MODELS/NSF
# output directory for generated waveforms (equivalent to gen_output_dir in config.py)
export TEMP_WAVEFORM_OUTPUT_DIRECTORY=$PWD/MODELS/NSF/output_trained
# equivalent to gen_network_path in config.py
export TEMP_WAVEFORM_MODEL_NETWORK_PATH=$PWD/MODELS/NSF/trained_network.jsn
# a temporary directory to save intermediate files (which will be deleted after generation)
export TEMP_WAVEFORM_TEMP_OUTPUT_DIRECTORY=$PWD/MODELS/NSF/output_trained_tmp

# generating
python ../SCRIPTS/02_genwaveform.py config

rm -r ${TEMP_WAVEFORM_TEMP_OUTPUT_DIRECTORY}


