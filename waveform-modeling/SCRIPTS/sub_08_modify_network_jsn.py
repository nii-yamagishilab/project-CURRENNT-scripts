#!/usr/bin/python

""" Modify the network configuration
  This script is designed for each specific project
"""

import os
import sys
import json
from pyTools import display

if __name__ == "__main__":
    
    network_path = sys.argv[1]
    try:
        resolution = int(sys.argv[2])
    except ValueError:
        raise Exception("Error: input resolution inccorect %s, sub_08" % (sys.argv[2]))

    try:
        sampling_rate = int(sys.argv[3])
    except ValueError:
        raise Exception("Error: input sampling rate incorrect %s, sub_08" % (sys.argv[3]))

    try:
        acous_dim = int(sys.argv[4])
    except ValueError:
        raise Exception("Error: input acoustic dim incorrect %s, sub_08" % (sys.argv[4]))

    if not os.path.isfile(network_path):
        display.self_print('Error: not found %s' % (network_path), 'error')
        quit()

    network_path_tmp = network_path + '.tmp'
    with open(network_path, 'r') as file_ptr:
        network_data = json.load(file_ptr)

    # change if necessary
    if network_data.has_key('layers'):
        for layer_idx in range(len(network_data['layers'])):
            # change time resolution for condition layer
            if network_data['layers'][layer_idx].has_key('resolution'):
                if network_data['layers'][layer_idx]['resolution'] > 1:
                    network_data['layers'][layer_idx]['resolution'] = resolution
                    
            # change sampling frequency for source module of NSF
            if network_data['layers'][layer_idx].has_key('frequencySR'):
               network_data['layers'][layer_idx]['frequencySR'] = sampling_rate


            # change input layer size of conditional layer
            if network_data['layers'][layer_idx].has_key('type'):
                if network_data['layers'][layer_idx]['type'] == 'externalloader':
                    try:
                        network_data['layers'][layer_idx]['size'] = acous_dim
                    except KeyError:
                        raise Exception("Error: layer %s has no size" % (network_path))
                    
                    if network_data['layers'][layer_idx+1]['type'] == 'skipini':
                        network_data['layers'][layer_idx+1]['size'] = acous_dim
                        
            # change skip-connection of F0 for NSF
            # this change is only used for network.jsn provided
            if network_data['layers'][layer_idx].has_key('layerFlag'):
                if network_data['layers'][layer_idx]['layerFlag'] == 'wavenetConditionInputLayer':
                    if network_data['layers'][layer_idx].has_key('preSkipLayerDim'):
                        tmp = network_data['layers'][layer_idx]['preSkipLayerDim']
                        try:
                            tmp_dim = [int(x) for x in tmp.split('_')]
                        except ValueError:
                            raise Exception("Error: invalid preSkipLayerDim in condition module")
                        if len(tmp_dim) == 4:
                            # assume F0 is always put at least
                            tmp_dim[-2] = acous_dim-1
                            tmp_dim[-1] = acous_dim
                            tmp = '_'.join(str(x) for x in tmp_dim)
                            network_data['layers'][layer_idx]['preSkipLayerDim'] = tmp
                            
    else:
        raise Exception("Error: %s is invalid: no layers found" % (network_path))

    with open(network_path_tmp, 'w') as file_ptr:
        json.dump(network_data, file_ptr, indent=4, separators=(',', ': '))

    os.system("mv %s %s" % (network_path_tmp, network_path))
    display.self_print('%s updated' % (network_path), 'highlight')
    
