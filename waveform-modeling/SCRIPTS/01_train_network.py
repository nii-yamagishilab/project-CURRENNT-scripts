#!/usr/bin/python
###########################################################################
##  Scripts for NSF model ----------------------------------------------  #
## ---------------------------------------------------------------------  #
##                                                                        #
##  Copyright (c) 2018  National Institute of Informatics                 #
##                                                                        #
##  THE NATIONAL INSTITUTE OF INFORMATICS AND THE CONTRIBUTORS TO THIS    #
##  WORK DISCLAIM ALL WARRANTIES WITH REGARD TO THIS SOFTWARE, INCLUDING  #
##  ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS, IN NO EVENT    #
##  SHALL THE NATIONAL INSTITUTE OF INFORMATICS NOR THE CONTRIBUTORS      #
##  BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY   #
##  DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS,       #
##  WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS        #
##  ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE   #
##  OF THIS SOFTWARE.                                                     #
###########################################################################
##                         Author: Xin Wang                               #
##                         Date:   31 Oct. 2018                           #
##                         Contact: wangxin at nii.ac.jp                  #
###########################################################################
from __future__ import absolute_import
from __future__ import print_function

import os
import sys

# Load configure
sys.path.append(os.getcwd())
try:
    cfg = __import__(sys.argv[1])
except IndexError:
    print("Error: missing argument. Usage: python **.py CONFIG_NAME")
    quit()
except ImportError:
    print("Error: cannot load library: ", sys.argv[1])
    quit()
sys.path.append(cfg.path_pyTools)

from pyTools import display
from ioTools import readwrite


def exe_cmd(cmd, debug=False):
    
    display.self_print(cmd + '\n', 'highlight')
    if not debug:
        os.system(cmd)
    
