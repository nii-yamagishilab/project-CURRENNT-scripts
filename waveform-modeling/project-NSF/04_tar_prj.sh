#!/bin/sh
# ----- This script make a tar ball of the project,
# ----- without unnecessary files

PRJNAME=`basename $PWD`
cd ../
tar --exclude="./${PRJNAME}/*DATATEMP*" --exclude="./${PRJNAME}/MODELS/*/epoch*" -cvzf ${PRJNAME}.tar.gz ./SCRIPTS ./${PRJNAME}
cd ${PRJNAME}
mv ../${PRJNAME}.tar.gz ./
