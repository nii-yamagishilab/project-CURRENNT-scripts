#!/bin/sh

DATANCDIR=$1
LABIDXDIR=$2
WAVDATADIR=$3
DATALST=$4
CONFIG=$5
SCRIPTS=$6

echo ${SCRIPTS}
PREPARESCRIPT=${SCRIPTS}/dataProcess/PrePareData.py
PACKSCRIPT=${SCRIPTS}/dataProcess/PackData.py

if [ -d ${DATANCDIR} ];then
    rm -r ${DATANCDIR}
fi
mkdir ${DATANCDIR}

if [ ! -e ${CONFIG} ];then
    echo "Error: cannot find ${CONFIG}"
    exit
fi

if [ ! -e ${PREPARESCRIPT} ];then
    echo "Error: cannot find ${PREPARESCRIPT}"
    exit
fi

if [ ! -e ${PACKSCRIPT} ]; then
    echo "Error: cannot find ${PACKSCRIPT}"
    exit
fi

cp ${CONFIG} ${DATANCDIR}/data_config.py
cat ${DATALST} | sed 's:^:'${LABIDXDIR}'/:g' | sed 's:$:.bin:g' > ${DATANCDIR}/lab.scp

if [ "$WAVDATADIR" = "testset" ]; then
    echo "generating for test set"

else
    cat ${DATALST} | sed 's:^:'${WAVDATADIR}'/:g' | sed 's:$:.bin:g' > ${DATANCDIR}/wav.scp
fi

echo python ${PREPARESCRIPT} ${DATANCDIR}/data_config.py ${DATANCDIR}
python ${PREPARESCRIPT} ${DATANCDIR}/data_config.py ${DATANCDIR}

if [ -e ${testDataDir}/mask.txt ]
then
    maskOpt=${testDataDir}/mask.txt
else
    maskOpt=None
fi

if [ -e ${testDataDir}/normMask ]
then
    normMaskOpt=${testDataDir}/normMask
else
    normMaskOpt=None
fi

if [ -e ${testDataDir}/normMethod ]
then
    normMethOpt=${testDataDir}/normMethod
else
    normMethOpt=None
fi

if [ ! -e ${DATANCDIR}/all.scp ]; then
    echo "Error: PrePareData.py didn't generate all.scp. Something was wrong"
    exit
fi
echo python ${PACKSCRIPT} ${DATANCDIR}/all.scp None ${DATANCDIR} 1 0 0 ${maskOpt} 1 ${normMaskOpt} ${normMethOpt}
python ${PACKSCRIPT} ${DATANCDIR}/all.scp None ${DATANCDIR} 1 0 0 ${maskOpt} 1 ${normMaskOpt} ${normMethOpt}
    
