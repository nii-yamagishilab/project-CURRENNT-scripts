#!/bin/sh




# preparing the training data
python ../SCRIPTS/01_prepare.py config

# training the RNN model
python ../SCRIPTS/02_train.py config

