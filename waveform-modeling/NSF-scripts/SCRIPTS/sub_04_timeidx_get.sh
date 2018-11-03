#!/bin/sh

FEATDIR=$1
FEATDIM=$2
FEATEXT=$3
RESOLUTION=$4
OUTDIR=$5
FILELST=$6
SCRIPTDIR=$7

if [ ! -e ${OUTDIR} ]; then
    mkdir ${OUTDIR}
fi

SCRIPT=${SCRIPTDIR}/wavScripts/06_getTimeIdx.py


if [ ! -e ${SCRIPT} ]; then
    echo "Error: cannot find ${SCRIPT}"
fi

python ${SCRIPT} ${FEATDIR} ${OUTDIR} ${FILELST} ${FEATDIM} ${FEATEXT} ${RESOLUTION}
