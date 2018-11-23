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

# ------------- Swith -------------
# step01: preparing data
step01 = True
#  fine controls on each step (by default, conduct all steps)
#  step01.1 creat symbolic link to the input/output files
step01Prepare_LINK = step01
#  step01.2 create frame index 
step01Prepare_IDX  = step01
#  step01.3 package the data.nc
step01Prepare_PACK = step01
#  step01.4 calculate mean and std
step01Prepare_MV   = step01


# step02. create config.cfg for training
step02 = True
#  fine controls on each step (by default, conduct all steps)
#  step02.1 create configuration.cfg and networks.jsn
step02train_CFG    = step02
#  step02.2 train network
step02train_TRAIN  = step02


# step03. generate from network
step03 = True
#  fine controls on each step
#  step03.1: prepare test data 
step03Prepare_DATA = step03
#  step03.2: generate from network
step03NNGen = step03
#  step03.3: waveform generation
step03WaveFormGen = step03


# ------------ Data configuration ------------

# -- input feature configuration
# inputDirs: absolute path of directories of input features.
#   Unput features may have multiple types of features, e.g., label-vector, speaker-id.
#   Please specify the features directories in this way:

#            [[training_set-input-feature-1,   training_set-input-feature-2, ..., ]
#             [validation_set-input-feature-1, valiadtion_set-input-feature-2, ..., ]]

#   Note: for one utterance, its input and output features should have the roughtly the
#   same number of frames. For example, if one utterance has N frames, the speaker-id
#   feature file should also contain N frames, where every frame has the same speaker-id.

tmpDir  = os.path.join(prjdir, '../DATA')
inputDirs = [[tmpDir + '/lab_train', tmpDir + '/spk_train'],
             [tmpDir + '/lab_val',   tmpDir + '/spk_val']]

# inputDim: dimensions of each type of input features
#   len(inputDim) should be equal to len(inputDirs[0])
inputDim  = [367, 69]

# inputExt: file name extension of input features
#   len(inputExt) should be equal to len(inputDirs[0])
inputExt  = ['.lab', '.bin']

# normMask: which dimension should NOT be normalized?
#  len(inputNormMask) should be = len(inputDim)
#  for each inputNormMask[n]:
#    [start_dim, end_dim]: don't norm from dimension start_dim to end_dim
#    ['not_norm']: don't norm all dimensions
#    []: default (norm all the dimensions)
#  
#  for example, [[], ['not_norm']] will normalize *.lab, but not *.bin
inputNormMask = [[], ['not_norm']]


# -- output feature configuration
tmpDir  = os.path.join(prjdir, '../DATA')
outputDirs= [[tmpDir + '/mgc_train', tmpDir + '/lf0_train', tmpDir + '/vuv_train', tmpDir + '/bap_train'],
             [tmpDir + '/mgc_val', tmpDir + '/lf0_val', tmpDir + '/vuv_val', tmpDir + '/bap_val']]
outputDim = [180, 3, 1, 75]
outputExt = ['.mgc', '.lf0', '.vuv', '.bap']
# normalize all the output features
outputNormMask = [[], [], [], []]

#  Whether each output feature has delta / delta-delta component(s):
#   3: has static, delta-delta and delta
#   2: has static, delta
#   1: has static
#  For example [3, 3, 1, 3] says that all the output mgc, lf0, and bap features contain
#  the static, delta, and delta-delta components. But vuv only has static component
outputDelta = [3, 3, 1, 3]

# -- when output features contain F0
#  If F0 is not in the output features, set lf0UV = False, lf02f0 = False
#  
#  Whether conver generated interpolated 'F0' into un-interpolated 'F0'?
lf0UV = True
#  extension of log-liear f0
lf0ext = '.lf0'
#  extension of vuv
vuvext = '.vuv'

# Whether Convert generated F0 to linear domain?
lf02f0 = True
#  extension of linear f0
f0ext = '.f0'


# ---- data division
# dataDivision: name of each data division
#               inputDirs[0] + outputDirs[0] will be called the 'train' set
#               inputDirs[1] + outputDirs[1] will be called the 'val' set
dataDivision = ['train', 'val']

# trainSet: which data division is used as the training set?
trainSet        = dataDivision[0]
# valSet:   which data division is used as the validation set?
valSet          = dataDivision[1]

# computMeanStdOn: on which data division the mean and std of input/output features are calculated?
#  By default, mean/std will be computed over the trainining set
computMeanStdOn = trainSet


# ------------ Model  configuration ------------
# path to the model directory
model_dir = os.path.join(prjdir, 'MODELS', 'RNN_001')

# path to the network file
network = os.path.join(model_dir, 'network.jsn')

# path to the network training configuration file
#  Please configure it beforehand if necessary
trainCfg = os.path.join(prjdir, 'train_config.cfg')

# configuration for the MDN layer (no need for RNN model)
mdnConfig    = []
initialModel = None
initialModelWhichLayers = None


# ------------ Generation configuration ------------

# test_inputDirs: directories of the test data files
tmpDir  = os.path.join(prjdir, '../TESTDATA')
test_inputDirs = [[tmpDir + '/lab_test', tmpDir + '/spk_test']]

