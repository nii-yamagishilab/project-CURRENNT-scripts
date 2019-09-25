#!/usr/bin/python3
###########################################################################
##                         Author: Takaki Shinji
##                         Date:   2016 - 2019                           #
##                         Contact: takaki at nii.ac.jp                  #
###########################################################################

# This script extracts 80-dim mel-spectrogram from 16kHz input waveforms
# 1. Please check and modify configuration in SpeechProcessing.py
# 2. Run command $: python3 00_run.py
# 3. Please check the extracted *.mfbsp

# Sample arctic_a0002.wav comes from CMU arctic corpus http://www.festvox.org/cmu_arctic/
#

import wave, numpy
from speechprocessing import SpeechProcessing

fname = './arctic_a0002.wav'
sp = SpeechProcessing()

with wave.Wave_read(fname) as f:
    T = numpy.frombuffer(f.readframes(f.getnframes()), numpy.int16).astype(numpy.float32)
X = sp.analyze(T)


f = open('./arctic_a0002.mfbsp','wb')
datatype = numpy.dtype(('<f4',1))
temp_data = X.astype(datatype)
temp_data.tofile(f,'')
f.close()

print('Done')
