#!/bin/sh

WAVINPUTDIR=$1
WAVOUTDIR=$2
WAVLST=$3
SAMP=$4
SCRIPTDIR=$5
SOX=$6
SV56=$7

if [ ! -e ${WAVOUTDIR} ]; then
    mkdir ${WAVOUTDIR}
fi

NORMSCRIPT=${SCRIPTDIR}/wavScripts/01_normRMS.sh
DOWNSCRIPT=${SCRIPTDIR}/wavScripts/02_downsamp.sh

if [ ! -e ${SOX} ]; then
    echo "Error: cannot find ${SOX}"
    exit
fi

if [ ! -e ${SV56} ]; then
    echo "Warning: sv56 is not found, waveform will not be normalized"
fi



if [ ! -e ${NORMSCRIPT} ]; then
    echo "Error: cannot find ${NORMSCRIPT}"
fi

if [ ! -e ${DOWNSCRIPT} ]; then
    echo "Error: cannot find ${DOWNSCRIPT}"
fi


if command -v "parallel" >/dev/null 2>&1 ; then
    # use parallel if available
    cat ${WAVLST} | parallel sh ${NORMSCRIPT} ${WAVINPUTDIR}/{}.wav ${WAVOUTDIR}/{}_temp.wav ${SOX} ${SV56}
    cat ${WAVLST} | parallel sh ${DOWNSCRIPT} ${WAVOUTDIR}/{}_temp.wav ${WAVOUTDIR}/{}.wav ${SAMP} ${SOX}
    cat ${WAVLST} | parallel rm ${WAVOUTDIR}/{}_temp.wav
    
else
    # not use parallel
    for filename in `cat ${WAVLST}`
    do
	if [ -e ${WAVINPUTDIR}/${filename}.wav ]; then
	    sh ${NORMSCRIPT} ${WAVINPUTDIR}/${filename}.wav \
	       ${WAVOUTDIR}/${filename}_temp.wav ${SOX} ${SV56}
	    sh ${DOWNSCRIPT} ${WAVOUTDIR}/${filename}_temp.wav ${WAVOUTDIR}/${filename}.wav ${SAMP} ${SOX}
	    rm ${WAVOUTDIR}/${filename}_temp.wav
	else
	    echo "Error: cannot find ${WAVINPUTDIR}/${filename}.wav"
	fi
    done
fi

