#! /bin/bash
set -e
<< COMMENTOUT
This script is building and installing 'CURRENNT'.
'CURRENNT' is frontend program of Neural Source Filter (NSF).

References
Source code   : https://github.com/nii-yamagishilab/project-CURRENNT-public
Sample scripts: https://github.com/nii-yamagishilab/project-CURRENNT-scripts
COMMENTOUT

cat <<-EOS
---WORNING!!-------------------------------------------------------------------
'CURRENNT' depends on 'Numpy', 'Scipy' and 'Cython'.
And 'CURRENNT' needs 'CUDA 6.5' or later. (Test building under 'CUDA 6.5, 7.0, 8.0, 10.0')
This scripts install dependent packages that is same as the version when TonyWangX (contributer) was build.
You want to install other or later version, you can change version of dependent packages in this script.
-------------------------------------------------------------------------------
EOS

# Versions
VER_BOOST=1.59.0
VER_HDF5=1.10.6
VER_NETCDF=4.3.3.1
VER_SZIP=2.1.1
VER_ZLIB=1.2.11

read -p "Did you installed 'Numpy', 'Scipy', 'Cython'? [y/N]:" ANS

case $ANS in
    [Yy]* )
    cat <<-EOS
Build and install these dependent packages.
・BOOST -> ${VER_BOOST}
・HDF5 -> ${VER_HDF5}
・NETCDF -> ${VER_NETCDF}
・SZIP -> ${VER_SZIP}
・ZLIB -> ${VER_ZLIB}
EOS
    ;;
    * )
    echo "You try again after you install 'Numpy', 'Scipy', 'Cython'."
    exit
    ;;
esac

read -p "Do you agree to install dependent packages? [y/N]:" ANS
case $ANS in 
    [Yy]* )
        read -p "Install path for dependent packages(default=$HOME):" INSTALLPATH
        INSTALLPATH=${INSTALLPATH:-$HOME}
        NSF=$INSTALLPATH/nsf
        BUILDPATH=$NSF/build
        BOOST=$NSF/boost-${VER_BOOST}
        HDF5=$NSF/hdf5-${VER_HDF5}
        NETCDF=$NSF/netcdf-${VER_NETCDF}
        SZLIB=$NSF/szlib

        ;;
    *)
        read -p "Did you installed dependent packages？[y/N]" ANS2
        case $ANS2 in
            [Yy]* )
                echo "Path of dependent packages."
                echo -n "BOOST:"
                read BOOST
                echo -n "HDF5:"
                read HDF5
                echo -n "NETCDF:"
                read NETCDF
                echo -n "SZIP:"
                read SZIP
                echo -n "ZLIB:"
                read ZLIB
                echo "Install path for CURRENNT"
                echo -n "Path:"
                read NSF
                BUILDPATH=$NSF/build
                ;;
            *)
                echo "Breaked install script."
                exit 0
                ;;
        esac
    ;;
esac
cat <<-EOS
Install to
----------------
BOOST -> $BOOST
HDF5 -> $HDF5
NETCDF -> $NETCDF
SZIP, ZLIB -> $SZLIB
----------------
NSF -> $NSF
----------------
EOS

mkdir $NSF

