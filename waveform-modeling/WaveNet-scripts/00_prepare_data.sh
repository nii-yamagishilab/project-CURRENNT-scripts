#!/bin/sh
###########################################################################
##  Scripts for NSF model ----------------------------------------------  #
## ---------------------------------------------------------------------  #
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

# === dependency configuration
#
# path of the pyTools scripts
pyToolsDir=/home/smg/wang/WORK/CODE/GIT/pyTools
export PYTHONPATH=${pyToolsDir}:${PYTHONPATH}

# path of the scripts in pyTools 
scriptsDir=${pyToolsDir}/scripts/utilities-new

# path of sox 
SOX=/usr/bin/sox

# path of SV56 for waveform normalization
#  if not available, please normalize the waveform before using this script
SV56=/work/smg/wang/TOOL/bin/sv56demo

# === input/output configuration
# directories of input data 
INPUT=$PWD/DATA
# directories of training waveform (32kHz, but will be downsampled to 16kHz)
WAVDIR=${INPUT}/wav32k
# directories of mel-spectrogram and F0 (put F0 at last)
ACOUSDIRS=${INPUT}/mfbsp
# file name extension (***.mfbsp for mel-spec, ***.f0 for F0)
ACOUSEXTS=.mfbsp
# dimension of the acoustci features (80 for mel-spec, 1 for F0)
ACOUSDIMS=80
# = 16000 / 200, where 16000 is target waveform sampling rate
#  while 200 Hz is the sampling rate of Mel-spec and F0 since they extracted
#  with a frame shift of 5ms
UPSAMPRATE=80

# Use the 1000 utterances in WADIR as the training set,
#  and the rest as validation set
TRAINUTT=1000

# Specify the Mel-spec
#  (this is only used to generate some time step index files)
MELDIR=${INPUT}/mfbsp
# extension of the data
MELEXT=.mfbsp
# dimension of the data
MELDIM=80

# Number of bits for waveform mu-law compression
MULAWBITS=10


# Specify the extension of F0 feature (if this is available)
#  this will be used to identify the F0 data
F0EXT=None

# log file
LOG=log

# to save intermediate data
DATADIR=$PWD/DATATEMP

# =============================================
##                             
GRE='\033[0;32m'
NC='\033[0m' # No Color

if [ -e ${LOG} ]; then
    rm ${LOG}
    touch ${LOG}
fi
touch ${LOG}

if [ ! -d ${DATADIR} ]; then  
    mkdir ${DATADIR}
fi

check()
{
    Errors=`grep Error ${LOG} | wc -l`
    if [ ${Errors} -gt 0 ]; then
	echo "Terminated due to errors"
	cat ${LOG}
	exit
    fi
}

cmdExt()
{
    cmd="$1"
    echo "\n${GRE}${cmd}${NC}\c"
    echo "\n"
    ${cmd}
}

echo "------------------------------------------------"
echo "------ Step1. generating data lists-  ----------"
echo "------------------------------------------------"
cmd="python ./SCRIPTS/sub_01_prepare_list.py ${ACOUSDIRS},${WAVDIR} ${DATADIR}/scp ${TRAINUTT} > ${LOG} 2>${LOG}"
cmdExt "${cmd}"
check


echo "------------------------------------------------"
echo "------ Step2. process waveform files  ----------"
echo "------------------------------------------------"
# 2. normalize and down sample the waveform files
WAVFORMNORMDIR=${DATADIR}/wav16knorm
cmd="sh ./SCRIPTS/sub_02_waveform_process.sh ${WAVDIR} ${WAVFORMNORMDIR} ${DATADIR}/scp/train.lst
   ${scriptsDir} ${SOX} ${SV56} >> ${LOG} 2>>${LOG}"
cmdExt "${cmd}"

if [ -e ${DATADIR}/scp/val.lst ]; then
    cmd="sh ./SCRIPTS/sub_02_waveform_process.sh ${WAVDIR} ${WAVFORMNORMDIR} ${DATADIR}/scp/val.lst ${scriptsDir} ${SOX} ${SV56} >> ${LOG} 2>>${LOG}"
    cmdExt "${cmd}"
fi
check


echo "------------------------------------------------"
echo "------ Step3. get mu-law and float waveform-----"
echo "------------------------------------------------"
# 3. get mu-law and continous-valued waveforms (binary float32 format)
MUWAVDIR=${DATADIR}/wav16knorm_mulaw   # by default use 10 bits mu-law compression
RAWWAVDIR=${DATADIR}/wav16knorm_float

