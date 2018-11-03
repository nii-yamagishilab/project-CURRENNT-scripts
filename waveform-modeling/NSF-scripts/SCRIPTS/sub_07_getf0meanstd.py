#!/usr/bin/python

import os
import sys
from ioTools import readwrite as py_rw

if __name__ == "__main__":
    meanstd_data = sys.argv[1]
    acousExts = sys.argv[2]
    acousDims = sys.argv[3]
    f0Ext = sys.argv[4]

    acousExtList = acousExts.split(',')
    acousDimList = [int(x) for x in acousDims.split('_')]

    assert len(acousExtList) == len(acousDimList), "Error: unequal length of acousDims, acousExts"

    dimCnt = 0
    f0Dim = -1
    for acousExt, acousDim in zip(acousExtList, acousDimList):

        # confirm the F0 dimension
        if acousExt == f0Ext:
            f0Dim = dimCnt
        dimCnt = dimCnt + acousDim
    
    meanstd_data = py_rw.read_raw_mat(meanstd_data, 1)
    
    if f0Dim >= 0:
        print "%f %f" % (meanstd_data[f0Dim], meanstd_data[dimCnt+f0Dim])


