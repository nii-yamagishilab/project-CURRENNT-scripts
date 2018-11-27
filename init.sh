#!/bin/sh

# PATH to the pyTools
export TEMP_CURRENNT_PROJECT_PYTOOLS_PATH=/work/smg/wang/GIT/TEAM/project-CURRENNT-public/pyTools/

# PATH to currennt
export TEMP_CURRENNT_PROJECT_CURRENNT_PATH=/work/smg/wang/GIT/TEAM/project-CURRENNT-public/CURRENNT_codes/build/currennt

# PATH to SOX (http://sox.sourceforge.net/sox.html)
export TEMP_CURRENNT_PROJECT_SOX_PATH=/usr/bin/sox

# PATH to SV56 (a software to normalize waveform amplitude.
#  You can use other tools to normalize the waveforms before put them into this project.
#  Then, you can set TEMP_CURRENNT_PROJECT_SV56_PATH=None)
export TEMP_CURRENNT_PROJECT_SV56_PATH=/work/smg/wang/TOOL/bin/sv56demo

# Add pyTools to PYTHONPATH
export PYTHONPATH=${PYTHONPATH}:${TEMP_CURRENNT_PROJECT_PYTOOLS_PATH}
