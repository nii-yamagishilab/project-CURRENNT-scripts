#!/bin/sh

# PATH to the pyTools
export TEMP_WAVEFORM_PROJECT_PYTOOLS_PATH=/work/smg/wang/TEMP/code/py/project-CURRENNT-public/pyTools

# PATH to currennt
export TEMP_WAVEFORM_PROJECT_CURRENNT_PATH=/work/smg/wang/TEMP/code/CURRENNT/CURRENNT_0405/build_cuda9_temp/currennt

# PATH to SOX (http://sox.sourceforge.net/sox.html)
export TEMP_WAVEFORM_PROJECT_SOX_PATH=/usr/bin/sox

# PATH to SV56 (a software to normalize waveform amplitude.
#  You can use other tools to normalize the waveforms before put them into this project.
#  Then, you can set TEMP_WAVEFORM_PROJECT_SV56_PATH=None)
export TEMP_WAVEFORM_PROJECT_SV56_PATH=/work/smg/wang/TOOL/bin/sv56demo

# Add pyTools to PYTHONPATH
export PYTHONPATH=${PYTHONPATH}:${TEMP_WAVEFORM_PROJECT_PYTOOLS_PATH}
