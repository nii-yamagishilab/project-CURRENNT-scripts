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

# path of the pyTools scripts
pyToolsDir=/home/smg/wang/WORK/CODE/GIT/pyTools
# path of the scripts
scriptsDir=${pyToolsDir}/scripts/utilities-new

# === data configuration
# where is test data? 
INPUT=$PWD/TESTDATA
# Remember to put f0 at last
ACOUSDIRS=${INPUT}/mfbsp,${INPUT}/f0
ACOUSEXTS=.mfbsp,.f0
ACOUSDIMS=80_1
ACOUSMASK=1_0
UPSAMPRATE=80

# memory-save mode?
#  if the test sentence is short, and GPU mem space is large
#   please try MEMSAVEMODE=0
MEMSAVEMODE=1

# waveform sampling rate (for generating output in WAV format)
WAVEFORMSR=16000

# to generate the time idx file, use one of the ACOUSDIRS above
MELDIR=${INPUT}/mfbsp
MELEXT=.mfbsp
MELDIM=80

# specify the extension of F0 feature
# if F0mean std have been written into ${MODEL} (in signalgen layer,
#   frequencyF0Mean, frequencyF0Std), there is no need to
#   read F0 mean/std from external meanstd.bin.
#   Simply set F0EXT=''
F0EXT=.f0
# if you know F0 mean and F0std, you can set use them directly
F0Mean=''
F0Std=''


# the mean and std generated in 00_prepare_data.sh from training data
ACOUSMV=$PWD/DATATEMP/meanstd.bin

# trained model (either trained_network.jsn or epoch***.autoave )
MODEL=$PWD/MODELS/NSF/trained_network.jsn

# output directory
OUTDIR=$PWD/MODELS/NSF/output_trained_network

# path to currennt
CURRENNT=/work/smg/wang/TEMP/code/CURRENNT/CURRENNT_0405/build_cuda9_temp/currennt


# ========================
GRE='\033[0;32m'
NC='\033[0m' 
BLU='\033[0;34m'

cmdExt()
{
    cmd="$1"
    echo "\n${GRE}${cmd}${NC}\c"
    echo "\n"
    ${cmd}
}

showMessage()
{
    cmd="$1"
    echo "\n${BLU}${cmd}${NC}"
}


DATADIR=${INPUT}/TEMP
if [ -d ${DATADIR} ]; then
    rm -r ${DATADIR}
fi
mkdir ${DATADIR}

if [ ! -e ${MODEL} ];then
    echo "Error: cannot find ${MODEL}"
    exit
fi

echo "------------------------------------------------"
echo "------ Step1. generating data lists-  ----------"
echo "------------------------------------------------"
# 1. generating the list of test data
cmd="python ./SCRIPTS/sub_01_prepare_list.py ${ACOUSDIRS} ${DATADIR}/scp -1 testset"
cmdExt "${cmd}"


echo "------------------------------------------------"
echo "------ Step4. time index files for CURRENNT-----"
echo "------------------------------------------------"
# 4. prepare a simple time step index files
TIMEINDEXDIR=${DATADIR}/idxData
cmd="sh ./SCRIPTS/sub_04_timeidx_get.sh ${MELDIR} ${MELDIM} ${MELEXT} ${UPSAMPRATE} ${TIMEINDEXDIR} ${DATADIR}/scp/test.lst ${scriptsDir}"
cmdExt "${cmd}"


echo "------------------------------------------------"
echo "------ Step5. data.nc files for CURRENNT--------"
echo "------------------------------------------------"
# 5. package the data into data.nc files for CURRENNT
DATANCDIR=${DATADIR}/ncData
mkdir ${DATANCDIR}

cmd="sh ./SCRIPTS/sub_05_package_datanc.sh ${DATANCDIR}/DATA_TEST ${TIMEINDEXDIR} testset ${DATADIR}/scp/test.lst $PWD/CONFIGS/data_config_test.py ${scriptsDir}"
cmdExt "${cmd}"


if [ -e ${DATANCDIR}/DATA_TEST/data.scp ]; then
    testData=`cat ${DATANCDIR}/DATA_TEST/data.scp | tr '\n' ',' | sed 's/,$//'`
else
    echo "Error:  ${DATANCDIR}/DATA_TEST/data.scp is not generated"
    exit
fi

if [ -z "$testData" ]; then
    echo "Error: test data.nc is not generated"
    exit
fi


echo "------------------------------------------------"
echo "------ Step6. generate waveforms from CURRENNT -"
echo "------------------------------------------------"
# 6. generate
# default configurations for synthesis
CURRENNTARG="--train false --ff_output_format htk --parallel_sequences 1 --input_noise_sigma 0"
CURRENNTARG="${CURRENNTARG} --shuffle_fractions false --shuffle_sequences false --revert_std true"

# important configurations
CURRENNTARG="${CURRENNTARG} --ff_output_file ${OUTDIR} --ff_input_file ${testData}"
CURRENNTARG="${CURRENNTARG} --network ${MODEL} --ExtInputDirs ${ACOUSDIRS}"
CURRENNTARG="${CURRENNTARG} --ExtInputExts ${ACOUSEXTS} --ExtInputDims ${ACOUSDIMS}"
CURRENNTARG="${CURRENNTARG} --source_data_ms ${ACOUSMV} --resolutions ${UPSAMPRATE}"
CURRENNTARG="${CURRENNTARG} --waveNetMemSave ${MEMSAVEMODE}"

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

cmd="${CURRENNT} ${CURRENNTARG}"
cmdExt "${cmd}"
    
ls ${OUTDIR}/*.htk > ${OUTDIR}/gen.scp
cmd="python ${scriptsDir}/wavScripts/genWav.py ${OUTDIR} -1 ${WAVEFORMSR}"
cmdExt "${cmd}"

if [ ${MEMSAVEMODE} -eq 1 ]; then
    showMessage "Generating in memory-save mode"
else
    showMessage "Generating in full mode"
fi

showMessage "Output will be in ${OUTDIR}"
rm -r ${DATADIR}
