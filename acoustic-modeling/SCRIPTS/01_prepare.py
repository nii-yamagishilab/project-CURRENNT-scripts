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
import numpy as np
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
    meanStdToolPath = os.path.join(cfg.path_pyTools_scripts, 'dataProcess')
    sys.path.append(meanStdToolPath)
    meanStdTool = importlib.import_module('meanStd')
except ImportError:
    print("Cannot load %s" % meanStdToolPath)
    
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
                        
def crossSet(list1, list2):
    """ return the cross-set of list1 and list2
    """
    return list(set(list1).intersection(list2)), list(set(list1).symmetric_difference(list2))

def listSameContent(list1):
    if len(list1) == 1:
        return True
    else:
        temp = list1[0]
        for ele in list1[1:]:
            if temp != ele:
                return False
        return True

def writeDataConfig(filePath, idxScpName, fileNumInEachNCPack):
    filePtr = open(filePath, 'w')
    filePtr.write("#!/usr/bin/python\n")
    filePtr.write("import numpy as np\n")
    filePtr.write("dataType = np.float32\n")
    filePtr.write("flushThreshold = %d\n" % (fileNumInEachNCPack))
    filePtr.write("inDim = [1,]\n")
    filePtr.write("outDim = [1,]\n")
    filePtr.write("inScpFile = ['%s',]\n" % (idxScpName))
    filePtr.write("outScpFile = ['%s',]\n" % (idxScpName))
    filePtr.write("normMask = [[0], [0]]\n")
    filePtr.write("allScp = 'all.scp'\n")
    filePtr.close()
    


