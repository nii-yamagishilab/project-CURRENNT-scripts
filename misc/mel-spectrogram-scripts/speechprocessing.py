###########################################################################
##                         Author: Takaki Shinji
##                         Date:   2016 - 2019                           #
##                         Contact: takaki at nii.ac.jp                  #
###########################################################################

import numpy as np


class SpeechProcessing(object):
    """
    sampling_rate = 16000, 16kHz
    frame_length = 400, 400 sampling points = 25ms
    frame_shift = 80, 80 sampling points = 5ms
    fft_length = 1024, FFT 1024 points
    mel_dimension = 80, dimension of mel-spectrogram
    """
    def __init__(self, sf=16000, fl=400, fs=80, fftl=1024, mfbsize=80):
        self.sf = sf
        self.fl = fl
        self.fs = fs
        self.fftl = fftl
        self.mfbsize = mfbsize
        winpower = np.sqrt(np.sum(np.square(np.blackman(self.fl).astype(np.float32))))
        self.window = np.blackman(self.fl).astype(np.float32) / winpower
        self.melfb = self._melfbank()

    def _freq2mel(self, freq):
        return 1127.01048 * np.log(freq / 700.0 + 1.0)

    def _mel2freq(self, mel):
        return (np.exp(mel / 1127.01048) - 1.0) * 700.0
        
    def _melfbank(self):
        linear_freq = 1000.0
        mfbsize = self.mfbsize - 1

        bFreq = np.linspace(0, self.sf / 2.0, self.fftl//2 + 1, dtype=np.float32)
        minMel = self._freq2mel(0.0)
        maxMel = self._freq2mel(self.sf / 2.0)
        iFreq = self._mel2freq(np.linspace(minMel, maxMel, mfbsize + 2, dtype=np.float32))
        linear_dim = np.where(iFreq<linear_freq)[0].size
        iFreq[:linear_dim+1] = np.linspace(iFreq[0], iFreq[linear_dim], linear_dim+1)

        diff = np.diff(iFreq)
        so = np.subtract.outer(iFreq, bFreq)
        lower = -so[:mfbsize] / np.expand_dims(diff[:mfbsize], 1)
        upper = so[2:] / np.expand_dims(diff[1:], 1)
        fb = np.maximum(0, np.minimum(lower, upper))

        enorm = 2.0 / (iFreq[2:mfbsize+2] - iFreq[:mfbsize])
        fb *= enorm[:, np.newaxis]

        fb0 = np.hstack([np.array(2.0*(self.fftl//2)/self.sf, np.float32), np.zeros(self.fftl//2, np.float32)])
        fb = np.vstack([fb0, fb])

        return fb

    def _frame(self, X):
        X = np.concatenate([np.zeros(self.fl//2, np.float32), X, np.zeros(self.fl//2, np.float32)])
        X = X[:(len(X)-self.fl-1)//self.fs*self.fs+self.fl].reshape(-1, self.fs)
        F = np.hstack([X[i:len(X)-(self.fl//self.fs-1-i)] for i in range(self.fl//self.fs)])
        return F

    def _anawindow(self, F):
        W = F * self.window
        return W

    def _rfft(self, W):
        Y = np.fft.rfft(W, n=self.fftl).astype(np.complex64)
        return Y

    def _amplitude(self, Y):
        eps = 1.0E-12
        A = np.fmax(np.absolute(Y), eps)
        return A

    def _logmelfbspec(self, A):
        M = np.log(np.dot(A, self.melfb.T))
        return M

    def analyze(self, X):
        M = self._logmelfbspec(self._amplitude(self._rfft(self._anawindow(self._frame(X)))))
        return M
