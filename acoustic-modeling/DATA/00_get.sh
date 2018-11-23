#!/bin/sh

DIR1=/work/smg/wang/PROJ/PROJS/VCTK/VCTK68/HMM/HTS-NN-training/scripts/nndata
DIR2=/work/smg/wang/DATA/speech/VCTK68/speaker_onehot

mkdir mgc_train
mkdir lf0_train
mkdir vuv_train
mkdir bap_train
mkdir lab_train
mkdir spk_train
for file in `cat tmp.lst`
do
    cp ${DIR1}/mgc_delta/VCTK68_trn_trim/${file}.mgc mgc_train/${file}.mgc
    cp ${DIR1}/iplf0_delta/VCTK68_trn_trim/${file}.lf0 lf0_train/${file}.lf0
    cp ${DIR1}/vuv/VCTK68_trn_trim/${file}.vuv vuv_train/${file}.vuv
    cp ${DIR1}/bap_delta/VCTK68_trn_trim/${file}.bap bap_train/${file}.bap
    cp ${DIR1}/lab/VCTK68_trn_trim/${file}.lab lab_train/${file}.lab
    cp ${DIR2}/${file}.bin spk_train/${file}.bin
done

mkdir mgc_val
mkdir lf0_val
mkdir vuv_val
mkdir bap_val
mkdir lab_val
mkdir spk_val
for file in `cat tmp2.lst`
do
    cp ${DIR1}/mgc_delta/VCTK68_dev_trim/${file}.mgc mgc_val/${file}.mgc
    cp ${DIR1}/iplf0_delta/VCTK68_dev_trim/${file}.lf0 lf0_val/${file}.lf0
    cp ${DIR1}/vuv/VCTK68_dev_trim/${file}.vuv vuv_val/${file}.vuv
    cp ${DIR1}/bap_delta/VCTK68_dev_trim/${file}.bap bap_val/${file}.bap
    cp ${DIR1}/lab/VCTK68_dev_trim/${file}.lab lab_val/${file}.lab
    cp ${DIR2}/${file}.bin spk_val/${file}.bin
done
