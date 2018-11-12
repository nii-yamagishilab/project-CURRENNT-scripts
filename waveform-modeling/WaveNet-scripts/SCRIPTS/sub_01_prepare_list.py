#!/usr/bin/python
"""
"""

import os
import sys
import imp
import numpy as np
import random
from random import shuffle as random_shuffle
from pyTools import display


def lstdirNoExt(fileDir):
    """ return the list of file names without extension                  
    """
    return [x.split('.')[0] for x in os.listdir(fileDir)]

def crossSet(list1, list2):
    """ return the cross-set of list1 and list2                          
    """
    return list(set(list1).intersection(list2))


def createFileLst(dataDirs, dataListDirs, trainortest, trainSetRatio=0.8, random_seed=12345):
    """ create data lists 
        output *.scp will be in dataListDirs
    """
    dataDirs = dataDirs.split(',')
    
    # get the cross-set of file list                               
    dataList  = lstdirNoExt(dataDirs[0])
    for dataDir in dataDirs[1:]:
        listTmp  = lstdirNoExt(dataDir)
        dataList = crossSet(dataList, listTmp)

    random.seed(random_seed)
    random_shuffle(dataList)

    display.self_print('Generating data lists in to %s' % (dataListDirs), 'warning')

    if trainortest == 'test':
        # generating for test set
        display.self_print('\ttest size: %d' % (len(dataList)), 'warning')
        testFileOut = dataListDirs + os.path.sep + 'test.lst'
        testFilePtr = open(testFileOut, 'w')
        for fileName in dataList:
            testFilePtr.write('%s\n' % (fileName))
        testFilePtr.close()
    else:
        # determine the train and validatition set if necessary
        if trainSetRatio is not None and trainSetRatio > 0.0:
            if trainSetRatio < 1.0:
                # a ratio
                trainSetDivide = int(np.round(len(dataList)*trainSetRatio))
            elif trainSetRatio < len(dataList):
                # absolute value of the number of training utterances
                trainSetDivide = int(trainSetRatio)
            else:
                # a default ratio 0.8
                trainSetDivide = int(np.round(len(dataList)*0.8))
            trainSet = dataList[0:trainSetDivide]
            valSet = dataList[trainSetDivide:]
        
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
                
            display.self_print('\ttrain/val sizes: %d, %d' % (len(trainSet), len(valSet)), 'warning')
        else:
            display.self_print('\ttrain/val sizes: %d, 0' % (len(dataList)), 'warning')
            trainFileOut = dataListDirs + os.path.sep + 'train.lst'
            trainFilePtr = open(trainFileOut, 'w')
            for fileName in dataList:
                trainFilePtr.write('%s\n' % (fileName))
            trainFilePtr.close()
    # done
    return

    

if __name__ == "__main__":
    
    dataDirs = sys.argv[1]
    dataListDir = sys.argv[2]
    try:
        trainRatio = float(sys.argv[3])
    except ValueError:
        trainRatio = None

    try:
        if sys.argv[4] == 'testset':
            trainortest = 'test'
        else:
            trainortest = 'train'
    except IndexError:
        trainortest = 'train'        
        
    try:
        os.mkdir(dataListDir)
    except OSError:
        pass
    createFileLst(dataDirs, dataListDir, trainortest,
                  trainSetRatio=trainRatio)
        
