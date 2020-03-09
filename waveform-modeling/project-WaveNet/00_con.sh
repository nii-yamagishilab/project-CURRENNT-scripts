#!/bin/sh
#$ -cwd
#$ -l q_node=1
#$ -l h_rt=24:00:00

. /etc/profile.d/modules.sh
module load cuda/10.0.130
module load python-extension

/gs/hs0/tgh-19IAA/wang/CODE/project-CURRENNT-public/CURRENNT_codes/build/currennt --continue $1 > log_train 2> log_err
