#!/bin/sh


export PYTHONPATH=/home/smg/wang/WORK/CODE/GIT/pyTools:$PYTHONPATH

# Please configure ***_train.py and ***_syn.py before hand

# ***_train.py: configuration for training and data prepration

# ***_syn.py:  configuration for feature and waveform generation


# preparing the training data
python 01_prepare.py networkConfig_RNN/RNN_001_train.py

# training the RNN model
python 02_train.py networkConfig_RNN/RNN_001_train.py

# synthesis, using the configuration in synconfig.py
#python 03_syn.py networkConfig_RNN/RNN_001_syn.py

# training the RMDN model
#python 02_train.py networkConfig_RMDN/RMDN_001_train.py

# synthesis, using the configuration in synconfig.py
#python 03_syn.py networkConfig_RMDN/RMDN_001_syn.py

# training the SAR model
#python 02_train.py networkConfig_SAR/SAR_001_train.py

# synthesis, using the configuration in synconfig.py
#python 03_syn.py networkConfig_SAR/SAR_001_syn.py
