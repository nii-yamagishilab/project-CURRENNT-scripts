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


# === data configuration (copied from 00_prepare_data.sh)
# where is the acoustic features? Remember to put f0 at last
INPUT=$PWD/DATA
ACOUSDIRS=${INPUT}/mfbsp,${INPUT}/f0
ACOUSEXTS=.mfbsp,.f0
ACOUSDIMS=80_1
ACOUSMASK=1_0

UPSAMPRATE=80

# specify the extension of F0 feature
#  this is used to get the F0 mean and F0 std
#  if the trained_network.jsn has frequencyF0Mean, frequencyF0Std
#  in signalgen layer, there is no need to specify F0EXT
F0EXT=.f0

# if you know F0 mean and F0std, you can use them
#  otherwise set them to ""
F0Mean=''
F0Std=''

# path to currennt
CURRENNT=/work/smg/wang/TEMP/code/CURRENNT/CURRENNT_0405/build_cuda9_temp/currennt

# directory of the model to be trained
MODELDIR=$PWD/MODELS/NSF

# command configurations for model trainning
COMMONCFG=$PWD/CONFIGS/train_config.cfg


# the mean and std generated in 00_prepare_data.sh (no need to change if unnecessary)
ACOUSMV=$PWD/DATATEMP/meanstd.bin
# where is the data.nc directory (no need to change if unnecessary)
DATANCDIR=$PWD/DATATEMP/ncData_floatWav

# =============================================
GRE='\033[0;32m'
NC='\033[0m'
BLU='\033[0;34m'

cmdExtSpecial()
{
    cmd="$1"
    echo "\n${GRE}${cmd}${NC}\c"
    echo "\n"
    ${cmd}  > log_train 2>log_err &
}

showMessage()
{
    cmd="$1"
    echo "\n${BLU}${cmd}${NC}"
}


if [ ! -e ${MODELDIR}/network.jsn ]; then
    echo "Error: cannot find ${MODELDIR}/network.jsn"
    exit
fi

if [ ! -e ${COMMONCFG} ]; then
    echo "Error: cannot find ${COMMONCFG}"
    exit
fi


if [ ! -e ${DATANCDIR}/DATA_TRAIN/data.scp ]; then
    echo "Error: cannot find ${DATANCDIR}/DATA_TRAIN"
    exit
fi

trainData=`cat ${DATANCDIR}/DATA_TRAIN/data.scp | tr '\n' ',' | sed 's/,$//'`

if [ -e ${DATANCDIR}/DATA_VAL/data.scp ]; then
    valData=`cat ${DATANCDIR}/DATA_VAL/data.scp | tr '\n' ',' | sed 's/,$//'`
else
    valData=''
fi


cp ${COMMONCFG} ${MODELDIR}/config.cfg

CURRENNTARG="--options_file config.cfg --verbose 1 --ExtInputDirs ${ACOUSDIRS}"
CURRENNTARG="${CURRENNTARG} --ExtInputExts ${ACOUSEXTS} --ExtInputDims ${ACOUSDIMS}"
CURRENNTARG="${CURRENNTARG} --source_data_ms ${ACOUSMV} --resolutions ${UPSAMPRATE}"
CURRENNTARG="${CURRENNTARG} --train_file ${trainData}"

if [ ! -z "$valData" ]; then
    CURRENNTARG="${CURRENNTARG} --val_file ${valData}"
fi

if [ -z "$F0EXT" ]; then
    if [ -z "${F0Mean}" ] && [ -z "${F0Std}" ]; then
	echo "Assume F0 mean and std have been stored in network.jsn"
    else
	echo "F0 mean: ${F0Mean}"
	echo "F0 std: ${F0Std}"
	CURRENNTARG="${CURRENNTARG} --F0MeanForSourceModule ${F0Mean}"
	CURRENNTARG="${CURRENNTARG} --F0StdForSourceModule ${F0Std}"
    fi
else
    F0MS=`python ./SCRIPTS/sub_07_getf0meanstd.py ${ACOUSMV} ${ACOUSEXTS} ${ACOUSDIMS} ${F0EXT}`
    F0Mean=`echo ${F0MS} | awk '{print $1}'`
    F0Std=`echo ${F0MS} | awk '{print $2}'`
    echo "F0 mean: ${F0Mean}"
    echo "F0 std: ${F0Std}"
    CURRENNTARG="${CURRENNTARG} --F0MeanForSourceModule ${F0Mean}"
    CURRENNTARG="${CURRENNTARG} --F0StdForSourceModule ${F0Std}"
fi



cd ${MODELDIR}
cmdTmp="${CURRENNT} ${CURRENNTARG}"
cmdExtSpecial "${cmdTmp}"
showMessage "Job submitted to background."
showMessage "Please check nvidia-smi"
showMessage "Please check training log in $PWD/log_train"
showMessage "Please check error per utterance in $PWD/log_err"
showMessage "After training, there will epoch***.autosave and trained_network.jsn in $PWD"

