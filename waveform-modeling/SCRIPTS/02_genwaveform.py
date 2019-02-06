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

        
if cfg.step3:
    display.self_print_with_date('Step3. Generating', 'h')

    if os.path.dirname(cfg.tmp_test_data_dir):
        tmp_test_data_dir = cfg.tmp_test_data_dir
    else:
        tmp_test_data_dir = os.getcwd() + os.path.sep + cfg.tmp_test_data_dir
    tmp_data_scp_dir = tmp_test_data_dir + os.path.sep + cfg.tmp_scp_name
    tmp_test_lst = tmp_data_scp_dir + os.path.sep + 'test.lst'
    tmp_idx_dir = tmp_test_data_dir + os.path.sep + cfg.tmp_idx_dir
    
    tmp_nc_dir = tmp_test_data_dir + os.path.sep + cfg.tmp_nc_dir
    tmp_sub_nc_dir = tmp_nc_dir + os.path.sep + cfg.tmp_nc_dir_test
    tmp_test_nc_scp = tmp_sub_nc_dir + os.path.sep + 'data.scp'

    tmp_mv_data = os.getcwd() + os.path.sep + cfg.tmp_name_mean_file

    try:
        os.mkdir(tmp_test_data_dir)
    except OSError:
        pass

    if not os.path.isfile(tmp_mv_data):
        display.self_print('Error: %s is not generated in 00_*.pt' % (tmp_mv_data), 'error')
        quit()
        
    if True:
        display.self_print_with_date('step3.1 generating data lists', 'm')
        tmp_acous_path = ','.join(cfg.path_test_acous_feats)
        tmp_feat_ext = ','.join(cfg.ext_acous_feats)
        tmp_feat_dim = '_'.join([str(x) for x in cfg.dim_acous_feats])
        cmd = 'python %s' % (cfg.path_scripts) + os.path.sep + 'sub_01_prepare_list.py'
        cmd = cmd + ' %s %s %s %s -1 testset' % (tmp_acous_path, tmp_feat_ext, tmp_feat_dim,
                                                 tmp_data_scp_dir)
        exe_cmd(cmd, cfg.debug)
    
                    
    if True:
        display.self_print_with_date('step3.2 time index files', 'm')
        
        cmd = 'sh %s' % (cfg.path_scripts) + os.path.sep + 'sub_04_timeidx_get.sh'
        cmd = cmd + ' %s %d %s' % (cfg.path_test_acous_feats[0],
                                   cfg.dim_acous_feats[0],
                                   cfg.ext_acous_feats[0])
        cmd = cmd + ' %d %s %s %s' % (cfg.upsampling_rate, tmp_idx_dir, tmp_test_lst,
                                      cfg.path_pyTools_scripts)
        exe_cmd(cmd, cfg.debug)

    if True:
        display.self_print_with_date('step1.4 data.nc generating for CURRENNT', 'm')

        
        try:
            os.mkdir(tmp_nc_dir)
        except OSError:
            pass

        tmp_data_nc_config =  cfg.tmp_test_data_nc_config
        
        
        cmd = 'sh %s' % (cfg.path_scripts) + os.path.sep + 'sub_05_package_datanc.sh'
        cmd = cmd + ' %s %s' % (tmp_sub_nc_dir, tmp_idx_dir)
        cmd = cmd + ' testset %s %s %s' % (tmp_test_lst, tmp_data_nc_config,
                                           cfg.path_pyTools_scripts)
        exe_cmd(cmd, cfg.debug)


    if os.path.isfile(tmp_test_nc_scp):
        tmp_test_data_nc_list = readwrite.read_txt_list(tmp_test_nc_scp)
        if len(tmp_test_data_nc_list) < 1:
            display.self_print('Error: not found test data.nc in %s' % (tmp_sub_nc_dir), 'error')
            quit()
        tmp_test_data_nc_args = ','.join(tmp_test_data_nc_list)
    else:
        display.self_print('Error: not found %s' % (tmp_test_nc_scp), 'error')
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

    # cmmandline of CURRENNT

    cmd = '%s --train false --ff_output_format htk' % (cfg.path_currennt)
    cmd = cmd + ' --parallel_sequences 1 --input_noise_sigma 0 --random_seed 12345231'
    cmd = cmd + ' --shuffle_fractions false --shuffle_sequences false --revert_std true'
    
    if cfg.waveform_mu_law_bits > 0:
        # configuration specific for Wavenet mu-law
        cmd = cmd + ' --ScheduleSampOpt 4 --ScheduleSampPara 0'
        cmd = cmd + ' --mdnSoftmaxGenMethod 2'
        
    try:
        if cfg.flag_CPU_gen > 0:
            cmd = cmd + ' --cuda off'
    except AttributeError:
        pass
        
    cmd = cmd + ' --network %s' % (cfg.gen_network_path)    
    cmd = cmd + ' --ff_output_file %s' % (cfg.gen_output_dir)
    cmd = cmd + ' --ff_input_file %s' % (tmp_test_data_nc_args)
    cmd = cmd + ' --ExtInputDirs %s' % (','.join(cfg.path_test_acous_feats))
    cmd = cmd + ' --ExtInputExts %s' % (','.join(cfg.ext_acous_feats))
    cmd = cmd + ' --ExtInputDims %s' % ('_'.join([str(dim) for dim in cfg.dim_acous_feats]))
    cmd = cmd + ' --source_data_ms %s' % (tmp_mv_data)
    cmd = cmd + ' --resolutions %d' % (cfg.upsampling_rate)
    cmd = cmd + ' --waveNetMemSave %d' % (cfg.mem_save_mode)
    
    if cfg.f0_ext is not None and f0mean > 0 and f0std > 0:
        cmd = cmd + ' --F0MeanForSourceModule %f' % (f0mean)
        cmd = cmd + ' --F0StdForSourceModule %f' % (f0std)

    exe_cmd(cmd, cfg.debug)


    exe_cmd("ls %s/*.htk > %s/gen.scp" % (cfg.gen_output_dir, cfg.gen_output_dir), cfg.debug)
    cmd = "python %s/wavScripts/genWav.py " % (cfg.path_pyTools_scripts)
    cmd = cmd + '  %s %d %s' % (cfg.gen_output_dir, cfg.waveform_mu_law_bits, cfg.gen_wav_samp)
    exe_cmd(cmd, cfg.debug)
    
    display.self_print("\noutput will be in %s" % (cfg.gen_output_dir), "highlight")
    #exe_cmd("rm -r %s" % (tmp_test_data_dir))

else:
    display.self_print_with_date('Skip step3(generating)', 'h')

