FROM nvidia/cuda:10.0-devel-ubuntu18.04

ENV BUILDPATH /home/builds
WORKDIR ${BUILDPATH}

ENV BOOST /usr/local/boost
ENV HDF5 /usr/local/hdf5
ENV NETCDF /usr/local/netcdf
ENV NSF /usr/local/nsf
ENV PYTHONPATH=${PYTHONPATH}:/usr/local/nsf/pyTools
ENV SZLIB /usr/local/szlib
ENV TEMP_CURRENNT_PROJECT_CURRENNT_PATH /usr/local/nsf/currennt
ENV TEMP_CURRENNT_PROJECT_PYTOOLS_PATH /usr/local/nsf/pyTools
ENV TEMP_CURRENNT_PROJECT_SOX_PATH /usr/bin/sox
ENV TEMP_CURRENNT_PROJECT_SV56_PATH None

ENV VER_BOOST 1.59.0
ENV VER_HDF5 1.10.6
ENV VER_NETCDF 4.3.3.1
ENV VER_SZIP 2.1.1
ENV VER_ZLIB 1.2.11

ARG DOCKER_UID=1000
ARG DOCKER_USER=docker
ARG DOCKER_PASSWORD=docker

SHELL ["/bin/bash", "-c"]

RUN apt update && apt -y upgrade && \
    apt install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        cmake \
        git \ 
        libpthread-stubs0-dev \ 
        m4 \ 
        ninja-build \ 
        sox \ 
        sudo \ 
        wget && \
    wget https://repo.anaconda.com/miniconda/Miniconda3-py37_4.8.2-Linux-x86_64.sh -O ./miniconda.sh && \
    bash ./miniconda.sh -b -p /opt/conda && \
    /opt/conda/bin/conda clean -tipsy && \
    ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
    echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc && \
    rm ./miniconda.sh && \
    /opt/conda/bin/conda install -y Cython numpy==1.16.4 scipy && \
    /opt/conda/bin/conda install -c conda-forge librosa pip tqdm && \
    /opt/conda/bin/conda clean -ya

RUN export JOBS=$[$(grep cpu.cores /proc/cpuinfo | sort -u | sed 's/[^0-9]//g')+1] && \
    wget http://sourceforge.net/projects/boost/files/boost/${VER_BOOST}/boost_${VER_BOOST//./_}.tar.gz \
         https://support.hdfgroup.org/ftp/HDF5/releases/hdf5-$(echo ${VER_HDF5}|rev|cut -c 3-|rev)/hdf5-${VER_HDF5}/src/hdf5-${VER_HDF5}.tar.gz \
         https://github.com/Unidata/netcdf-c/archive/v${VER_NETCDF}.tar.gz \
         https://support.hdfgroup.org/ftp/lib-external/szip/${VER_SZIP}/src/szip-${VER_SZIP}.tar.gz \
         http://www.zlib.net/zlib-${VER_ZLIB}.tar.gz && \
    find ./*.tar.gz | xargs -n 1 tar -xf && \
    cd $(find ${BUILDPATH} -name "zlib-${VER_ZLIB}" -type d) && \
    ./configure --prefix=${SZLIB} && make -j${JOBS} && make install && \
    cd $(find ${BUILDPATH} -name "szip-${VER_SZIP}" -type d) && \
    ./configure --prefix=${SZLIB} && make -j${JOBS} && make install && \
    cd $(find ${BUILDPATH} -name "hdf5-${VER_HDF5}" -type d) && \
    ./configure --prefix=${HDF5} --with-szlib=${SZLIB} --enable-threadsafe --with-pthread=/usr/include/,/usr/lib/x86_64-linux-gnu/ --enable-hl --enable-shared --enable-unsupported && \
    make -j${JOBS} && make install && \
    cd $(find ${BUILDPATH} -name "netcdf-c-${VER_NETCDF}" -type d) && \
    ./configure --disable-netcdf-4 --prefix=${NETCDF} && make -j${JOBS} && make install && \
    cd $(find ${BUILDPATH} -name "boost_${VER_BOOST//./_}" -type d) && \
    ./bootstrap.sh --with-libraries=program_options,filesystem,system,random,thread && \
    ./b2 install --prefix=${BOOST}

ENV PATH /opt/conda/bin:$PATH

RUN git clone https://github.com/nii-yamagishilab/project-CURRENNT-public.git && \
    cd project-CURRENNT-public/CURRENNT_codes && mkdir build && cd build && \
    cmake .. -DCMAKE_BUILD_TYPE=Release -DBOOST_ROOT=${BOOST} -DNETCDF_LIB=${NETCDF}/lib && \
    make -j${JOBS} && mkdir ${NSF} && \
    mv ./currennt ${NSF} && mv ../../pyTools/ ${NSF} && \
    cd ${TEMP_CURRENNT_PROJECT_PYTOOLS_PATH} && export PYTHONPATH=$(pwd):$PYTHONPATH && \
    bash ./setup.sh

WORKDIR /home/docker

RUN rm -r ${BUILDPATH} && \
    git clone https://github.com/nii-yamagishilab/project-CURRENNT-scripts.git && \
    mkdir ./project-CURRENNT-scripts/audio

WORKDIR /home/docker/project-CURRENNT-scripts


