#!/usr/bin/python
###########################################################################
##  Scripts for NSF model ----------------------------------------------  #
## ---------------------------------------------------------------------  #
##                                                                        #
##  Copyright (c) 2018  National Institute of Informatics                 #
##                                                                        #
##  THE NATIONAL INSTITUTE OF INFORMATICS AND THE CONTRIBUTORS TO THIS    #
##  WORK DISCLAIM ALL WARRANTIES WITH REGARD TO THIS SOFTWARE, INCLUDING  #
##  ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS, IN NO EVENT    #
##  SHALL THE NATIONAL INSTITUTE OF INFORMATICS NOR THE CONTRIBUTORS      #
##  BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY   #
##  DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS,       #
##  WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS        #
##  ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE   #
##  OF THIS SOFTWARE.                                                     #
###########################################################################
##                         Author: Xin Wang                               #
##                         Date:   31 Oct. 2018                           #
##                         Contact: wangxin at nii.ac.jp                  #
###########################################################################

import os
import sys
prjdir = os.getcwd()

# -------------------------------------------------
# --------------- Configuration start --------------
# ---- Swith

# step1: preparing data
step1 = False

#  fine control on step1
#    [generating_data_list, pre_processing_waveforms, generating_time_index,
#     generating_data_nc, calculate_mean_std_of_acoustic_features]
step1s = [False, False, False, False, False]

# step2: network training
step2 = False

# step3: waveform generation
step3 = True

# ---- Data configuration

# (abosolute) path of the directories of acoustic features
#  [path_of_feature_1, path_of_feature_2, ..., path_of_feature_3]
tmp_path = prjdir + '/../DATA'
path_acous_feats = [tmp_path + os.path.sep + 'mfbsp',
                    tmp_path + os.path.sep + 'f0',]

# dimension of acoustic features
dim_acous_feats = [80, 1]

# file name extensions of acoustic features
ext_acous_feats = ['.mfbsp', '.f0']

# which ext denotes F0?
#  if F0 is not included in acoustic features, set f0_ext = None
f0_ext = '.f0'

# waveform sampling rate
wav_samp = 16000

# upsampling rate of acoustic features (waveform sampling rate * acoustic feature frame shift)
#  for example, 80 = 16000 Hz * 5 ms 
upsampling_rate = 80

# (abosolute) path of the directories of waveform
path_waveform = tmp_path + os.path.sep + 'wav32k'

# waveform representation
#  waveform_mu_law_bits = 10: 10 bits mu-law compression (for WaveNet)
#  waveform_mu_law_bits = -1: float-valued waveform (for NSF)
waveform_mu_law_bits = -1


# ----- Network generation configuration

# directory of model for generation
# test_inputDirs: directories of the test data files
if os.getenv('TEMP_WAVEFORM_MODEL_INPUT_DIRS') is None:
    # test data directory (in the same order as path_acous_feats)
    tmp_test_path = prjdir + '/../TESTDATA-for-pretrained'
    path_test_acous_feats = [tmp_test_path + os.path.sep + 'mfbsp',
                             tmp_test_path + os.path.sep + 'f0',]
else:
    tmp_inpput_path = os.getenv('TEMP_WAVEFORM_MODEL_INPUT_DIRS')
    path_test_acous_feats = tmp_inpput_path.split(',')
    if len(path_test_acous_feats) != len(dim_acous_feats):
        raise Exception("Error: invalid path TEMP_WAVEFORM_MODEL_INPUT_DIRS=%s" % (tmp_inpput_path))

if os.getenv('TEMP_WAVEFORM_MODEL_DIRECTORY') is None:
    # specify here if you don't want to use getenv
    gen_model_dir = prjdir + '/MODELS/NSF'
else:
    gen_model_dir = os.getenv('TEMP_WAVEFORM_MODEL_DIRECTORY')

