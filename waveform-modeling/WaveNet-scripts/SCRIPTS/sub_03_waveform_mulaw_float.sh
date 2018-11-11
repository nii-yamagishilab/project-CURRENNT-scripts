#!/bin/sh

WAVINPUTDIR=$1
MUWAVOUTDIR=$2
RAWWAVOUTDIR=$3
WAVLST=$4
MULAWBITS=$5
SCRIPTDIR=$6


if [ ! -e ${MUWAVOUTDIR} ]; then
    mkdir ${MUWAVOUTDIR}
fi

if [ ! -e ${RAWWAVOUTDIR} ]; then
    mkdir ${RAWWAVOUTDIR}
fi

MUWAVSCRIPT=${SCRIPTDIR}/wavScripts/04_getMuWav.py
RAWWAVSCRIPT=${SCRIPTDIR}/wavScripts/05_getFloatWav.py


if [ ! -e ${MUWAVSCRIPT} ]; then
    echo "Error: cannot find ${MUWAVSCRIPT}"
fi

if [ ! -e ${RAWWAVSCRIPT} ]; then
    echo "Error: cannot find ${RAWWAVSCRIPT}"
fi

# default, 10 bits mu-law compression
python ${MUWAVSCRIPT} ${WAVLST} ${WAVINPUTDIR} ${MUWAVOUTDIR} ${MULAWBITS}

python ${RAWWAVSCRIPT} ${WAVLST} ${WAVINPUTDIR} ${RAWWAVOUTDIR}
