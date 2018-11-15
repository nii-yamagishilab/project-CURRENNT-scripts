#!/bin/sh

WAVINPUTDIR=$1
MUWAVOUTDIR=$2
RAWWAVOUTDIR=$3
WAVLST=$4
MULAWBITS=$5
SCRIPTDIR=$6

MUWAVSCRIPT=${SCRIPTDIR}/wavScripts/04_getMuWav.py
RAWWAVSCRIPT=${SCRIPTDIR}/wavScripts/05_getFloatWav.py
if [ ! -e ${MUWAVSCRIPT} ]; then
    echo "Error: cannot find ${MUWAVSCRIPT}"
fi

if [ ! -e ${RAWWAVSCRIPT} ]; then
    echo "Error: cannot find ${RAWWAVSCRIPT}"
fi


if [ ${MULAWBITS} -gt 0 ];then
    # mu-law  waveform
    if [ ! -e ${MUWAVOUTDIR} ]; then
	mkdir ${MUWAVOUTDIR}
    fi
    python ${MUWAVSCRIPT} ${WAVLST} ${WAVINPUTDIR} ${MUWAVOUTDIR} ${MULAWBITS}
    
else
    # float waveform
    if [ ! -e ${RAWWAVOUTDIR} ]; then
	mkdir ${RAWWAVOUTDIR}
    fi
    python ${RAWWAVSCRIPT} ${WAVLST} ${WAVINPUTDIR} ${RAWWAVOUTDIR}
fi