if os.getenv('TEMP_WAVEFORM_MODEL_NETWORK_PATH') is None:
    # specify here if you don't want to use getenv
    # path of the network file
    gen_network_path = gen_model_dir + os.path.sep + '/trained_network.jsn'
else:
    gen_network_path = os.getenv('TEMP_WAVEFORM_MODEL_NETWORK_PATH')

if os.getenv('TEMP_WAVEFORM_OUTPUT_DIRECTORY') is None:
    # output data directory
    gen_output_dir = gen_model_dir + '/output'
else:
    gen_output_dir = os.getenv('TEMP_WAVEFORM_OUTPUT_DIRECTORY')
  
# waveform generation mode
#  for WaveNet only mem_save_mode = 1
#  for NSF, if sentences are short, mem_save_mode can be 0
mem_save_mode = 1

# use CPU to generate waveform?
#  for WaveNet, using CPU is also OK
flag_CPU_gen = 0

if os.getenv('TEMP_ADDITIONAL_COMMAND') is None:             
    # specify here if you don't want to use getenv           
    additiona_command = None                                 
else:                                                        
    additiona_command = os.getenv('TEMP_ADDITIONAL_COMMAND')



# --------------- Configuration done --------------


# ---- Reserved configs (no need to change)
# debug? if True, all commands will be printed out without executing
debug = False

path_pyTools = os.getenv('TEMP_CURRENNT_PROJECT_PYTOOLS_PATH')

# path of CURRENNT
path_currennt = os.getenv('TEMP_CURRENNT_PROJECT_CURRENNT_PATH')

# path of SOX
path_sox = os.getenv('TEMP_CURRENNT_PROJECT_SOX_PATH')

# path of SV56
#  if SV56 is unavailable, set sv56 = None, and normalize the waveform using your own tools
path_sv56 = os.getenv('TEMP_CURRENNT_PROJECT_SV56_PATH')


if path_sv56 is None or path_sox is None or path_currennt is None or path_pyTools is None:
    raise Exception("Please initialize the tool paths by source ../../init.sh")

# path of project scripts
path_scripts = prjdir + '/../SCRIPTS'

# name of the directory to save intermediate data
tmp_data_dir = 'DATATEMP'

# name of the directory to save intermediate data for test set
tmp_test_data_dir = 'TESTDATATEMP'

# name of pre-processed waveform
tmp_wav_pre_dir = 'wav16knorm'

# name of intermediate waveform files for mu-law
tmp_wav_mu_law_dir = 'wav16knorm_mulaw'

# name of intermediate waveform files for float
tmp_wav_float_dir = 'wav16knorm_float'

# name of time index file directory
tmp_idx_dir = 'idxData'

tmp_nc_dir = 'ncData'

tmp_nc_dir_train = 'DATA_TRAIN'

tmp_nc_dir_val = 'DATA_VAL'

tmp_nc_dir_test = 'DATA_TEST'

tmp_name_mean_file = 'meanstd.bin'

tmp_config_name = 'CONFIGS'

tmp_data_nc_config = path_scripts + os.path.sep + tmp_config_name + os.path.sep + 'data_config.py'

tmp_test_data_nc_config = path_scripts + os.path.sep + tmp_config_name + os.path.sep + 'data_config_test.py'

tmp_scp_name = 'scp'

tmp_scp_train_name = 'train.lst'

tmp_scp_val_name = 'val.lst'

tmp_mdn_config_name = 'mdn.config'

tmp_network_trn_log = 'log_train'

tmp_network_trn_err = 'log_err'

path_pyTools_scripts = path_pyTools + '/scripts/utilities-new'

gen_wav_samp = wav_samp

##### check

assert (len(dim_acous_feats)==len(path_acous_feats)), "Error: len(dim_acous_feats)!=len(path_acous_feats)"

assert (len(ext_acous_feats)==len(path_acous_feats)), "Error: len(ext_acous_feats)!=len(path_acous_feats)"
