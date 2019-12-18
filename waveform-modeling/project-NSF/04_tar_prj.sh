#!/bin/sh
# ----- This script make a tar ball of this project,

PRJNAME=`basename $PWD`
cd ../
SUPPRJNAME=`basename $PWD`
cd ../
tar --exclude="./${SUPPRJNAME}/${PRJNAME}/*DATATEMP*" --exclude="./${SUPPRJNAME}/${PRJNAME}/MODELS/*/epoch*" --exclude="./${SUPPRJNAME}/${PRJNAME}/*.tar.gz" -cvzf ${PRJNAME}.tar.gz ./${SUPPRJNAME}/SCRIPTS ./init.sh ./${SUPPRJNAME}/${PRJNAME}
cd ./${SUPPRJNAME}/${PRJNAME}
mv ../../${PRJNAME}.tar.gz ./

echo "Please find the tar ball: ${PRJNAME}.tar.gz"
