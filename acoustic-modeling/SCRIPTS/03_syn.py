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
import imp
import random


""" ----- Prepare data.nc files for CURRENNT -----
"""

sys.path.append(os.getcwd())
try:
    cfg = __import__(sys.argv[1])
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
    networkToolPath = os.path.join(cfg.path_pyTools_scripts, 'networkTool/netCreate.py')
    networkTool = imp.load_source('netCreate', networkToolPath)
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
                        

def lstdirNoExt(fileDir):
    """ return the list of file names without extension
    """
    return [os.path.splitext(x)[0] for x in os.listdir(fileDir)]
    
def crossSet(list1, list2):
    """ return the cross-set of list1 and list2
    """
    return list(set(list1).intersection(list2))


def writeSplitConfig(filePath):
    filePtr = open(filePath, 'w')
    filePtr.write("#!/usr/bin/python\n")
    filePtr.write("import numpy as np\n")
    filePtr.write("dataType = np.float32\n")
    filePtr.write("outDim = [%s]\n" % (','.join([str(x) for x in cfg.outputDim])))
    filePtr.write("outputDelta = [%s]\n" % (','.join([str(x) for x in cfg.outputDelta])))
    filePtr.write("outputName  = ['%s']\n" % ("','".join([x for x in cfg.outputExt])))

    if hasattr(cfg, 'f0quantize') and hasattr(cfg, 'f0quantizePara') and cfg.f0quantize:
        # convert quantized F0 backinto continuous-valued F0
        if cfg.f0quantizePara[3]:
            filePtr.write("f0Info  = [%f, %f, %d, True]\n" % (cfg.f0quantizePara[0],
                                                              cfg.f0quantizePara[1],
                                                              cfg.f0quantizePara[2]))
        else:
            filePtr.write("f0Info  = [%f, %f, %d, False]\n" % (cfg.f0quantizePara[0],
                                                               cfg.f0quantizePara[1],
                                                               cfg.f0quantizePara[2]))
    
    filePtr.close()

def writeDataConfig(filePath, idxScpName, fileNameInEachNCPack):
    filePtr = open(filePath, 'w')
    filePtr.write("#!/usr/bin/python\n")
    filePtr.write("import numpy as np\n")
    filePtr.write("dataType = np.float32\n")
    filePtr.write("flushThreshold = %d\n" % (fileNameInEachNCPack))
    filePtr.write("inDim = [1,]\n")
    filePtr.write("outDim = [1,]\n")
    filePtr.write("inScpFile = ['%s',]\n" % (idxScpName))
    filePtr.write("outScpFile = ['%s',]\n" % (idxScpName))
    filePtr.write("normMask = [[0], [0]]\n")
    filePtr.write("allScp = 'all.scp'\n")
    filePtr.close()


