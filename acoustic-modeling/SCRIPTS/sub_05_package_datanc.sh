#!/bin/sh

DATANCDIR=$1
SCRIPTS=$2

echo ${SCRIPTS}
PREPARESCRIPT=${SCRIPTS}/dataProcess/PrePareData.py
PACKSCRIPT=${SCRIPTS}/dataProcess/PackData.py


if [ ! -e ${PREPARESCRIPT} ];then
    echo "Error: cannot find ${PREPARESCRIPT}"
    exit
fi

if [ ! -e ${PACKSCRIPT} ]; then
    echo "Error: cannot find ${PACKSCRIPT}"
    exit
fi

if [ ! -e ${DATANCDIR}/data_config.py ];then
    echo "Error: cannot find ${DATANCDIR}/data_config.py"
    exit
fi

rm ${DATANCDIR}/all*
echo python ${PREPARESCRIPT} ${DATANCDIR}/data_config.py ${DATANCDIR}
python ${PREPARESCRIPT} ${DATANCDIR}/data_config.py ${DATANCDIR}

maskOpt=None
normMaskOpt=None
normMethOpt=None
    
if [ ! -e ${DATANCDIR}/all.scp ]; then
    echo "Error: PrePareData.py didn't generate all.scp. Something was wrong"
    exit
fi

echo python ${PACKSCRIPT} ${DATANCDIR}/all.scp None ${DATANCDIR} 1 0 0 ${maskOpt} 1 ${normMaskOpt} ${normMethOpt}
python ${PACKSCRIPT} ${DATANCDIR}/all.scp None ${DATANCDIR} 1 0 0 ${maskOpt} 1 ${normMaskOpt} ${normMethOpt}
    
