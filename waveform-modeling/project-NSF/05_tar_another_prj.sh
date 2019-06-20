#!/bin/sh
# ----- This script make a tar ball from a project,
# ----- without unnecessary files

# Where is the root of the project
PRJROOT=/work/smg/yasuda/xinwang-wavenet-125ms-vctk/

# What's the name of the project
PRJNAME=project-WaveNet

# What's the name of the network in the project
MODEL=MODELS/wavenet001/trained_network.jsn

# ${PRJROOT}/${PRJNAME}/${MODEL} should be the full path 
#  to the trained_network.jsn

# 
mkdir -p tmp/${PRJNAME}
cd tmp
cp -r ${PRJROOT}/SCRIPTS ./SCRIPTS
cp ${PRJROOT}/${PRJNAME}/* ./${PRJNAME}/
mkdir -p ./${PRJNAME}/`dirname ${MODEL}`
cp ${PRJROOT}/${PRJNAME}/${MODEL} ./${PRJNAME}/`dirname ${MODEL}`

tar -czvf ${PRJNAME}.tar.gz ./SCRIPTS ./${PRJNAME}
mv ${PRJNAME}.tar.gz ../
cd -
rm -r tmp