def prepareData(dataDir, flag_create_new_data):

    testdataDirs = []
    
    dataListPath = dataDir + os.path.sep + 'lists'
    dataRawDir = dataDir + os.path.sep + cfg.idxDirName    
    dataLinkDir = dataDir + os.path.sep + cfg.linkDirname
    
    if flag_create_new_data:
        # create directories
        try:
            os.mkdir(dataDir)
        except OSError:
            pass
        try:
            os.mkdir(dataListPath)
        except OSError:
            pass
        try:
            os.mkdir(dataRawDir)
        except OSError:
            pass
        try:
            os.mkdir(dataLinkDir)
        except OSError:
            pass
    else:
        for tmp_dataDir in [dataDir, dataListPath, dataRawDir, dataLinkDir]:
            if not os.path.isdir(tmp_dataDir) and not os.path.islink(tmp_dataDir):
                display.self_print('Error: cannot find ' + tmp_dataDir, 'error')
                display.self_print('Please use step03Prepare_DATA = True', 'error')
                display.self_print('and create test data again', 'error')
                return

    
    # create file list
    for inputDirSet, outputDirSet, dataPart in zip(cfg.test_inputDirs,
                                                   cfg.test_outputDirs,
                                                   cfg.test_dataDivision):

        display.self_print('Processing ' + dataPart + ' data', 'highlight')
        
        # get the cross-set of file list
        listInput  = lstdirNoExt(inputDirSet[0])
        if cfg.outputUttNum > 0:
            fileList   = listInput[0:cfg.outputUttNum]
        else:
            fileList   = listInput
            
        if inputDirSet:
            for inputDir in inputDirSet:
                listInput2  = lstdirNoExt(inputDir)
                fileList   = crossSet(fileList, listInput2)

        if outputDirSet:
            listOutput = lstdirNoExt(outputDirSet[0])
            if outputDirSet:
                for outputDir in outputDirSet:
                    listOutput2  = lstdirNoExt(outputDir)
                    fileList   = crossSet(fileList, listOutput2)

        # writing file lst
        fileListFilePath = dataListPath + os.path.sep + dataPart + '.lst'
        filePtr = open(fileListFilePath, 'w')
        for fileName in fileList:
            filePtr.write('%s\n' % (fileName))
        filePtr.close()


        # create file directories
        dataSaveDir = dataDir + os.path.sep + dataPart
        testdataDirs.append(dataSaveDir)

        # if data has been created, just return the directory
        if not flag_create_new_data:
            continue
        
        try:
            os.mkdir(dataSaveDir)
        except OSError:
            pass

        inputScpList  = []
        outputScpList = []
        
        # create the fileName + fileExt lists
        for inputDir, featDim, featName in zip(inputDirSet, cfg.inputDim, cfg.inputExt):
            tmpFileScp = dataSaveDir + os.path.sep + featName + '.scp'
            inputScpList.append(tmpFileScp)
            filePtr = open(tmpFileScp, 'w')
            for fileName in fileList:
                filePtr.write('%s%s%s.%s\n' % (inputDir, os.path.sep, fileName, featName))
                os.system("ln -f -s %s%s%s.%s %s%s%s.%s" % (inputDir, os.path.sep, fileName, featName,
                                                            dataLinkDir, os.path.sep, fileName, featName))
            filePtr.close()

        if outputDirSet:
            for outputDir, featDim, featName in zip(outputDirSet, cfg.outputDim, cfg.outputExt):
                tmpFileScp = dataSaveDir + os.path.sep + featName + '.scp'
                outputScpList.append(tmpFileScp)
                filePtr = open(tmpFileScp, 'w')
                for fileName in fileList:
                    filePtr.write('%s%s%s.%s\n' % (outputDir, os.path.sep, fileName, featName))
                    os.system("ln -f -s %s%s%s.%s %s%s%s.%s" % (outputDir, os.path.sep, fileName, featName,
                                                                dataLinkDir, os.path.sep, fileName, featName))
                filePtr.close()

                
        filePtr = open(dataSaveDir + os.path.sep + cfg.idxFileName + '.scp', 'w')
        for fileName in fileList:
            filePtr.write('%s%s%s.%s\n' % (dataRawDir, os.path.sep, fileName, cfg.idxFileName))
        filePtr.close()

        
        # create the lab index lists
        cmd = 'python %s/dataPrepare/getLabIdx5ms.py' % (cfg.path_pyTools_scripts)
        cmd = '%s %s %s %s %s %s %s' % (cmd, inputDirSet[0], cfg.inputExt[0], cfg.inputDim[0],
                                        dataRawDir, cfg.idxFileName, fileListFilePath)
        display.self_print('Creating idx', 'highlight')
        exe_cmd(cmd, cfg.debug)

        
        # write data_config.cfg
        writeDataConfig(dataSaveDir + os.path.sep + 'data_config.py',
                        cfg.idxFileName + '.scp', cfg.fileNumInEachNCPack)

        
        # pack data
        packDataCmd = 'sh %s/sub_05_package_datanc.sh %s %s' % (cfg.path_scripts, dataSaveDir,
                                                                cfg.path_pyTools_scripts)
        display.self_print('Packing data', 'highlight')
        exe_cmd(packDataCmd, cfg.debug)
    return testdataDirs


