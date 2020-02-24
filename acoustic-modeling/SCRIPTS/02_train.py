#!/usr/bin/python
###########################################################################
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
from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import random
import importlib

""" ----- Prepare data.nc files for CURRENNT -----
"""

sys.path.append(os.getcwd())
try:
    cfg = importlib.import_module(sys.argv[1])
except IndexError:
    print("Error: missing argument. Usage: python **.py CONFIG_NAME")
    sys.exit(1)
except ImportError:
    print("Error: cannot load library: ", sys.argv[1])
    sys.exit(1)
sys.path.append(cfg.path_pyTools)
from pyTools import display
from ioTools import readwrite
import subprocess

try:
    
    networkToolPath = os.path.join(cfg.path_pyTools_scripts, 'networkTool')
    sys.path.append(networkToolPath)
    networkTool = importlib.import_module('netCreate')
except ImportError:
    print("Cannot load %s" % networkToolPath)
    
def exe_cmd(cmd, debug=False):
    display.self_print("Execute command:", 'ok')
    display.self_print(cmd + '\n', 'highlight')
    if not debug:
        try:
            subprocess.check_call(cmd, shell=True)
            display.self_print("Command is successfully executed:\n%s\n\n" % (cmd), 'ok')
        except subprocess.CalledProcessError as e:
            display.self_print("Failed to run:" + cmd, 'error')
            display.self_print("Please check the printed error message", 'error')
            display.self_print("Process terminated with %s" % (e.returncode), 'error')
            sys.exit(1)
                        


def prepareCURRENNT(modelDir):
    """ Generating config.cfg in the model directory
    """
    try:
        os.mkdir(modelDir)
    except OSError:
        pass


    ## modify the network file
    network = cfg.network
    if cfg.mdnConfig:
        mdnConfigPath = modelDir + os.path.sep + cfg.nnMDNConfigName
    else:
        mdnConfigPath = None

    try:
        networkTool.modifyNetworkFile(cfg.network, sum(cfg.inputDim), sum(cfg.outputDim),
                                      cfg.mdnConfig, network, mdnConfigPath)
    except Exception as e:
        print("Fail to parse %s" % (cfg.network))
        print(e)
        sys.exit(1)


    ## find the necessary input/output data
    dataDir    = cfg.nnDataDirName
    trainNcDir = dataDir + os.path.sep + cfg.trainSet
    valNcDir   = dataDir + os.path.sep + cfg.valSet
    #linkDataDir= dataDir + os.path.sep + cfg.linkDirname

    linkDataDirInput = dataDir + os.path.sep + cfg.linkDirname_input
    linkDataDirOutput = dataDir + os.path.sep + cfg.linkDirname_output
    
    trainFileList = [trainNcDir + os.path.sep + fileName for fileName in os.listdir(trainNcDir) if fileName.startswith(cfg.nnDataNcPreFix)]
    valFileList   = [valNcDir + os.path.sep + fileName for fileName in os.listdir(valNcDir) if fileName.startswith(cfg.nnDataNcPreFix)]

    if os.path.isdir(linkDataDirInput) or os.path.islink(linkDataDirInput):
        inputDirs = ','.join([linkDataDirInput for x in range(len(cfg.inputDim))])
    else:
        inputDirs = ','.join(cfg.inputDirs[0])
    inputDims     = '_'.join([str(x) for x in cfg.inputDim])
    inputExts     = ','.join(['.' +x for x in cfg.inputExt])

    if os.path.isdir(linkDataDirOutput) or os.path.islink(linkDataDirOutput):
        outputDirs    = ','.join([linkDataDirOutput for x in range(len(cfg.outputDim))])
    else:
        outputDirs    = ','.join(cfg.outputDirs[0])
    outputDims    = '_'.join([str(x) for x in cfg.outputDim])
    outputExts    = ','.join(['.' +x for x in cfg.outputExt])

    inputMV       = dataDir + os.path.sep + cfg.computMeanStdOn + os.path.sep +  cfg.nnDataInputMV
    outputMV      = dataDir + os.path.sep + cfg.computMeanStdOn + os.path.sep +  cfg.nnDataOutputMV

    
    ## create the config.cfg for CURRENNT
    config = modelDir + os.path.sep  + cfg.nnModelCfgname
    exe_cmd('cp %s %s' % (cfg.trainCfg, config), cfg.debug)

    filePtr = open(config, 'a')
    filePtr.write('\n')
    if trainFileList:
        filePtr.write('train_file = %s\n' % (','.join(trainFileList)))
    if valFileList:
        filePtr.write('val_file = %s\n' % (','.join(valFileList)))
    filePtr.write('ExtInputDirs = %s \n' % (inputDirs))
    filePtr.write('ExtInputExts = %s \n' % (inputExts))
    filePtr.write('ExtInputDims = %s \n' % (inputDims))
    filePtr.write('ExtOutputDirs = %s \n' % (outputDirs))
    filePtr.write('ExtOutputExts = %s \n' % (outputExts))
    filePtr.write('ExtOutputDims = %s \n' % (outputDims))
    filePtr.write('target_data_ms = %s \n' % (outputMV))
    filePtr.write('source_data_ms = %s \n' % (inputMV))
    if mdnConfigPath is not None:
        filePtr.write('mdn_config = %s \n' % (mdnConfigPath))
        filePtr.write('tieVariance = false \n')
    if cfg.initialModel is not None:
        assert os.path.isfile(cfg.initialModel), "Cannot find %s" % (cfg.initialModel)
        filePtr.write('trainedModel = %s \n' % (cfg.initialModel))
        if cfg.initialModelWhichLayers is not None:
            filePtr.write('trainedModelCtr = %s \n' % (cfg.initialModelWhichLayers))
    if hasattr(cfg, 'sarOrder'):
        assert hasattr(cfg, 'sarConfig'), "Fail to found sarConfig"
        filePtr.write('AROrder = %s \n' % ('_',join([str(int(x)) in cfg.sarOrder])))
        filePtr.write('ARConfig = %s \n' % ('_',join([str(int(x)) in cfg.sarConfig])))
        filePtr.write('wInitPara = 20 \n')
        filePtr.write('varInitPara = 0.001 \n')
        
    filePtr.close()


