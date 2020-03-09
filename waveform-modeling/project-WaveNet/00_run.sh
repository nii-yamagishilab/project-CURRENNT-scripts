#!/bin/sh
#$ -cwd
#$ -l q_node=1
#$ -l h_rt=24:00:00

. /etc/profile.d/modules.sh
module load cuda/10.0.130
module load python-extension

# PATH to the pyTools
export TEMP_CURRENNT_PROJECT_PYTOOLS_PATH=/gs/hs0/tgh-19IAA/wang/CODE/project-CURRENNT-public/pyTools

# PATH to currennt
export TEMP_CURRENNT_PROJECT_CURRENNT_PATH=/gs/hs0/tgh-19IAA/wang/CODE/project-CURRENNT-public/CURRENNT_codes/build/currennt

# PATH to SOX (http://sox.sourceforge.net/sox.html)
export TEMP_CURRENNT_PROJECT_SOX_PATH=/gs/hs0/tgh-19IAA/wang/CODE/bin/sox

# PATH to SV56 (a software to normalize waveform amplitude.
#  https://www.itu.int/rec/T-REC-P.56 (document)
#  https://www.itu.int/rec/T-REC-G.191-201901-I/en (code)
#  This software is not necessary, I used it because it is available in our lab.
#  You can use other tools to normalize the waveforms before put them into this project.
#  Then, you can set TEMP_CURRENNT_PROJECT_SV56_PATH=None)
export TEMP_CURRENNT_PROJECT_SV56_PATH=None

# Add pyTools to PYTHONPATH
export PYTHONPATH=${PYTHONPATH}:${TEMP_CURRENNT_PROJECT_PYTOOLS_PATH}

CONFIG=config

# preparing data
python ../SCRIPTS/00_prepare_data.py ${CONFIG}
status=$?
if [ $status -eq 0 ]; then

    # model training
    python ../SCRIPTS/01_train_network.py ${CONFIG}
fi