def genSynCfg(testDataDir):
    """ 
    """
    dataDir    = cfg.nnDataDirNameTest
    linkDataDir= dataDir + os.path.sep + cfg.linkDirname

    testFileList = [testDataDir + os.path.sep + fileName for fileName in os.listdir(testDataDir) if fileName.startswith(cfg.nnDataNcPreFix)]

    inputDirs     = ','.join([linkDataDir for x in range(len(cfg.inputDim))])
    inputDims     = '_'.join([str(x) for x in cfg.inputDim])
    inputExts     = ','.join(['.' +x for x in cfg.inputExt])

    traindataDir  = cfg.nnDataDirNameTrain
    #inputMV       = os.path.join(traindataDir, cfg.computMeanStdOn, cfg.nnDataInputMV)
    #outputMV      = os.path.join(traindataDir, cfg.computMeanStdOn, cfg.nnDataOutputMV)
    
    config = ''
    
    assert testFileList, "found no data.nc in %s" % (testDataDir)
    config = config + '--options_file %s ' % (cfg.synCfg)
    config = config + '--network %s ' % (cfg.test_network)
    config = config + '--ff_input_file %s ' % (','.join(testFileList))
    config = config + '--ff_output_file %s ' % (cfg.outputDir)
    config = config + '--mdn_samplePara %f ' % (cfg.mdnSamplingNoiceStd)    
    config = config + '--ExtInputDirs %s ' % (inputDirs)
    config = config + '--ExtInputExts %s ' % (inputExts)
    config = config + '--ExtInputDims %s ' % (inputDims)
    config = config + '--random_seed 12345231 '
    #config = config + '--target_data_ms %s ' % (outputMV)
    #config = config + '--source_data_ms %s ' % (inputMV)
    if hasattr(cfg, 'f0quantize') and cfg.f0quantize:
        config = config + '--mdnSoftmaxGenMethod 1 --ScheduleSampOpt 2 --ScheduleSampPara 50'
        
    if hasattr(cfg, 'nnCurrenntGenCommand') and cfg.nnCurrenntGenCommand is not None:
        config = config + ' ' + cfg.nnCurrenntGenCommand

    runCmd = '%s %s' % (cfg.path_currennt, config)
    exe_cmd(runCmd, cfg.debug)


    
def genSplit(testDataDir):
    splitConfig = cfg.nnDataDirNameTest + os.path.sep + cfg.splitConfig
    writeSplitConfig(splitConfig)
    datamv   = 'NONE'        
    splitCmd = 'python %s' % (os.path.join(cfg.path_pyTools_scripts, 'dataGen/GenSynData.py'))
    splitCmd = '%s %s %s %s %s' % (splitCmd, splitConfig, testDataDir, testDataDir, datamv)
    exe_cmd(splitCmd, cfg.debug)
    display.self_print('Output features are generated to %s' % (testDataDir), 'highlight')
    