# test_dataDivision: a temporary name to the test set
test_dataDivision = ['testset_1']

# outputUttNum: how many utterances in test_inputDirs should be synthesized?
#  This is used for quick generation and debugging
#  By default -1, all the test files in test_inputDirs will be synthesized
outputUttNum = -1

# test_modelDir: directory of the trained model
test_modelDir = model_dir
# test_network: path of the trained network.
#  You can also use *.autosave from any epoch rather than the final trained_network.jsn
test_network = os.path.join(test_modelDir, 'trained_network.jsn')

# outputDir: directory to store generated acoustic features
outputDir = os.path.join(test_modelDir, 'output_trained')

# If MDN is used, choose the standard deviation of the noise for random sampling
#  0.0  -> mean-based generation
#  >0.0 -> sampling with the std of the noise distribution
#  -1.0 -> output the parameter set of the distribution
mdnSamplingNoiceStd = 0.00000

# nnCurrenntGenCommand: any other CURRENNT arguments for generation
#  If none, comment this out
# nnCurrenntGenCommand = None

# ----------- Waveform generation configuration ---------
# Other options for waveform generations.
#  Set step03WaveFormGen=False, if you use your own script for waveform generation
# 
# mlpgFlag: flags to use MLPG on each output features
#  len(mlpgFlag) should = len(outputDim)
#  MLPG can only be used on output features who outputDelta is 3
mlpgFlag = [1, 1, 0, 1]

# if mlpgFlag is 1, please specify the window and std for mlpg (HTS/data/var)
mlpgVar  = '/work/smg/wang/PROJ/PROJS/VCTK/VCTK68/HMM/HTS-NN-training/scripts/nndata'

# wavPostFilter: parameter to enhance formant through post-filtering
wavPostFilter = 0.8

# which waveform generator to be used? 'WORLD' or 'STRAIGHT'?
wavformGenerator = 'WORLD'


# --------------- Configuration start done --------------
# -------------------------------------------------

# Reserved configuration (no need to modify) 
debug = False

# path of pyTools
path_pyTools = os.getenv('TEMP_WAVEFORM_PROJECT_PYTOOLS_PATH')
# path of CURRENNT
path_currennt = os.getenv('TEMP_WAVEFORM_PROJECT_CURRENNT_PATH')
if path_currennt is None or path_pyTools is None:
    raise Exception("Please initialize the tool paths by source ../../init.sh")
# path of project scripts
path_scripts = prjdir + '/../SCRIPTS'
path_pyTools_scripts = path_pyTools + '/scripts/utilities-new'
#
nnDataDirName  = os.path.join(prjdir,'DATATEMP')
nnDataDirNameTrain = nnDataDirName
nnDataDirNameTest  = nnDataDirName + '_test'

idxDirName    = 'idxFiles'
idxFileName   = 'idx'
nnDataNcPreFix= 'data.nc'
linkDirname   = 'link'

nnDataInputMV='input_meanstd.bin'
nnDataOutputMV='output_meanstd.bin'
nnModelCfgname= 'config.cfg'
nnMDNConfigName='mdn.config'
#
fileNameInEachNCPack = 3000
tmp_network_trn_log = 'log_train'
tmp_network_trn_err = 'log_err'

wavGenWorldRequire    = ['mgc', 'bap', 'lf0']
wavGenStraightRequire = ['mgc', 'bap', 'lf0']


# External U/V data can be used if lf0UV = 1
#   directory of the external U/V data 
lf0UVExternalDir = None
#  extension of output vuv (for example, vuv)
lf0UVExternalExt = None
#  F0[t] is unvoiced if filename.lf0UVExternalExt[t] < lf0UVExternalThreshold
lf0UVExternalThre = None

#
test_outputDirs  = [[] for x in test_inputDirs]

synCfg = path_scripts + '/commonConfig/syn.cfg'
splitConfig  = 'data_split.py'

assert len(inputDirs) == len(dataDivision), "len(inputDirs != len(dataDivision))"
assert len(outputDirs)== len(dataDivision), "len(outputDirs != len(dataDivision))"
assert len(test_inputDirs)== len(test_dataDivision), "len(test_inputDirs != len(test_dataDivision))"
assert len(inputDim) == len(inputExt), "len(inputDim) != len(inputExt)"
assert len(inputDim) == len(inputNormMask), "len(inputDim) != len(inputNormMask)"
assert len(outputDim) == len(outputExt), "len(outputDim) != len(outputExt)"
assert len(outputDim) == len(outputNormMask), "len(outputputDim) != len(outputNormMask)"
assert len(outputDim) == len(outputDelta), "len(outputputDim) != len(outputDelta)"

#
inputExt = [x.lstrip('.') for x in inputExt if x.startswith('.')]
outputExt = [x.lstrip('.') for x in outputExt if x.startswith('.')]

if not len(list(set(inputExt))) == len(inputExt):
    print("Some Input features use the same name extensions.")
    raise Exception("Please modify the input file name extensions and inputExt")

if not len(list(set(outputExt))) == len(outputExt):
    print("Some Output features use the same name extensions.")
    raise Exception("Please modify the output file name extensions and outputExt")
