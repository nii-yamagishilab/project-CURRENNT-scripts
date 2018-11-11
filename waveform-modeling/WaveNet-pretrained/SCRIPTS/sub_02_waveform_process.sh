#!/bin/sh

WAVINPUTDIR=$1
WAVOUTDIR=$2
WAVLST=$3

SCRIPTDIR=$4
SOX=$5
SV56=$6

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
    exit
fi



if [ ! -e ${NORMSCRIPT} ]; then
    echo "Error: cannot find ${NORMSCRIPT}"
fi

if [ ! -e ${DOWNSCRIPT} ]; then
    echo "Error: cannot find ${DOWNSCRIPT}"
fi

for filename in `cat ${WAVLST}`
do
    if [ -e ${WAVINPUTDIR}/${filename}.wav ]; then
	sh ${NORMSCRIPT} ${WAVINPUTDIR}/${filename}.wav \
	   ${WAVOUTDIR}/${filename}_temp.wav ${SOX} ${SV56}
	sh ${DOWNSCRIPT} ${WAVOUTDIR}/${filename}_temp.wav ${WAVOUTDIR}/${filename}.wav ${SOX}
	rm ${WAVOUTDIR}/${filename}_temp.wav
    else
	echo "Error: cannot find ${WAVINPUTDIR}/${filename}.wav"
    fi
done