cmd="sh ./SCRIPTS/sub_03_waveform_mulaw_float.sh ${WAVFORMNORMDIR} ${MUWAVDIR} ${RAWWAVDIR} ${DATADIR}/scp/train.lst ${MULAWBITS} ${scriptsDir} >> ${LOG} 2>>${LOG}"
cmdExt "${cmd}"
if [ -e ${DATADIR}/scp/val.lst ]; then
    cmd="sh ./SCRIPTS/sub_03_waveform_mulaw_float.sh ${WAVFORMNORMDIR} ${MUWAVDIR} ${RAWWAVDIR} ${DATADIR}/scp/val.lst ${MULAWBITS} ${scriptsDir} >> ${LOG} 2>>${LOG}"
    cmdExt "${cmd}"
fi
check

cmd="python ${scriptsDir}/networkTool/netCreate.py $PWD/CONFIGS/mdn.config wavenet-mu-law ${MULAWBITS}"
cmdExt "${cmd}"
if [ ! -e $PWD/CONFIGS/mdn.config ]; then
    echo "MDN config is not generated $PWD/CONFIGS/mdn.config"
    exit
fi
   

echo "------------------------------------------------"
echo "------ Step4. time index files for CURRENNT-----"
echo "------------------------------------------------"
# 4. prepare a simple time step index files
TIMEINDEXDIR=${DATADIR}/idxData
cmd="sh ./SCRIPTS/sub_04_timeidx_get.sh ${MELDIR} ${MELDIM} ${MELEXT} ${UPSAMPRATE} ${TIMEINDEXDIR} ${DATADIR}/scp/train.lst ${scriptsDir} >> ${LOG} 2>>${LOG}"
cmdExt "${cmd}"
if [ -e ${DATADIR}/scp/val.lst ]; then
    cmd="sh ./SCRIPTS/sub_04_timeidx_get.sh ${MELDIR} ${MELDIM} ${MELEXT} ${UPSAMPRATE} ${TIMEINDEXDIR} ${DATADIR}/scp/val.lst ${scriptsDir} >> ${LOG} 2>>${LOG}"
    cmdExt "${cmd}"
fi
check


echo "------------------------------------------------"
echo "------ Step5. data.nc files for CURRENNT--------"
echo "------------------------------------------------"
# 5. package the data into data.nc files for CURRENNT
NCFLOATWAV=${DATADIR}/ncData_muwav
if [ ! -d ${NCFLOATWAV} ]; then
    mkdir ${NCFLOATWAV}
fi

cmd="sh ./SCRIPTS/sub_05_package_datanc.sh ${NCFLOATWAV}/DATA_TRAIN ${TIMEINDEXDIR} ${MUWAVDIR} ${DATADIR}/scp/train.lst $PWD/CONFIGS/data_config.py ${scriptsDir} >> ${LOG} 2>>${LOG}"
cmdExt "${cmd}"

if [ -e ${DATADIR}/scp/val.lst ]; then
    cmd="sh ./SCRIPTS/sub_05_package_datanc.sh ${NCFLOATWAV}/DATA_VAL ${TIMEINDEXDIR} ${MUWAVDIR} ${DATADIR}/scp/val.lst $PWD/CONFIGS/data_config.py ${scriptsDir} >> ${LOG} 2>>${LOG}"
    cmdExt "${cmd}"
fi
check

echo "\n\n"
echo "------------------------------------------------"
echo "------ Step6. mean/std of acoustic features ----"
echo "------------------------------------------------"
# 6. calculate mean/std of acoustic features 
#  note: only train set will be used to caculate mean/std
#        F0 mean/std will be conducted over voiced regions
MEANSTD=${DATADIR}/meanstd.bin
cmd="python ./SCRIPTS/sub_06_norm_acousticfeature.py ${DATADIR}/scp/train.lst ${ACOUSDIRS} ${ACOUSEXTS} ${ACOUSDIMS} NONE ${F0EXT} ${DATADIR}/scp ${MEANSTD} ${scriptsDir} >> ${LOG} 2>>${LOG}"
cmdExt "${cmd}"
check

cat ${LOG}

echo "------------------------------------------------"
echo "------ Step6. mean/std of acoustic features ----"
echo "------------------------------------------------"
