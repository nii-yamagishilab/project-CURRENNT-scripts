# PATCH for CURRENNT
This patch conposed these program.    

* INSTALLER : Install shell script for Ubuntu/Debian ([install.sh](./INSTALLER/install.sh)) and [Dockerfile](./INSTALLER/dockerfile/Dockerfile)
* PREPROCESS: [preprocess.py](./PREPROCESS/preprocess.py) make dataset for sample program of CURRENNT

# Dependence
#### You must install before using this patch 
* numpy == 1.16.4
* scipy
* cython
* pyworld
* librosa
* tqdm

#### These pacages install after [install.sh](./INSTALLER/install.sh).
* BOOST == 1.59
* HDF5 == 1.10.6
* NETCDF == 4.3.3.1
* SZIP == 2.1.1
* ZLIB == 1.2.11
* CURRENNT