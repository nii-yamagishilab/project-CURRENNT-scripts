# -*-coding:utf-8-+-
import argparse
from glob import glob
import math
import os
import pickle
import time

import librosa
import numpy as np
from tqdm import tqdm

import pyworld as pw


def _find_wavs(path):
    wavs = glob(path + os.sep + "*.wav")
    wavs.sort()
    return wavs


def _load(fname, sr, mono=True):
    wav, _ = librosa.load(fname, sr=sr, mono=mono)
    return wav


def _fetch_basename(fname):
    return os.path.splitext(os.path.basename(fname))[0]


def fetch_basenames(fnames):
    return [_fetch_basename(fname) for fname in fnames]


def load_wavs(wav_dir, sr, mono=True):
    fnames = _find_wavs(wav_dir)
    wavs = [_load(fname, sr=sr, mono=mono) for fname in fnames]
    return wavs, fnames


def save_pickle(variable, fname):
    with open(fname, "wb") as f:
        pickle.dump(variable, f)


def saves(fname, save_dir, f0, mcep):
    with open(save_dir + os.sep + "f0" + os.sep + fname + ".f0", "wb") as f:
        temp_data1 = np.array(f0, dtype=('<f4', 1))
        temp_data1.tofile(f, '')
    with open(save_dir + os.sep + "mfbsp" + os.sep + fname + ".mfbsp", "wb") as f:
        temp_data = np.array(mcep, dtype=('<f4', 1))
        temp_data.tofile(f, '')


def save_dataset(fnames, save_dir, per_val):
    num_val = math.floor(len(fnames) * per_val)
    with open(save_dir + os.sep + "list" + os.sep + "train.lst", "w", encoding="utf-8") as f:
        f.write("\n".join(fnames[0:-num_val]))
    with open(save_dir + os.sep + "list" + os.sep + "val.lst", "w", encoding="utf-8") as f:
        f.write("\n".join(fnames[-num_val:]))

    return len(fnames) - num_val, num_val


class ExtractFeatures(object):
    def __init__(self, sr=16000, frame_period=5.0, dim=24, mono=True):
        self.sr = sr
        self.frame_period = frame_period
        self.dim = dim
        self.mono = mono

    def _decompose(self, wav):
        wav = wav.astype(np.float64)
        # 基本周波数の抽出
        _f0, taxis = pw.harvest(wav, self.sr, frame_period=self.frame_period,
                                f0_floor=71.0, f0_ceil=800.0)
        f0 = pw.stonemask(wav, _f0, taxis, self.sr)  # 基本周波数の修正
        sp = pw.cheaptrick(wav, f0, taxis, self.sr, fft_size=512)  # スペクトル包絡の抽出
        ap = pw.d4c(wav, f0, taxis, self.sr)  # 非周期性指標の抽出

        return f0, taxis, sp, ap

    # Get Mel-Cepstral coefficients
    def _get_mcep(self, sp):
        mcep = pw.code_spectral_envelope(sp, self.sr, self.dim)

        return mcep.T
    
    def _encode(self, wav):
        f0, taxis, sp, ap = self._decompose(wav)
        mcep = self._get_mcep(sp)
        
        return f0, taxis, mcep, ap
    
    def enode_data(self, wavs):
        f0s = []
        taxes = []
        mceps = []
        aps = []

        for wav in tqdm(wavs):
            f0, taxis, sp, ap = self._decompose(wav)
            mcep = self._get_mcep(sp)
            f0s.append(f0)
            taxes.append(taxis)
            mceps.append(mcep)
            aps.append(ap)

        return f0s, taxes, mceps, aps

    def cal_mean_std(self, mceps):
        mceps_concatenated = np.concatenate(mceps, axis=1)
        mceps_mean = np.mean(mceps_concatenated, axis=1, keepdims=True)
        mceps_std = np.std(mceps_concatenated, axis=1, keepdims=True)

        return mceps_mean, mceps_std
    
    def norm_mcep(self, mcep, mean, std):
        return (mcep - mean) / std


def main(args):
    if args.per_valuation > 1.0:
        print("You must set persentage between 0.0 and 1.0")
        raise Exception("Error: mistake setting persentage of valuation.")

    print("Start Preprocess ...")
    extract = ExtractFeatures(args.sample_rate, args.frame_period, args.dimension, args.mono)

    start_time = time.time()

    wavs, fnames = load_wavs(args.wav_dir, args.sample_rate, args.mono)

    print("Extracting features ...")
    f0s, taxes, mceps, aps = extract.enode_data(wavs)

    mceps_mean, mceps_std = extract.cal_mean_std(mceps)

    print("Saving ...")
    if not os.path.exists(args.save_dir):
        os.makedirs(args.save_dir)
        os.makedirs(args.save_dir + os.sep + "f0")
        os.makedirs(args.save_dir + os.sep + "mfbsp")
        os.makedirs(args.save_dir + os.sep + "list")

    base_fnames = fetch_basenames(fnames)

    for i, (base_fname, f0, mcep) in enumerate(zip(tqdm(base_fnames), f0s, mceps)):
        saves(base_fname, args.save_dir, f0, extract.norm_mcep(mcep, mceps_mean, mceps_std))

    n_train, n_val = save_dataset(base_fnames, args.save_dir, args.per_valuation)

    end_time = time.time()
    print("Preprocessing finished! saved at {}".format(args.save_dir))
    print("Time taken for preprocessing {:.4f} seconds".format(end_time - start_time))
    print("Train data: {}, Valuation data: {}".format(n_train, n_val))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", '--wav_dir', type=str, help="Directory for voice sample")
    parser.add_argument("-s", '--save_dir', type=str, help="Directory for saving preprocessed samples")
    parser.add_argument("--sample_rate", type=int, default=16000, help="Sample rate")
    parser.add_argument("--frame_period", type=float, default=5.0, help="Frame period")
    parser.add_argument("--dimension", type=int, default=80, help="Dimension for mcep")
    parser.add_argument("--mono", type=bool, default=True, help="Convert signal to mono")
    parser.add_argument("--per_valuation", type=float, default=0.3, help="Percentage of valuation (0.0 < x < 1.0)")
    args = parser.parse_args()

    main(args)
