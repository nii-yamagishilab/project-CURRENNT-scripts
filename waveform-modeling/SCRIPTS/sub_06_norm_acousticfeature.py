#!/usr/bin/python
from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import importlib
from ioTools import readwrite as py_rw

try:
    meanStdToolPath = sys.argv[9] + os.path.sep + 'dataProcess'
    sys.path.append(meanStdToolPath)
    meanStdTool = importlib.import_module('meanStd')
except ImportError:
    print("Cannot found %s/dataProcess" % (sys.argv[9]))
        
if __name__ == "__main__":
    dataLst = sys.argv[1]
    acousDirs = sys.argv[2]
    acousExts = sys.argv[3]
    acousDims = sys.argv[4]
    normMask = sys.argv[5]
    f0Ext = sys.argv[6]
    dataLstDir = sys.argv[7]
    mvoutputPath = sys.argv[8]
    
    acousDirList = acousDirs.split(',')
    acousExtList = acousExts.split(',')
    acousDimList = [int(x) for x in acousDims.split('_')]
    try:
        normMaskList = [[int(x)] for x in normMask.split('_')]
    except ValueError:
        # by default, normlize every feature dimension
        normMaskList = [[] for dimCnt in acousDimList]
        
    assert len(acousDirList) == len(acousExtList), "Error: unequal length of acousDirs, acousExts"
    assert len(acousExtList) == len(acousDimList), "Error: unequal length of acousDims, acousExts"
    assert len(acousExtList) == len(normMaskList), "Error: unequal length of acousDims, normmask"

    fileListsBuff = []
    dimCnt = 0
    f0Dim = -1
    for acousDir, acousExt, acousDim in zip(acousDirList, acousExtList, acousDimList):

        # confirm the F0 dimension
        if acousExt == f0Ext:
            f0Dim = dimCnt

        # clearn the extension
        if acousExt.startswith('.'):
            acousExt = acousExt[1:]

        # write the file script
        fileOutput = dataLstDir + os.path.sep + acousExt + '.scp'
        fileListsBuff.append(fileOutput)
        writePtr = open(fileOutput, 'w')
        with open(dataLst, 'r') as readfilePtr:
            for line in readfilePtr:
                filename = line.rstrip('\n')
                writePtr.write('%s/%s.%s\n' % (acousDir, filename, acousExt))
        writePtr.close()

        dimCnt = dimCnt + acousDim
    
    
    meanStdTool.meanStdNormMask(fileListsBuff, acousDimList, normMaskList, mvoutputPath,
                                f0Dim = f0Dim)
    
    meanstd_data = py_rw.read_raw_mat(mvoutputPath, 1)
    if f0Dim >= 0:
        print("Please note:")
        print("F0 mean: %f" % (meanstd_data[f0Dim]))
        print("F0 std: %f" % (meanstd_data[dimCnt+f0Dim]))