if cfg.step2:
    display.self_print_with_date('Step2. model training', 'h')

    tmp_network_dir = cfg.model_dir
    tmp_network_file = tmp_network_dir + os.path.sep + cfg.network_name
    tmp_trn_config_template = os.getcwd() + os.path.sep + cfg.network_trn_config

    tmp_data_dir = os.getcwd() + os.path.sep + cfg.tmp_data_dir
    tmp_nc_dir = tmp_data_dir + os.path.sep + cfg.tmp_nc_dir
    tmp_trn_nc_dir = tmp_nc_dir + os.path.sep + cfg.tmp_nc_dir_train
    tmp_trn_nc_scp = tmp_trn_nc_dir + os.path.sep + 'data.scp'
    tmp_val_nc_dir = tmp_nc_dir + os.path.sep + cfg.tmp_nc_dir_val
    tmp_val_nc_scp = tmp_val_nc_dir + os.path.sep + 'data.scp'

    tmp_mv_data = os.getcwd() + os.path.sep + cfg.tmp_name_mean_file

    tmp_mdn_config = os.getcwd() + os.path.sep + cfg.tmp_data_dir
    tmp_mdn_config = tmp_mdn_config + os.path.sep + cfg.tmp_mdn_config_name

    # Get the string of training data.nc files
    if os.path.isfile(tmp_trn_nc_scp):
        tmp_trn_data_nc_list = readwrite.read_txt_list(tmp_trn_nc_scp)
        if len(tmp_trn_data_nc_list) < 1:
            display.self_print('Error: not found train data.nc in %s' % (tmp_trn_nc_dir), 'error')
            quit()
        tmp_trn_data_nc_args = ','.join(tmp_trn_data_nc_list)
    else:
        display.self_print('Error: not found %s' % (tmp_trn_nc_scp), 'error')
        quit()        

    if os.path.isfile(tmp_val_nc_scp):
        tmp_val_data_nc_list = readwrite.read_txt_list(tmp_val_nc_scp)
        if len(tmp_val_data_nc_list) < 1:
            display.self_print('Warning: val data.nc is not used', 'warning')
            tmp_val_data_nc_args = ''
        tmp_val_data_nc_args = ','.join(tmp_val_data_nc_list)
    else:
        display.self_print('Warning: val data.nc is not used' % (tmp_val_nc_dir), 'warning')
        tmp_val_data_nc_args = ''

    # Get template config.cfg
    if os.path.isfile(tmp_trn_config_template):
        #exe_cmd("cp %s %s" % (tmp_trn_config_template, tmp_trn_config))
        pass
    else:
        display.self_print('Error: not found %s' % (tmp_trn_config_template), 'error')
        quit()        

    if not os.path.isfile(tmp_network_file):
        display.self_print('Error: not found %s' % (tmp_network_file), 'error')
        quit()

    if not os.path.isfile(tmp_mv_data):
        display.self_print('Error: %s is not generated in 00_*.pt' % (tmp_mv_data), 'error')
        quit()
        
    # Get F0 mean and std if necessary
    if cfg.f0_ext is not None:
        # get F0 mean and std
        dimCnt = 0
        f0Dim = -1

        meanstd_data = readwrite.read_raw_mat(tmp_mv_data, 1)
        for acousExt, acousDim in zip(cfg.ext_acous_feats, cfg.dim_acous_feats):
            if acousExt == cfg.f0_ext:
                f0Dim = dimCnt
            dimCnt = dimCnt + acousDim
            
        if f0Dim >= 0:
            f0mean = meanstd_data[f0Dim]
            f0std = meanstd_data[f0Dim + dimCnt]
        else:
            f0mean = -1
            f0std = -1
            
    # Update network configurations
    cmd = 'python %s' % (cfg.path_scripts) + os.path.sep + 'sub_08_modify_network_jsn.py'
    cmd = cmd + ' %s %d %d %d' % (tmp_network_file, cfg.upsampling_rate,
                                  cfg.gen_wav_samp, sum(cfg.dim_acous_feats))
    exe_cmd(cmd)


    # Network training
    cmd = '%s --options_file %s --verbose 1' % (cfg.path_currennt, tmp_trn_config_template)
    cmd = cmd + ' --network %s' % (tmp_network_file)
    cmd = cmd + ' --ExtInputDirs %s' % (','.join(cfg.path_acous_feats))
    cmd = cmd + ' --ExtInputExts %s' % (','.join(cfg.ext_acous_feats))
    cmd = cmd + ' --ExtInputDims %s' % ('_'.join([str(dim) for dim in cfg.dim_acous_feats]))
    cmd = cmd + ' --source_data_ms %s' % (tmp_mv_data)
    cmd = cmd + ' --resolutions %d' % (cfg.upsampling_rate)
    cmd = cmd + ' --train_file %s' % (tmp_trn_data_nc_args)
    if len(tmp_trn_data_nc_args):
        cmd = cmd + ' --val_file %s' % (tmp_val_data_nc_args)
        
    if cfg.f0_ext is not None and f0mean > 0 and f0std > 0:
        cmd = cmd + ' --F0MeanForSourceModule %f' % (f0mean)
        cmd = cmd + ' --F0StdForSourceModule %f' % (f0std)

    if cfg.waveform_mu_law_bits > 0:
        if os.path.isfile(tmp_mdn_config):
            cmd = cmd + ' --mdn_config %s' % (tmp_mdn_config)
        else:
            display.self_print('Error: %s is not generated in 00_*.py' % (tmp_mdn_config), 'error')
            quit()

    os.chdir(tmp_network_dir)

    display.self_print("CPU job submitted. Please wait until terminated.", 'ok')
    display.self_print("Please open another terminal to check nvidia-smi", 'ok')
    display.self_print("Also check %s" % (tmp_network_dir + os.path.sep + cfg.tmp_network_trn_log),
                       'ok')
    display.self_print("Also check %s\n" % (tmp_network_dir + os.path.sep + cfg.tmp_network_trn_err),
                       'ok')
    
    exe_cmd(cmd + ' > %s 2>%s' % (cfg.tmp_network_trn_log, cfg.tmp_network_trn_err), cfg.debug)
    display.self_print_with_date('Finish network training', 'ok')
    
else:
    display.self_print_with_date('Skip step2(model training)', 'h')
