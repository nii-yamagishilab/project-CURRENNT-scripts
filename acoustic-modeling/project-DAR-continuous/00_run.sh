#!/bin/sh

# preparing data
python ../SCRIPTS/01_prepare.py config
status=$?
if [ $status -eq 0 ]; then

    # model training
    python ../SCRIPTS/02_train.py config

fi
