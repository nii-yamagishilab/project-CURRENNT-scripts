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
    sys.exit(1)
except ImportError:
    print("Error: cannot load library: ", sys.argv[1])
    sys.exit(1)
sys.path.append(cfg.path_pyTools)
from pyTools import display
import subprocess

def exe_cmd(cmd, debug=False):
    display.self_print("Execute command:", 'ok')
    display.self_print(cmd + '\n', 'highlight')
    if not debug:
        try:
            subprocess.check_call(cmd, shell=True)
            display.self_print("Command is successfully executed:\n%s\n\n" % (cmd), 'ok')
        except subprocess.CalledProcessError as e:
            display.self_print("Failed to run:" + cmd, 'error')
            display.self_print("Please check the printed error message", 'error')
            display.self_print("Process terminated with %s" % (e.returncode), 'error')
            sys.exit(1)
    

if cfg.step1:
    display.self_print_with_date('Step1. preparing data', 'h')

    assert len(cfg.step1s) == 5, 'len(step1s) should be 5 %s' % (sys.argv[1])

    if os.path.dirname(cfg.tmp_data_dir):
        tmp_data_dir = cfg.tmp_data_dir
    else:
        tmp_data_dir = os.getcwd() + os.path.sep + cfg.tmp_data_dir
    tmp_data_scp_dir = tmp_data_dir + os.path.sep + cfg.tmp_scp_name
    tmp_train_lst = tmp_data_scp_dir + os.path.sep + cfg.tmp_scp_train_name
    tmp_val_lst = tmp_data_scp_dir + os.path.sep + cfg.tmp_scp_val_name
    tmp_idx_dir = tmp_data_dir + os.path.sep + cfg.tmp_idx_dir
    tmp_wav_mu_dir = tmp_data_dir + os.path.sep + cfg.tmp_wav_mu_law_dir
    tmp_wav_float_dir = tmp_data_dir + os.path.sep + cfg.tmp_wav_float_dir
    
    try:
        os.mkdir(tmp_data_dir)
    except OSError:
        pass

    if cfg.step1s[0]:
        if hasattr(cfg, 'trn_list') and hasattr(cfg, 'val_list'):
            if os.path.isfile(cfg.trn_list) and os.path.isfile(cfg.val_list):
                display.self_print_with_date('step1.1 copying data lists', 'm')
                tmp_acous_path = ','.join(cfg.path_acous_feats)
                tmp_feat_ext = ','.join(cfg.ext_acous_feats)
                tmp_feat_dim = '_'.join([str(x) for x in cfg.dim_acous_feats])
                cmd = 'python %s' % (cfg.path_scripts) + os.path.sep + 'sub_01_check_list.py'
                cmd = cmd + ' %s,%s' % (tmp_acous_path, cfg.path_waveform)
                cmd = cmd + ' %s,.wav' % (tmp_feat_ext)
                cmd = cmd + ' %s_1' % (tmp_feat_dim)
                cmd = cmd + ' %s' % (tmp_data_scp_dir)
                cmd = cmd + ' %s' % (cfg.trn_list)
                cmd = cmd + ' %s' % (cfg.val_list)
                exe_cmd(cmd, cfg.debug)
            else:
                display.self_print('cannot find %s %s' % (cfg.trn_list, cfg.val_list), 'error')
                sys.exit(1)
        else:
            display.self_print_with_date('step1.1 generating data lists', 'm')
            tmp_acous_path = ','.join(cfg.path_acous_feats)
            tmp_feat_ext = ','.join(cfg.ext_acous_feats)
            tmp_feat_dim = '_'.join([str(x) for x in cfg.dim_acous_feats])
            cmd = 'python %s' % (cfg.path_scripts) + os.path.sep + 'sub_01_prepare_list.py'
            cmd = cmd + ' %s,%s' % (tmp_acous_path, cfg.path_waveform)
            cmd = cmd + ' %s,.wav' % (tmp_feat_ext)
            cmd = cmd + ' %s_1' % (tmp_feat_dim)
            cmd = cmd + ' %s' % (tmp_data_scp_dir)
            cmd = cmd + ' %f' % (cfg.train_utts)
            exe_cmd(cmd, cfg.debug)

    
    if cfg.step1s[1]:
        display.self_print_with_date('step1.2 pre-process waveform', 'm')
        tmp_wav_pre_dir = tmp_data_dir + os.path.sep + cfg.tmp_wav_pre_dir

        # loop over train and validation sets
        for tmp_lst in [tmp_train_lst, tmp_val_lst]:
            
            if os.path.isfile(tmp_lst):
                
                cmd = 'sh %s' % (cfg.path_scripts) + os.path.sep + 'sub_02_waveform_process.sh'
                cmd = cmd + ' %s %s %s %d' % (cfg.path_waveform, tmp_wav_pre_dir,
                                              tmp_lst, cfg.wav_samp)
                cmd = cmd + ' %s %s %s' % (cfg.path_pyTools_scripts, cfg.path_sox, cfg.path_sv56)
                exe_cmd(cmd, cfg.debug)

                if cfg.waveform_mu_law_bits > 0:
                    # mu-law waveform
                    
                    cmd = 'sh %s' % (cfg.path_scripts)+os.path.sep+'sub_03_waveform_mulaw_float.sh'
                    cmd = cmd + ' %s %s None' % (tmp_wav_pre_dir, tmp_wav_mu_dir)
                    cmd = cmd + ' %s %d %s' % (tmp_lst, cfg.waveform_mu_law_bits,
                                               cfg.path_pyTools_scripts)
                    exe_cmd(cmd, cfg.debug)

                    # create a mdn.config for mulaw network
                    tmp_mdn_config = os.getcwd() + os.path.sep + cfg.tmp_data_dir
                    tmp_mdn_config = tmp_mdn_config + os.path.sep + cfg.tmp_mdn_config_name
                    cmd = 'python %s' % (cfg.path_pyTools_scripts)
                    cmd = cmd + os.path.sep + 'networkTool' + os.path.sep + 'netCreate.py'
                    cmd = cmd + ' %s' % (tmp_mdn_config)
                    cmd = cmd + ' wavenet-mu-law %d' % (cfg.waveform_mu_law_bits)
                    exe_cmd(cmd, cfg.debug)

                    if not os.path.isfile(tmp_mdn_config):
                        display.self_print('Error %s not generated' % (tmp_mdn_config), 'error')
                        sys.exit(1)
                    
                else:
                    # float waveform
                    
                    cmd = 'sh %s' % (cfg.path_scripts)+os.path.sep+'sub_03_waveform_mulaw_float.sh'
                    cmd = cmd + ' %s None %s' % (tmp_wav_pre_dir, tmp_wav_float_dir)
                    cmd = cmd + ' %s %d %s' % (tmp_lst, cfg.waveform_mu_law_bits,
                                               cfg.path_pyTools_scripts)
                    exe_cmd(cmd, cfg.debug)    
            else:
                if tmp_lst == tmp_train_lst:
                    display.self_print('Error %s not found' % (tmp_train_lst), 'error')
                    sys.exit(1)
                    
    if cfg.step1s[2]:
        display.self_print_with_date('step1.3 time index files', 'm')
        

        # loop over train and validation sets
        for tmp_lst in [tmp_train_lst, tmp_val_lst]:
            if os.path.isfile(tmp_lst):
                cmd = 'sh %s' % (cfg.path_scripts) + os.path.sep + 'sub_04_timeidx_get.sh'
                cmd = cmd + ' %s %d %s' % (cfg.path_acous_feats[0],
                                           cfg.dim_acous_feats[0],
                                           cfg.ext_acous_feats[0])
                cmd = cmd + ' %d %s %s %s' % (cfg.upsampling_rate, tmp_idx_dir, tmp_lst,
                                              cfg.path_pyTools_scripts)
                exe_cmd(cmd, cfg.debug)

    if cfg.step1s[3]:
        display.self_print_with_date('step1.4 data.nc generating for CURRENNT', 'm')

        tmp_nc_dir = tmp_data_dir + os.path.sep + cfg.tmp_nc_dir
        try:
            os.mkdir(tmp_nc_dir)
        except OSError:
            pass

        tmp_data_nc_config =  cfg.tmp_data_nc_config
        
        for tmp_lst, tmp_sub_nc_dir in zip([tmp_train_lst, tmp_val_lst],
                                           [tmp_nc_dir + os.path.sep + cfg.tmp_nc_dir_train,
                                            tmp_nc_dir + os.path.sep + cfg.tmp_nc_dir_val]):
            if not os.path.isfile(tmp_lst):
                continue
            cmd = 'sh %s' % (cfg.path_scripts) + os.path.sep + 'sub_05_package_datanc.sh'
            cmd = cmd + ' %s %s' % (tmp_sub_nc_dir, tmp_idx_dir)
            if cfg.waveform_mu_law_bits > 0:
                # mu-law waveform
                cmd = cmd + ' %s %s %s %s' % (tmp_wav_mu_dir, tmp_lst, tmp_data_nc_config,
                                              cfg.path_pyTools_scripts)
            else:
                # float waveform
                cmd = cmd + ' %s %s %s %s' % (tmp_wav_float_dir, tmp_lst, tmp_data_nc_config,
                                              cfg.path_pyTools_scripts)
            exe_cmd(cmd, cfg.debug)

    if cfg.step1s[4]:
        display.self_print_with_date('step1.5 get mean/std of acoustic features', 'm')
        tmp_mv_file = os.getcwd() + os.path.sep + cfg.tmp_name_mean_file
        cmd = 'python %s' % (cfg.path_scripts) + os.path.sep + 'sub_06_norm_acousticfeature.py'
        cmd = cmd + ' %s' % (tmp_train_lst)
        cmd = cmd + ' %s %s %s NONE' % (','.join(cfg.path_acous_feats),
                                        ','.join(cfg.ext_acous_feats),
                                        '_'.join([str(dim) for dim in cfg.dim_acous_feats]))
        cmd = cmd + ' %s %s %s %s' % (str(cfg.f0_ext), tmp_data_scp_dir, tmp_mv_file,
                                      cfg.path_pyTools_scripts)
        exe_cmd(cmd, cfg.debug)
        
    # Done
    display.self_print_with_date('Finish data preparation', 'ok')        
else:
    display.self_print_with_date('Skip step1 (preparing data)', 'h')