def wavCreate(testDataDir):


    mlpgFlag = []
    pythonScript = os.path.join(cfg.path_pyTools_scripts, 'synWav.py')
    if cfg.wavformGenerator == 'WORLD':
        for featName in cfg.wavGenWorldRequire:
            try:
                mlpgFlagIdx = cfg.outputExt.index(featName)
                mlpgFlag.append(cfg.mlpgFlag[mlpgFlagIdx])
            except ValueError:
                print("outputExt in synconfig has no %s " % (featName))
                raise Exception("WORLD vocoder requires %s " % (featName))


    elif cfg.wavformGenerator == 'STRAIGHT':
        for featName in cfg.wavGenWorldRequire:
            try:
                mlpgFlagIdx = cfg.outputExt.index(featName)
                mlpgFlag.append(cfg.mlpgFlag[mlpgFlagIdx])
            except ValueError:
                print("outputExt in synconfig has no %s " % (featName))
                raise Exception("STRAIGHT vocoder requires %s " % (featName))
                
    else:
        raise Exception("Unknown wavFormGenerator = %s" % (cfg.wavFormGenerator))
        
        
    if sum(mlpgFlag) > 0:
        datamv = cfg.mlpgVar
        assert os.path.isdir(datamv), "Cannot find mlpgVar = %s for MLPG"
    else:
        datamv = 'NONE'

    if hasattr(cfg, 'vu_threshold'):
        vuThres = cfg.vu_threshold
        display.self_print("Use vu_threshold %f" % (vuThres), 'highlight')
    else:
        vuThres = 0.5

        
    exe_cmd("ls %s/*.htk > %s/gen.scp" % (testDataDir, testDataDir), cfg.debug)
    wavCmd = 'python %s %s %f %s %d %s %d %s %d %s %s %s %s %f' \
             % (pythonScript, testDataDir, cfg.wavPostFilter,
                testDataDir, mlpgFlag[0],
                testDataDir, mlpgFlag[1],
                testDataDir, mlpgFlag[2],
                "%s/gen.scp" % (testDataDir),
                cfg.wavformGenerator,
                datamv, cfg.path_pyTools_scripts, vuThres)
    
    exe_cmd(wavCmd, cfg.debug)

    if cfg.lf0UV:
        uvScript = os.path.join(cfg.path_pyTools_scripts, 'dataGen/useUVonLf0.py')
        if cfg.lf0UVExternalDir is None:
            uvCmd = 'python %s %s %s %s %s %s' % (uvScript, testDataDir, vuThres,
                                                  cfg.lf0ext, cfg.vuvext, testDataDir)
        else:
            uvCmd = 'python %s %s %s %s %s %s' % (uvScript, testDataDir, cfg.lf0UVExternalThre,
                                                  cfg.lf0ext, cfg.lf0UVExternalExt,
                                                  cfg.lf0UVExternalDir)
        exe_cmd(uvCmd, cfg.debug)
        
    if cfg.lf02f0:
        f0Script = os.path.join(cfg.path_pyTools, 'speechTools/f0convert.py')
        f0Cmd = 'python %s %s %s %s' % (f0Script, testDataDir, cfg.lf0ext, cfg.f0ext)
        exe_cmd(f0Cmd, cfg.debug)

    
if __name__ == "__main__":
    # prepare test data
    if cfg.step03:
        display.self_print_with_date('Step3. Generating from networks', 'h')
        
        if cfg.step03Prepare_DATA is True:
            testDataDirs = prepareData(cfg.nnDataDirNameTest,
                                       cfg.step03Prepare_DATA)
        else:
            testDataDirs = prepareData(cfg.nnDataDirNameTest,
                                       cfg.step03Prepare_DATA)
            display.self_print('Skip packaing data', 'highlight')

        # for each test data dir
        for testDataDir in testDataDirs:        
            display.self_print(testDataDir, 'highlight')
            if cfg.step03NNGen is True:
                # generate output data (HTK format) from CURRENNT
                genSynCfg(testDataDir)
                # extract the output features from the HTK genreated by CURRENNT
                genSplit(cfg.outputDir)
            else:
                display.self_print('Skip generating output from network', 'highlight')

        if cfg.step03WaveFormGen is True:
            # generate waveform
            wavCreate(cfg.outputDir)
            display.self_print("\nGenerated waveforms in %s" % (cfg.outputDir), 'highlight')
        else:
            display.self_print('Skip generating waveform', 'highlight')
        display.self_print_with_date('Finish', 'h')
    else:
        display.self_print_with_date('skip step3 (Generating from networks)', 'h')
    