def trainCURRENNT(model_dir):
    
    os.chdir(model_dir)
    display.self_print('******** train config ******\n', 'highlight')
    os.system("cat ./%s" % (cfg.nnModelCfgname))
    display.self_print('****************************\n', 'highlight')
    
    runCmd = '%s --options_file %s --verbose 1' % (cfg.path_currennt, cfg.nnModelCfgname)
    runCmd = runCmd + ' >%s 2>%s' % (cfg.tmp_network_trn_log, cfg.tmp_network_trn_err)
    
    display.self_print("GPU job submitted. Please wait until terminated.", 'ok')
    display.self_print("Please open another terminal to check nvidia-smi", 'ok')
            
    display.self_print("Also check %s" % (os.path.join(model_dir, cfg.tmp_network_trn_log)), 'ok')
    display.self_print("Also check %s" % (os.path.join(model_dir, cfg.tmp_network_trn_err)), 'ok')
    exe_cmd(runCmd, cfg.debug)
    display.self_print_with_date('Processed terminated. Please check %s %s' % (os.path.join(model_dir, cfg.tmp_network_trn_log), os.path.join(model_dir, cfg.tmp_network_trn_err)), 'ok')
    
if __name__ == '__main__':

    if cfg.step02:
        display.self_print_with_date('Step2. network training', 'h')

        if not os.path.isdir(cfg.model_dir):
            raise Exception("Error: cannot find %s" % (cfg.model_dir))
        
        if cfg.step02train_CFG:
            prepareCURRENNT(cfg.model_dir)

        if cfg.step02train_TRAIN:
            trainCURRENNT(cfg.model_dir)
    else:
        display.self_print_with_date('skip step2(network training)', 'h')