# Build dependent packages
case $ANS2 in
    [Yy]* )

        ;;
    *)  
        DJOBS=$[$(grep cpu.cores /proc/cpuinfo | sort -u | sed 's/[^0-9]//g')+1]
        read -p "Physical core for build. (default=All）:" JOBS
        JOBS=${JOBS:-$DJOBS}
        echo "Using ${JOBS}cores for build."
        read -sp "Password for sudo:" PASS
        sudo -S apt install -y --no-install-recommends build-essential ca-certificates cmake git libpthread-stubs0-dev m4 ninja-build sox wget
        mkdir $BUILDPATH
        cd $BUILDPATH
        wget http://sourceforge.net/projects/boost/files/boost/${VER_BOOST}/boost_${VER_BOOST//./_}.tar.gz \
             https://support.hdfgroup.org/ftp/HDF5/releases/hdf5-$(echo ${VER_HDF5}|rev|cut -c 3-|rev)/hdf5-${VER_HDF5}/src/hdf5-${VER_HDF5}.tar.gz \
             https://github.com/Unidata/netcdf-c/archive/v${VER_NETCDF}.tar.gz \
             https://support.hdfgroup.org/ftp/lib-external/szip/${VER_SZIP}/src/szip-${VER_SZIP}.tar.gz \
             http://www.zlib.net/zlib-${VER_ZLIB}.tar.gz
        find ./*.tar.gz | xargs -n 1 tar -xf
        # Zlib
        cd $(find ${BUILDPATH} -name "zlib-${VER_ZLIB}" -type d) 
        ./configure --prefix=${SZLIB} 
        make -j${JOBS}  
        make install 
        # Szip
        cd $(find ${BUILDPATH} -name "szip-${VER_SZIP}" -type d) 
        ./configure --prefix=${SZLIB}  
        make -j${JOBS}  
        make install 
        # HDF5
        cd $(find ${BUILDPATH} -name "hdf5-${VER_HDF5}" -type d) 
        ./configure --prefix=${HDF5} --with-szlib=${SZLIB} --enable-threadsafe --with-pthread=/usr/include/,/usr/lib/x86_64-linux-gnu/ --enable-hl --enable-shared --enable-unsupported 
        make -j${JOBS}  
        make install 
        # NETCDF
        cd $(find ${BUILDPATH} -name "netcdf-c-${VER_NETCDF}" -type d) 
        ./configure --disable-netcdf-4 --prefix=${NETCDF}  
        make -j${JOBS}  
        make install 
        # BOOST
        cd $(find ${BUILDPATH} -name "boost_${VER_BOOST//./_}" -type d) 
        ./bootstrap.sh --with-libraries=program_options,filesystem,system,random,thread 
        ./b2 install --prefix=${BOOST}
        ;;
esac

TEMP_CURRENNT_PROJECT_CURRENNT_PATH=$NSF/currennt/currennt
TEMP_CURRENNT_PROJECT_PYTOOLS_PATH=$NSF/currennt/pyTools
TEMP_CURRENNT_PROJECT_SOX_PATH=/usr/bin/sox
TEMP_CURRENNT_PROJECT_SV56_PATH=None

# NSF
cd ${BUILDPATH}
git clone -b work-reverb https://github.com/nii-yamagishilab/project-CURRENNT-public.git 
cd project-CURRENNT-public/CURRENNT_codes 
mkdir build $NSF/currennt
cd build 
cmake .. -DCMAKE_BUILD_TYPE=Release -DBOOST_ROOT=${BOOST} -DNETCDF_LIB=${NETCDF}/lib 
make -j${JOBS}
mv ./currennt $NSF/currennt
cp -r ../../pyTools/ $NSF/currennt
cd ${TEMP_CURRENNT_PROJECT_PYTOOLS_PATH}  
bash ./setup.sh

cd ${BUILDPATH}
cp ./project-CURRENNT-public/README $NSF/currennt/
mv ./project-CURRENNT-public/ ../

# NSF exmaple script
rm -r $BUILDPATH
cd $HOME
git clone https://github.com/nii-yamagishilab/project-CURRENNT-scripts.git
# 環境パスを$HOME/project-CURRENNT-scripts/init.shに追加
cat <<-EOS > $HOME/project-CURRENNT-scripts/init.sh
#!/bin/sh

# PATH to currennt
export TEMP_CURRENNT_PROJECT_CURRENNT_PATH=$NSF/currennt/currennt
# PATH to the pyTools
export TEMP_CURRENNT_PROJECT_PYTOOLS_PATH=$NSF/currennt/pyTools

# PATH to SOX (http://sox.sourceforge.net/sox.html)
export TEMP_CURRENNT_PROJECT_SOX_PATH=/usr/bin/sox

# PATH to SV56 (a software to normalize waveform amplitude.
#  https://www.itu.int/rec/T-REC-P.56 (document)
#  https://www.itu.int/rec/T-REC-G.191-201901-I/en (code)
#  This software is not necessary, I used it because it is available in our lab.
#  You can use other tools to normalize the waveforms before put them into this project.
#  Then, you can set TEMP_CURRENNT_PROJECT_SV56_PATH=None)
export TEMP_CURRENNT_PROJECT_SV56_PATH=None

# Add pyTools to PYTHONPATH
export PYTHONPATH="${TEMP_CURRENNT_PROJECT_PYTOOLS_PATH}:$PYTHONPATH"

# Use currennt with command "currennt [option]"
export PATH="$PATH:$NSF/currennt"
EOS

# Generate sample data
read -p "Do you agree to run sample generate scripts? [y/N]:" ANS

case $ANS in
    [Yy]* )
        cd $HOME/project-CURRENNT-scripts
        echo "Start sample generate scripts."
        source ./init.sh
        cd ./waveform-modeling/project-NSF-pretrained/
        SECONDS=0
        bash ./01_gen.sh
        time1=$SECONDS

        cd ../project-NSF-v2-pretrained/
        SECONDS=0
        bash ./01_gen.sh
        time2=$SECONDS

        cd ../project-WaveNet-pretrained/
        SECONDS=0
        bash ./01_gen.sh
        time3=$SECONDS
        cat <<-EOS
Finish sample generate scripts!
------------------
Taking time
------------------
NSF    : $time1
NSF-v2 : $time2
WaveNet: $time3
------------------
Total  : $((time1 + time2 + time3))
------------------
Output to
------------------
NSF   : $HOME/project-CURRENNT-scripts/waveform-modeling/project-NSF-pretrained/MODELS/NSF/output_trained_network
NSF-v2: $HOME/project-CURRENNT-scripts/waveform-modeling/project-NSF-v2-pretrained/MODELS/h-sinc-NSF/output
Wavnet: $HOME/project-CURRENNT-scripts/waveform-modeling/project-WaveNet-pretrained/MODELS/wavenet001/output
------------------
EOS
        ;;
    *)
    ""
        ;;
esac

cat <<-EOS
Finish build!
---WORNING!!----------------------------------------------------------------------------------------
You must run `source $HOME/project-CURRENNT-scripts/init.sh` before using 'CURRENNT'.
----------------------------------------------------------------------------------------------------
References
CURRENNT                  : $NSF/currennt/README
pyTools of CURRENNT       : $NSF/currennt/pyTools/README
Source code of CURRENNT   : $NSF/project-CURRENNT-public
Sample scripts of CURRENNT: $NSF/project-CURRENNT-scripts/README
EOS

exit 0