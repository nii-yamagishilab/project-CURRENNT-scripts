#!/usr/bin/python
"""
"""
from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import imp
import numpy as np
import random
from random import shuffle as random_shuffle
from pyTools import display
from ioTools import readwrite

def lstdirNoExt(fileDir, ext=None):
    """ return the list of file names without extension                  
    """
    #return [x.split('.')[0] for x in os.listdir(fileDir)]
    if ext is None:
        return [x.split('.')[0] for x in os.listdir(fileDir) if not x.startswith('.')]
    else:
        return [x.split('.')[0] for x in os.listdir(fileDir) if not x.startswith('.') and x.endswith(ext)]

def crossSet(list1, list2):
    """ return the cross-set of list1 and list2                          
    """
    return list(set(list1).intersection(list2))

def diff_list(list1, list2):
    return list(set(list1).difference(list2))

def createFileLst(dataDirs, dataExts, dataDim, dataListDirs, trnList, valList):
    """ create data lists 
        output *.scp will be in dataListDirs
    """
    dataDirs = dataDirs.split(',')
    dataExts = dataExts.split(',')
    dataDims = [int(x) for x in dataDim.split('_')]
    assert len(dataDirs) == len(dataExts), 'Error: sub_1_prepare_list.py dataDirs and dataExts wrong'

    # get the cross-set of file lists
    dataList  = lstdirNoExt(dataDirs[0], dataExts[0])
    for dataDir, dataExt in zip(dataDirs[1:], dataExts[1:]):
        listTmp  = lstdirNoExt(dataDir, dataExt)
        dataList = crossSet(dataList, listTmp)

    # check if file exists
    if len(dataList) < 1:
        display.self_print("Error: fail to found data. Please check:", 'error')
        display.self_print("path_acous_feats, ext_acous_feats, path_waveform in config.py;", 'error')
        display.self_print("Please also check the names of input data files.", 'error')
        raise Exception("Error: fail to generate file list.")

    # check if data exists
    pre_defined_trn_list = readwrite.read_txt_list(trnList)
    pre_defined_val_list = readwrite.read_txt_list(valList)
    diff_trn_list =  diff_list(pre_defined_trn_list, dataList)
    diff_val_list =  diff_list(pre_defined_val_list, dataList)
    if len(diff_trn_list):
        display.self_print("Error: training data missing. Please check:", 'error')
        print(diff_trn_list)
        raise Exception("Error: fail to prepare file list.")
    
    if len(diff_val_list):
        display.self_print("Error: validation data missing. Please check:", 'error')
        print(diff_val_list)
        raise Exception("Error: fail to prepare file list.")    

    
    # before start, take a simple test on the configuration of feature dimension
    frameNum = None
    for inputDir, featDim, featName in zip(dataDirs[0:-1], dataDims[0:-1], dataExts[0:-1]):
        inputFile = os.path.join(inputDir, dataList[0]) + '.' + featName.lstrip('.')
        if os.path.isfile(inputFile):
            tmpframeNum = readwrite.read_raw_mat(inputFile, featDim).shape[0]
            if frameNum is None or frameNum < tmpframeNum:
                frameNum = tmpframeNum
    
    for inputDir, featDim, featName in zip(dataDirs[0:-1], dataDims[0:-1], dataExts[0:-1]):
        inputFile = os.path.join(inputDir, dataList[0]) + '.' + featName.lstrip('.')
        if os.path.isfile(inputFile):
            tmpframeNum = readwrite.read_raw_mat(inputFile, featDim).shape[0]
            if np.abs(frameNum - tmpframeNum)*1.0/frameNum > 0.1:
                if featDim == readwrite.read_raw_mat(inputFile, 1).shape[0]:
                    pass
                else:
                    display.self_print("Large mismatch of frame numbers %s" % (inputFile))
                    display.self_print("Please check whether inputDim are correct", 'error')
                    display.self_print("Or check input features are corrupted", 'error')
                    raise Exception("Error: mismatch of frame numbers")
    
    
    display.self_print('Generating data lists in to %s' % (dataListDirs), 'highlight')

    if True:
        trainSet = pre_defined_trn_list
        valSet = pre_defined_val_list

        if len(valSet) > len(trainSet):
            display.self_print("Warning: validation set is larger than training set", 'warning')
            display.self_print("It's better to change train_utts in config.py", 'warning')
            
        trainFileOut = dataListDirs + os.path.sep + 'train.lst'
        trainFilePtr = open(trainFileOut, 'w')
        for fileName in trainSet:
            trainFilePtr.write('%s\n' % (fileName))
        trainFilePtr.close()
            
        if len(valSet):
            valFileOut = dataListDirs + os.path.sep + 'val.lst'
            valFilePtr = open(valFileOut, 'w')
            for fileName in valSet:
                valFilePtr.write('%s\n' % (fileName))
            valFilePtr.close()
        display.self_print('\ttrain/val sizes: %d, %d' % (len(trainSet),len(valSet)), 'warning')
        
    # done
    return

    

if __name__ == "__main__":
    
    dataDirs = sys.argv[1]
    dataExts = sys.argv[2]
    dataDims = sys.argv[3]
    dataListDir = sys.argv[4]
    trnList = sys.argv[5]
    valList = sys.argv[6]
    
        
    try:
        os.mkdir(dataListDir)
    except OSError:
        pass
    createFileLst(dataDirs, dataExts, dataDims, dataListDir, trnList, valList)
        