def prepareData():
    """ prepreData: 
        1. create the file list
        2. create the symbolic link to the feature data
        3. create the index file (used by CURRENNT)
        4. create package data of index file (data.nc)
        5. calculate the mean and std for a specific data set
    """
    # create directories
    dataDir = cfg.nnDataDirName
    try:
        os.mkdir(dataDir)
    except OSError:
        pass

    dataListPath = dataDir + os.path.sep + 'lists'
    try:
        os.mkdir(dataListPath)
    except OSError:
        pass
    
    dataRawDir = dataDir + os.path.sep + cfg.idxDirName
    try:
        os.mkdir(dataRawDir)
    except OSError:
        pass


    # decide whether create the symbolic link to each file
    if len(cfg.inputDirs) == 1 and len(cfg.outputDirs) == 1:
        # no validation set
        flagFileUseSymbolLink = False
    elif listSameContent(cfg.inputDirs) and listSameContent(cfg.outputDirs):
        # all data have been in the same directory
        flagFileUseSymbolLink = False
    else:
        flagFileUseSymbolLink = True

        
    #dataLinkDir = dataDir + os.path.sep + cfg.linkDirname
    dataLinkDirInput = dataDir + os.path.sep + cfg.linkDirname_input
    dataLinkDirOutput = dataDir + os.path.sep + cfg.linkDirname_output    
    # prepare for data link
    if flagFileUseSymbolLink:
        try:
            os.mkdir(dataLinkDirInput)
            os.mkdir(dataLinkDirOutput)
        except OSError:
            pass
    else:
        if os.path.islink(dataLinkDirInput):
            os.system("rm %s" % (dataLinkDirInput))
        if os.path.isdir(dataLinkDirInput):
            os.system("rm -r %s" % (dataLinkDirInput))
        if os.path.islink(dataLinkDirOutput):
            os.system("rm %s" % (dataLinkDirOutput))
        if os.path.isdir(dataLinkDirOutput):
            os.system("rm -r %s" % (dataLinkDirOutput))    
            
        #os.system("ln -s %s %s" % (cfg.inputDirs[0][0], dataLinkDirInput))
        #os.system("ln -s %s %s" % (cfg.outputDirs[0][0], dataLinkDirOutput))

    
    # create file list
    for dataList, inputDirSet, outputDirSet, dataPart in zip(cfg.dataLists, cfg.inputDirs, cfg.outputDirs, cfg.dataDivision):

        display.self_print('Processing ' + dataPart + ' data', 'highlight')

        if dataList is None:
            # get the cross-set of file list
            listInput  = readwrite.list_file_name_in_dir(inputDirSet[0])
            listOutput = readwrite.list_file_name_in_dir(outputDirSet[0])
            fileList   = listInput
            if inputDirSet:
                for inputDir in inputDirSet:
                    listInput2  = readwrite.list_file_name_in_dir(inputDir)
                    fileList, diffSet  = crossSet(fileList, listInput2)
                    tmpName = os.path.join(dataListPath, dataPart+os.path.basename(inputDir)+'.dif.lst')
                    readwrite.write_txt_list(diffSet, tmpName)
                
            if outputDirSet:
                for outputDir in outputDirSet:
                    listOutput2  = readwrite.list_file_name_in_dir(outputDir)
                    fileList, diffSet = crossSet(fileList, listOutput2)
                    tmpName = os.path.join(dataListPath, dataPart+os.path.basename(outputDir)+'.dif.lst')
                    readwrite.write_txt_list(diffSet,tmpName)
        
            # writing the list of file name
            random.seed(1234567)
            random.shuffle(fileList)
            fileListFilePath = dataListPath + os.path.sep + dataPart + '.lst'
            readwrite.write_txt_list(fileList, fileListFilePath)
        else:
            fileListFilePath = dataListPath + os.path.sep + dataPart + '.lst'
            os.system("cp %s %s" % (dataList, fileListFilePath))
            fileList = readwrite.read_txt_list(fileListFilePath)

        # before start, take a simple test on the configuration of feature dimension
        frameNum = None
        # get the maximum number of frame
        for inputDir, featDim, featName in zip(inputDirSet, cfg.inputDim, cfg.inputExt):
            inputFile = os.path.join(inputDir, fileList[0]) + '.' + featName
            if os.path.isfile(inputFile):
                tmpframeNum = readwrite.read_raw_mat(inputFile, featDim).shape[0]
                if frameNum is None:
                    frameNum = tmpframeNum
                elif frameNum < tmpframeNum:
                    frameNum = tmpframeNum
                else:
                    pass
            else:
                raise Exception("Error: cannot find %s" % (inputFile))
        for outputDir, featDim, featName in zip(outputDirSet, cfg.outputDim, cfg.outputExt):
            outputFile = os.path.join(outputDir, fileList[0]) + '.' + featName
            if os.path.isfile(outputFile):
                tmpframeNum = readwrite.read_raw_mat(outputFile, featDim).shape[0]
                if frameNum < tmpframeNum:
                    frameNum = tmpframeNum
                else:
                    pass
            else:
                raise Exception("Error: cannot find %s" % (outputFile))

        # check the number of frames in input / output feature files
        for inputFeatIdx, (inputDir, featDim, featName) in enumerate(zip(inputDirSet, cfg.inputDim, cfg.inputExt)):
            inputFile = os.path.join(inputDir, fileList[0]) + '.' + featName
            if os.path.isfile(inputFile):
                tmpframeNum = readwrite.read_raw_mat(inputFile, featDim).shape[0]
                
                if np.abs(frameNum - tmpframeNum)*1.0/frameNum > 0.1:
                    if hasattr(cfg, 'inputUtteranceLevelFlag') and cfg.inputUtteranceLevelFlag[inputFeatIdx] == 1:
                        pass
                    else:
                        display.self_print("Large mismatch of frame numbers %s" % (inputFile))
                        display.self_print("Please check whether inputDim are correct", 'error')
                        display.self_print("Or check input features are corrupted", 'error')
                        raise Exception("Error: mismatch of frame numbers")
            else:
                raise Exception("Error: cannot find %s" % (inputFile))

        for outputDir, featDim, featName in zip(outputDirSet, cfg.outputDim, cfg.outputExt):
            outputFile = os.path.join(outputDir, fileList[0]) + '.' + featName
            if os.path.isfile(outputFile):
                tmpframeNum = readwrite.read_raw_mat(outputFile, featDim).shape[0]
                if np.abs(frameNum - tmpframeNum)*1.0/frameNum > 0.1:
                    display.self_print("Large mismatch of frame numbers %s" % (outputFile))
                    display.self_print("Please check whether inputDim are correct", 'error')
                    display.self_print("Or check input features are corrupted", 'error')
                    raise Exception("Error: mismatch of frame numbers")
                else:
                    pass
            else:
                raise Exception("Error: cannot find %s" % (outputFile))
        
        # create file directories
        dataSaveDir = dataDir + os.path.sep + dataPart
        try:
            os.mkdir(dataSaveDir)
        except OSError:
            pass

        inputScpList  = []
        outputScpList = []

        # create the fileName + fileExt lists
        # create symbolic link
        for inputDir, featDim, featName in zip(inputDirSet, cfg.inputDim, cfg.inputExt):
            tmpFileScp = dataSaveDir + os.path.sep + featName + '.scp'
            inputScpList.append(tmpFileScp)
            filePtr = open(tmpFileScp, 'w')
            for fileName in fileList:
                # write full path to the feature
                filePtr.write('%s%s%s.%s\n' % (inputDir, os.path.sep, fileName, featName))
                if cfg.step01Prepare_LINK is True and flagFileUseSymbolLink:
                    os.system("ln -f -s %s%s%s.%s %s%s%s.%s" % \
                              (inputDir, os.path.sep, fileName, featName,
                               dataLinkDirInput, os.path.sep, fileName, featName))
            filePtr.close()
            
        for outputDir, featDim, featName in zip(outputDirSet, cfg.outputDim, cfg.outputExt):
            tmpFileScp = dataSaveDir + os.path.sep + featName + '.scp'
            outputScpList.append(tmpFileScp)
            filePtr = open(tmpFileScp, 'w')
            for fileName in fileList:
                filePtr.write('%s%s%s.%s\n' % (outputDir, os.path.sep, fileName, featName))
                if cfg.step01Prepare_LINK is True and flagFileUseSymbolLink:
                    os.system("ln -f -s %s%s%s.%s %s%s%s.%s" % \
                              (outputDir, os.path.sep, fileName, featName,
                               dataLinkDirOutput, os.path.sep, fileName, featName))
            filePtr.close()
        
        # create index file list
        filePtr = open(dataSaveDir + os.path.sep + cfg.idxFileName + '.scp', 'w')
        for fileName in fileList:
            filePtr.write('%s%s%s.%s\n' % (dataRawDir, os.path.sep, fileName, cfg.idxFileName))
        filePtr.close()

        # create index files
        if cfg.step01Prepare_IDX is True or cfg.step01Prepare_PACK is True:
            # find the frame-level feature input
            inputFeatIdx = None
            if hasattr(cfg, 'inputUtteranceLevelFlag'):
                for tmpInputFeatIdx, tmpFlagValue in enumerate(cfg.inputUtteranceLevelFlag):
                    if tmpFlagValue == 0:
                        inputFeatIdx = tmpInputFeatIdx
                        break
                if inputFeatIdx is None:
                    raise Exception("Error: cannot process all utterance-level input")
            else:
                inputFeatIdx = 0
                
            # create the lab index lists
            cmd = 'python %s/dataPrepare/getLabIdx5ms.py' % (cfg.path_pyTools_scripts)
            cmd = '%s %s %s %s %s %s %s' % (cmd,
                                            inputDirSet[inputFeatIdx],
                                            cfg.inputExt[inputFeatIdx],
                                            cfg.inputDim[inputFeatIdx],
                                            dataRawDir,
                                            cfg.idxFileName,
                                            fileListFilePath)
            display.self_print('Creating time index files', 'highlight')
            exe_cmd(cmd, cfg.debug)
        else:
            display.self_print('skip creating time index', 'highlight')
        
        # package the data    
        if cfg.step01Prepare_IDX is True or cfg.step01Prepare_PACK is True:
            # write data_config.cfg
            writeDataConfig(dataSaveDir + os.path.sep + 'data_config.py',
                            cfg.idxFileName + '.scp', cfg.fileNumInEachNCPack)
            # pack data
            packDataCmd = 'sh %s/sub_05_package_datanc.sh %s %s' % (cfg.path_scripts, dataSaveDir,
                                                                    cfg.path_pyTools_scripts)

            display.self_print('Packing data', 'highlight')
            exe_cmd(packDataCmd, cfg.debug)
        else:
            display.self_print('skip packing data', 'highlight')

            
    # create file list
    for inputDirSet, outputDirSet, dataPart in zip(cfg.inputDirs, cfg.outputDirs, cfg.dataDivision):


        dataSaveDir = dataDir + os.path.sep + dataPart
        inputScpList  = []
        outputScpList = []
        
        for inputDir, featDim, featName in zip(inputDirSet, cfg.inputDim, cfg.inputExt):
            inputScpList.append(dataSaveDir + os.path.sep + featName + '.scp')
            
        for outputDir, featDim, featName in zip(outputDirSet, cfg.outputDim, cfg.outputExt):
            outputScpList.append(dataSaveDir + os.path.sep + featName + '.scp')
            
        # calculate mean and std
        if dataPart == cfg.computMeanStdOn and cfg.step01Prepare_MV is True:
            display.self_print('Calculating mean and std', 'highlight')

            meanStdTool.meanStdNormMask(inputScpList, cfg.inputDim, cfg.inputNormMask,
                                        dataSaveDir + os.path.sep + cfg.nnDataInputMV)
            display.self_print("\nSave input mean-std as %s" % (os.path.join(dataSaveDir,
                                                                             cfg.nnDataInputMV)),
                               'highlight')
            
            meanStdTool.meanStdNormMask(outputScpList, cfg.outputDim, cfg.outputNormMask,
                                        dataSaveDir + os.path.sep + cfg.nnDataOutputMV)
            display.self_print("\nSave output mean-std as %s" % (os.path.join(dataSaveDir,
                                                                              cfg.nnDataOutputMV)),
                               'highlight')
        else:
            display.self_print('skip calculating mean and std', 'highlight')

            
if __name__ == "__main__":
    if cfg.step01:
        display.self_print_with_date('Step1. preparing data', 'h')
        prepareData()
    else:
        display.self_print_with_date('skip step1(preparing data)', 'h')
    
