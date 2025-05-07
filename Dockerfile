FROM nvidia/cuda:11.5.2-devel-ubuntu20.04 AS builder


#GRAPHOS

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC
ENV QT_QPA_PLATFORM=offscreen
ENV XDG_RUNTIME_DIR=/code

# Actualiza el caché del enlazador dinámico
RUN ldconfig

# Sets the versions of the dependencies
ARG OPENCV_VERSION=4.5.4
ARG COLMAP_VERSION=3.7
ARG CGAL_VERSION=v5.5
ARG CERES_VERSION=2.0.0
ARG GDAL_VERSION=3.5
ARG PROJ_VERSION=9.0.0
ARG GLOG_VERSION=0.5.0
ARG OPENMVS_VERSION=2.2.0

ARG INSTALL_PREFIX=/usr/local

# Sets the working directory
WORKDIR /code

# Install dependencies
#RUN apt-get update && apt-get install -y \
#build-essential \
#git \
#ninja-build \
#wget \
#unzip \
#pkg-config \
#libjpeg-dev \	
#libpng-dev \	
#libtiff-dev \ 	
#libwebp-dev \	
#libboost-all-dev \
#libsqlite3-dev \
#sqlite3 && \
#apt-get clean && \
#rm -rf /var/lib/apt/lists/* 

RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    ninja-build \
    wget \
    unzip \
    pkg-config \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libwebp-dev \
    libboost-all-dev \
    libsqlite3-dev \
    sqlite3 \
    libexpat1-dev \
    libfreeimage-dev \
    libflann-dev \
    libmetis-dev \
    libsuitesparse-dev \
    libgflags-dev \
    libglew-dev \
    libgtk-3-dev \
    libgmp-dev \
    libmpfr-dev \
    qtbase5-dev \
    qttools5-dev \
    qttools5-dev-tools \
    qttranslations5-l10n \
    libqt5opengl5-dev \
    curl \
    python3 \
    python3-pip \
    python3-setuptools \
    libopenmpi-dev \
    libhdf5-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Update CMake to version 3.21.4
RUN wget https://github.com/Kitware/CMake/releases/download/v3.21.4/cmake-3.21.4-linux-x86_64.sh && \
    chmod +x cmake-3.21.4-linux-x86_64.sh && \
    ./cmake-3.21.4-linux-x86_64.sh --skip-license --prefix=/usr/local && \
    rm cmake-3.21.4-linux-x86_64.sh

#RUN git clone --branch ${OPENCV_VERSION} https://github.com/opencv/opencv.git /tmp/opencv && \
#    git clone --branch ${OPENCV_VERSION} https://github.com/opencv/opencv_contrib.git /tmp/opencv_contrib && \
#    mkdir -p /tmp/opencv/build && \
#    cd /tmp/opencv/build && \
#    cmake .. -GNinja \
#          -DCMAKE_BUILD_TYPE=Release \
#          -DCMAKE_INSTALL_PREFIX=${INSTALL_PREFIX} \
#          -DOPENCV_EXTRA_MODULES_PATH=/tmp/opencv_contrib/modules \
#          -DWITH_CUDA=ON \
#          -DCUDA_ARCH_BIN="5.0 5.2 6.0 6.1 7.0 7.5 8.0 8.6" \
#          -DCUDA_ARCH_PTX="" \
#          -DENABLE_FAST_MATH=OFF \
#          -DCUDA_FAST_MATH=OFF \
#          -DWITH_CUBLAS=ON \
#          -DWITH_GSTREAMER=OFF \
#          -DWITH_V4L=ON \
#          -DBUILD_opencv_apps=OFF \
#          -DBUILD_opencv_python2=OFF \
#          -DBUILD_opencv_python3=OFF \
#          -DBUILD_JAVA=OFF \   
#          -DBUILD_EXAMPLES=OFF \
#          -DBUILD_TESTS=OFF \
#          -DBUILD_DOCS=OFF \
#          -DBUILD_PERF_TESTS=OFF \
#          -DCMAKE_CXX_FLAGS="-Wno-deprecated-declarations -march=x86-64 -mtune=generic" .. && \     
#    ninja -j2 && \
#    ninja install && \
#    ldconfig && \
#    cd /code && \
#    rm -rf /tmp/opencv /tmp/opencv_contrib
    
RUN git clone --branch ${OPENCV_VERSION} https://github.com/opencv/opencv.git /tmp/opencv && \
    git clone --branch ${OPENCV_VERSION} https://github.com/opencv/opencv_contrib.git /tmp/opencv_contrib && \
    mkdir -p /tmp/opencv/build && \
    cd /tmp/opencv/build && \
    cmake .. -GNinja \
          -DCMAKE_BUILD_TYPE=Release \
          -DCMAKE_INSTALL_PREFIX=${INSTALL_PREFIX} \
          -DOPENCV_EXTRA_MODULES_PATH=/tmp/opencv_contrib/modules \
          -DWITH_CUDA=ON \
          -DCUDA_ARCH_BIN="5.0 5.2 6.0 6.1 7.0 7.5 8.0 8.6" \
          -DCUDA_ARCH_PTX="" \
          -DENABLE_FAST_MATH=OFF \
          -DCUDA_FAST_MATH=OFF \
          -DWITH_CUBLAS=ON \
          -DWITH_GSTREAMER=OFF \
          -DWITH_V4L=ON \
          -DBUILD_opencv_apps=OFF \
          -DBUILD_opencv_aruco=OFF \
          -DBUILD_opencv_bgsegm=OFF \
          -DBUILD_opencv_bioinspired=OFF \
          -DBUILD_opencv_calib3d=ON \
          -DBUILD_opencv_ccalib=OFF \
          -DBUILD_opencv_core=ON \
          -DBUILD_opencv_datasets=OFF \
          -DBUILD_opencv_cudaarithm=ON \
          -DBUILD_opencv_cudabgsegm=OFF \
          -DBUILD_opencv_cudacodec=OFF \
          -DBUILD_opencv_cudafeatures=ON \
          -DBUILD_opencv_cudafilters=ON \
          -DBUILD_opencv_cudaimgproc=ON \
          -DBUILD_opencv_cudalegacy=ON \
          -DBUILD_opencv_cudaobjdetect=OFF \
          -DBUILD_opencv_cudaoptflow=OFF \
          -DBUILD_opencv_cudastereo=OFF \
          -DBUILD_opencv_cudawarping=ON \
          -DBUILD_opencv_cudev=ON \
          -DBUILD_opencv_dnn=ON \
          -DBUILD_opencv_dnn_objdetect=OFF \
          -DBUILD_opencv_dnn_superres=OFF \
          -DBUILD_opencv_dpm=OFF \
          -DBUILD_opencv_face=OFF \
          -DBUILD_opencv_features=ON \
          -DBUILD_opencv_flann=ON \
          -DBUILD_opencv_fuzzy=OFF \
          -DBUILD_opencv_gapi=OFF \
          -DBUILD_opencv_hfs=OFF \
          -DBUILD_opencv_highgui=ON \
          -DBUILD_opencv_img_hash=OFF \
          -DBUILD_opencv_imgcodecs=ON \
          -DBUILD_opencv_imgproc=ON \
          -DBUILD_opencv_intensity_transform=OFF \
          -DBUILD_opencv_line_descriptor=OFF \
          -DBUILD_opencv_mcc=OFF \
          -DBUILD_opencv_ml=OFF \
          -DBUILD_opencv_objc_bindings_generator=OFF \
          -DBUILD_opencv_objdetect=ON \
          -DBUILD_opencv_optflow=OFF \
          -DBUILD_opencv_phase_unwrapping=OFF \
          -DBUILD_opencv_photo=ON \
          -DBUILD_opencv_plot=OFF \
          -DBUILD_opencv_python_bindings_generator=OFF \
          -DBUILD_opencv_python_tests=OFF \
          -DBUILD_opencv_quality=OFF \
          -DBUILD_opencv_rapid=OFF \
          -DBUILD_opencv_reg=OFF \
          -DBUILD_opencv_rgbd=OFF \
          -DBUILD_opencv_saliency=OFF \
          -DBUILD_opencv_shape=ON \
          -DBUILD_opencv_signal=OFF \
          -DBUILD_opencv_stereo=OFF \
          -DBUILD_opencv_stitching=ON \
          -DBUILD_opencv_structured_light=OFF \
          -DBUILD_opencv_superres=OFF \
          -DBUILD_opencv_surface_matching=OFF \
          -DBUILD_opencv_text=OFF \
          -DBUILD_opencv_tracking=OFF \
          -DBUILD_opencv_ts=OFF \
          -DBUILD_opencv_video=ON \
          -DBUILD_opencv_videoio=ON \
          -DBUILD_opencv_videostab=OFF \
          -DBUILD_opencv_wechat_qrcode=OFF \
          -DBUILD_opencv_world=OFF \
          -DBUILD_opencv_xfeatures2d=ON \
          -DBUILD_opencv_python2=OFF \
          -DBUILD_opencv_python3=OFF \
          -DBUILD_JAVA=OFF \
          -DBUILD_TESTS=OFF \
          -DBUILD_PERF_TESTS=OFF \
          -DCMAKE_CXX_FLAGS="-Wno-deprecated-declarations -march=x86-64 -mtune=generic" .. && \
    ninja -j2 && \
    ninja install && \
    ldconfig && \
    cd /code && \
    rm -rf /tmp/opencv /tmp/opencv_contrib

# Build and install fmt 10
RUN git clone --branch 10.0.0 https://github.com/fmtlib/fmt.git /tmp/fmt && \
    cd /tmp/fmt && \
    mkdir build && \
    cd build && \
    cmake .. -GNinja \
          -DCMAKE_BUILD_TYPE=Release \
          -DCMAKE_INSTALL_PREFIX=${INSTALL_PREFIX} \
          -DFMT_TEST=OFF \
          -DFMT_DOC=OFF && \		  
    ninja && \
    ninja install && \
	ldconfig && \
    cd /code && \
    rm -rf /tmp/fmt

# Build and install PROJ
RUN wget https://download.osgeo.org/proj/proj-${PROJ_VERSION}.tar.gz && \
    tar -xvf proj-${PROJ_VERSION}.tar.gz && \
    cd proj-${PROJ_VERSION} && \
    mkdir build && \
    cd build && \
    cmake .. -GNinja \
          -DCMAKE_BUILD_TYPE=Release \
          -DCMAKE_INSTALL_PREFIX=${INSTALL_PREFIX} \
          -DBUILD_TESTING=OFF \
          -DENABLE_CURL=OFF \
          -DBUILD_PROJSYNC=OFF && \
    ninja && \
    ninja install && \
    ldconfig && \
    cd /code && rm -rf proj-${PROJ_VERSION} proj-${PROJ_VERSION}.tar.gz

# Install the proj-data (grid and database files)
RUN wget https://download.osgeo.org/proj/proj-data-1.15.tar.gz && \
    mkdir proj-data-1.15 && \
    tar -xvf proj-data-1.15.tar.gz -C proj-data-1.15 && \
    cp -r proj-data-1.15/* ${INSTALL_PREFIX}/share/ && \
    rm -rf proj-data-1.15 proj-data-1.15.tar.gz

# Build and install GDAL
RUN git clone --branch release/${GDAL_VERSION} https://github.com/OSGeo/gdal.git /tmp/gdal && \
    cd /tmp/gdal && \
    mkdir build && \ 
    cd build && \
    cmake .. -GNinja \
          -DCMAKE_BUILD_TYPE=Release \
          -DCMAKE_INSTALL_PREFIX=${INSTALL_PREFIX} \
          -DBUILD_TESTING=OFF \        
          -DBUILD_APPS=OFF && \  
    ninja && \
    ninja install && \
    cd /code && \
    rm -rf /tmp/gdal
	
# EIGEN
RUN git clone --branch 3.4 https://gitlab.com/libeigen/eigen.git /tmp/eigen && \
    cd /tmp/eigen && \
    mkdir build && \ 
    cd build && \
    cmake .. -GNinja \
          -DCMAKE_BUILD_TYPE=Release \
          -DCMAKE_INSTALL_PREFIX=${INSTALL_PREFIX} \
          -DBUILD_TESTING=OFF \   
          -DEIGEN_BUILD_TESTING=OFF \  
          -DBUILD_APPS=OFF && \  
    ninja && \
    ninja install && \
    cd /code && \
    rm -rf /tmp/eigen

#RUN apt-get update && apt-get install -y \
#	libexpat1-dev \
#	libfreeimage-dev \
#    libflann-dev \	
#    libmetis-dev \
#    libsuitesparse-dev \
#    libgflags-dev \	
#    libglew-dev \
#    libgtk-3-dev \	
#    libgmp-dev \
#    libmpfr-dev \		
#    qtbase5-dev \
#    qttools5-dev \
#    qttools5-dev-tools \
#    qttranslations5-l10n \
#    libqt5opengl5-dev \	
#    && apt-get clean \	
#    && rm -rf /var/lib/apt/lists/*

# Build and install glog
RUN git clone https://github.com/google/glog.git /tmp/glog && \
    cd /tmp/glog && \
    git checkout v${GLOG_VERSION} && \
    mkdir build && \
    cd build && \
    cmake .. -DCMAKE_INSTALL_PREFIX=${INSTALL_PREFIX} \ 
             -DBUILD_TESTING=OFF \
             -DBUILD_SHARED_LIBS=OFF && \
    make -j$(nproc) && \
    make install && \
    cd /code && rm -rf /tmp/glog

	
# Build and install Ceres Solver
RUN git clone https://ceres-solver.googlesource.com/ceres-solver /tmp/ceres-solver && \
    cd /tmp/ceres-solver && \
    git checkout tags/${CERES_VERSION} && \
    mkdir build && \
    cd build && \
    cmake .. -GNinja \
          -DBUILD_TESTING=OFF \
          -DBUILD_EXAMPLES=OFF \
          -DCMAKE_INSTALL_PREFIX=${INSTALL_PREFIX} && \
    ninja && \
    ninja install && \
    cd /code && rm -rf /tmp/ceres-solver
	
	
# Build and install CGAL
RUN git clone https://github.com/CGAL/cgal.git /tmp/cgal && \
    cd /tmp/cgal && \
    git fetch https://github.com/CGAL/cgal.git ${CGAL_VERSION} && \
    git checkout FETCH_HEAD && \
    mkdir build && \
    cd build && \
    cmake .. -GNinja \
          -DBUILD_TESTING=OFF \	
          -DBUILD_DOC=OFF \	
          -DWITH_tests=OFF \	
          -DWITH_demos=OFF \	
          -DWITH_examples=OFF \	
          -DCMAKE_INSTALL_PREFIX=${INSTALL_PREFIX} && \
    ninja && \
    ninja install && \
	ldconfig && \
    cd /code && rm -rf /tmp/cgal
	
# Build and install COLMAP
RUN git clone https://github.com/colmap/colmap.git /tmp/colmap && \
    cd /tmp/colmap && \
    git fetch https://github.com/colmap/colmap.git ${COLMAP_VERSION} && \
    git checkout FETCH_HEAD && \
    mkdir build && \
    cd build && \
    cmake .. -GNinja -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_CUDA_ARCHITECTURES="5.0;5.2;6.0;6.1;7.0;7.5;8.0;8.6" \ 
    -DCMAKE_INSTALL_PREFIX=${INSTALL_PREFIX} \
    && ninja -j2 && \
    ninja install && \
    cd /code && rm -rf /tmp/colmap

# Build and install PoissonRecon
RUN git clone https://github.com/mkazhdan/PoissonRecon.git /tmp/PoissonRecon && \
    cd /tmp/PoissonRecon && \
	git checkout 19a8cbd && \
    make -j$(nproc) poissonrecon && \
    make -j$(nproc) surfacetrimmer && \
    cp Bin/Linux/PoissonRecon ${INSTALL_PREFIX}/bin/ && \
    cp Bin/Linux/SurfaceTrimmer ${INSTALL_PREFIX}/bin/ && \
    cd /code && rm -rf /tmp/PoissonRecon

# Install VCG
RUN git clone https://github.com/cdcseacave/VCG.git /tmp/vcglib && \
    mkdir -p ${INSTALL_PREFIX}/vcglib && \
    cp -r /tmp/vcglib/* ${INSTALL_PREFIX}/vcglib && \
    rm -rf /tmp/vcglib
	
	
# Build and install OpenMVS
RUN git clone https://github.com/cdcseacave/openMVS.git /tmp/openMVS && \
    cd /tmp/openMVS && \
	git checkout tags/v${OPENMVS_VERSION} && \
    mkdir _build && \
    cd _build && \
    cmake .. -DCMAKE_BUILD_TYPE=Release \
             -DCMAKE_INSTALL_PREFIX="${INSTALL_PREFIX}" \
             -DVCG_DIR="${INSTALL_PREFIX}/vcglib" \	
             -DCUDA_CUDA_LIBRARY=/usr/local/cuda-11.5/lib64/stubs/libcuda.so \			 
             -DOpenMVS_MAX_CUDA_COMPATIBILITY=ON \
             -DBUILD_TESTING=OFF \
             -DBUILD_SHARED_LIBS=OFF && \
    make -j2 && \
    make install && \
    cd /code && rm -rf /tmp/openMVS

# Build and install tidoplib
#RUN git clone --branch dev_3.1 https://github.com/TIDOP-USAL/tidoplib.git /tmp/tidoplib && \
#    cd /tmp/tidoplib && \
#    mkdir build && \
#    cd build && \
#    cmake .. -GNinja  \
#          -DCMAKE_BUILD_TYPE=Release \
#          -DCMAKE_INSTALL_PREFIX=${INSTALL_PREFIX} \
#          -DWITH_OPENCV=ON \
#          -DWITH_GDAL=ON \
#          -DWITH_PROJ=ON \
#          -DBUILD_APPS=OFF \
#          -DBUILD_TEST=OFF \
#          -DBUILD_DOC=OFF \
#          -DWITH_CUDA=ON \
#          -DTIDOPLIB_USE_SIMD_INTRINSICS=ON \
#          -DTIDOPLIB_CXX_STANDARD=C++14 && \
#    ninja && \
#    ninja install && \
#    cd /code && rm -rf /tmp/tidoplib	

RUN git clone https://github.com/hobuinc/laz-perf.git  /tmp/laz-perf && \
    cd /tmp/laz-perf && \
    mkdir build && cd build && \
    cmake .. -GNinja  \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX="${INSTALL_PREFIX}" && \
    ninja && \
    ninja install && \
    cd /code && rm -rf /tmp/laz-perf

RUN git clone https://github.com/RockRobotic/copc-lib.git  /tmp/copc-lib && \
    cd /tmp/copc-lib && \
    mkdir build && \
    cd build && \
    cmake .. -GNinja  \
             -DCMAKE_BUILD_TYPE=Release \
             -DCMAKE_INSTALL_PREFIX="${INSTALL_PREFIX}" && \
    ninja && \
    ninja install && \
    cd /code && rm -rf /tmp/copc-lib

#RUN git clone https://github.com/PDAL/PDAL.git /tmp/PDAL && \
#    cd /tmp/PDAL && \
#    git checkout 2.8.0 && \
#    mkdir build && \
#    cd build && \
#    cmake .. -GNinja  \
#             -DCMAKE_BUILD_TYPE=Release \
#             -DCMAKE_INSTALL_PREFIX="${INSTALL_PREFIX}" \
#             -DWITH_TESTS=OFF && \
#    ninja && \
#    ninja install && \
#    cd /code && rm -rf /tmp/PDAL

# Build and install LASzip
RUN wget https://github.com/LASzip/LASzip/archive/0069c42307183c49744f1eb170f7032a8cf6a9db.zip -O laszip.zip && \
    unzip laszip.zip && \
    mv LASzip-* /tmp/laszip && \
    cd /tmp/laszip && \
    mkdir build && \
    cd build && \
    cmake .. -GNinja  \
          -DBUILD_SHARED_LIBS=ON \
          -DBUILD_STATIC_LIBS=OFF \
          -DCMAKE_INSTALL_PREFIX=${INSTALL_PREFIX} && \
    ninja && \
    ninja install && \
    cd /code && rm -rf /tmp/laszip

RUN apt-get update && apt-get install -y libgeotiff-dev libssl-dev libcurl4-openssl-dev libzstd-dev

RUN git clone https://github.com/PDAL/PDAL.git /tmp/PDAL && \
    cd /tmp/PDAL && \
    git checkout 2.8.0 && \
    mkdir build && \
    cd build && \
    cmake .. -GNinja  \
             -DCMAKE_BUILD_TYPE=Release \
             -DCMAKE_INSTALL_PREFIX="${INSTALL_PREFIX}" \
             -DWITH_APPS=ON \
             -DWITH_LAZPERF=ON \
             -DWITH_GEOTIFF=ON \             
             -DWITH_TESTS=OFF && \
    ninja && \
    ninja install && \
    cd /code && rm -rf /tmp/PDAL

# Build and install PDAL.
#RUN git clone --no-checkout https://github.com/PDAL/PDAL.git /tmp/pdal && \
#    cd /tmp/pdal && \
#    git checkout 2.1.0  && \
#    mkdir build && \
#    cd build && \
#    cmake .. -GNinja  \
#          -DCMAKE_BUILD_TYPE=Release \
#          -DWITH_TEST=OFF \
#          -DCMAKE_INSTALL_PREFIX=${INSTALL_PREFIX}  \
#          -DBUILD_PGPOINTCLOUD_TESTS=OFF \
#          -DBUILD_PLUGIN_PGPOINTCLOUD=OFF \
#          -DBUILD_PLUGIN_CPD=OFF \
#          -DBUILD_PLUGIN_GREYHOUND=OFF \
#          -DBUILD_PLUGIN_HEXBIN=ON \
#          -DBUILD_PLUGIN_ICEBRIDGE=OFF \
#          -DBUILD_PLUGIN_MRSID=OFF \
#          -DBUILD_PLUGIN_NITF=OFF \
#          -DBUILD_PLUGIN_OCI=OFF \
#          -DBUILD_PLUGIN_P2G=OFF \
#          -DBUILD_PLUGIN_SQLITE=OFF \
#          -DBUILD_PLUGIN_RIVLIB=OFF \
#          -DBUILD_PLUGIN_PYTHON=OFF \
#          -DWITH_ZSTD=OFF \
#          -DENABLE_CTEST=OFF \
#          -DWITH_APPS=ON \
#          -DWITH_LAZPERF=ON \
#          -DWITH_GEOTIFF=ON \
#          -DLASZIP_FOUND=TRUE \
#          -DWITH_LASZIP=ON \
#          -DLASZIP_VERSION=3.1.1 \
#          -DLASZIP_LIBRARIES=${INSTALL_PREFIX}/lib/liblaszip.so \
#          -DLASZIP_INCLUDE_DIR=${INSTALL_PREFIX}/include/laszip \
#          -DLASZIP_LIBRARY=${INSTALL_PREFIX}/lib/liblaszip.so && \
#    ninja && \
#    ninja install  && \
#    cd /code && rm -rf /tmp/pdal	

RUN git clone https://github.com/TIDOP-USAL/tidoplib.git /tmp/tidoplib && \
    cd /tmp/tidoplib && \
    git checkout 3.2.1 && \ 
    mkdir build && \
    cd build && \
    cmake .. -GNinja  \
          -DCMAKE_BUILD_TYPE=Release \
          -DCMAKE_INSTALL_PREFIX=${INSTALL_PREFIX} \
          -DWITH_OPENCV=ON \
          -DWITH_GDAL=ON \
          -DWITH_PROJ=ON \
          -DBUILD_TL_FEAT_MATCH=OFF \
          -DBUILD_APPS=OFF \
          -DBUILD_TEST=OFF \
          -DBUILD_DOC=OFF \
          -DWITH_CUDA=ON \
          -DTIDOPLIB_USE_SIMD_INTRINSICS=ON \
          -DTIDOPLIB_CXX_STANDARD=C++14 && \
    ninja && \
    ninja install && \
    cd /code && rm -rf /tmp/tidoplib	

# Build and install entwine
#RUN git clone --branch 290 --depth 1 https://github.com/OpenDroneMap/entwine /tmp/entwine && \
#    cd /tmp/entwine && \
#    mkdir build && \
#    cd build && \
#    cmake .. -GNinja \
#          -DCMAKE_INSTALL_PREFIX=${INSTALL_PREFIX} \
#	      -DWITH_TESTS=OFF \
#          -DWITH_ZSTD=OFF \ 
#	      -DCMAKE_BUILD_TYPE=Release && \
#    ninja && \
#    ninja install && \
#    cd /code && rm -rf /tmp/entwine	

RUN git clone https://github.com/connormanning/entwine /tmp/entwine && \
    cd /tmp/entwine && \
    git checkout tags/3.1.1 && \ 
    mkdir build && \
    cd build && \
    cmake .. -GNinja \
        -DCMAKE_INSTALL_PREFIX=${INSTALL_PREFIX} \
        -DWITH_TESTS=OFF \
        -DWITH_ZSTD=OFF \ 
        -DCMAKE_BUILD_TYPE=Release && \
    ninja && \
    ninja install && \
    cd /code && rm -rf /tmp/entwine	

# Build and install graphos
RUN git clone --branch dev https://github.com/TIDOP-USAL/graphos.git /tmp/graphos && \
    cd /tmp/graphos && \
    mkdir build && \
    cd build && \
    cmake .. -GNinja  \
          -DCMAKE_BUILD_TYPE=Release \
          -DCMAKE_INSTALL_PREFIX=${INSTALL_PREFIX} \
          -DBUILD_GUI=OFF \
          -DBUILD_TRANSLATION=OFF \
          -DBUILD_ORTHOPHOTO_COMPONENT=ON \
          -DWITH_CUDA=ON && \
    ninja -j4 && \
    ninja install && \
    cd /code && rm -rf /tmp/graphos	    

RUN git clone https://github.com/OpenDroneMap/ODM.git /tmp/odm && \
    cp -r /tmp/odm/opendm/ /code/ && \
    cp /tmp/odm/settings.yaml /code/ && \
    cp /tmp/odm/requirements.txt /code/ && \
    rm -rf /tmp/odm


FROM nvidia/cuda:11.5.2-runtime-ubuntu20.04
#FROM nvidia/cuda:11.5.2-devel-ubuntu20.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC
ENV QT_QPA_PLATFORM=offscreen
ENV XDG_RUNTIME_DIR=/code
ENV PATH="$PATH:/usr/local/bin"
ENV GDAL_DATA=/usr/local/share/gdal
ENV PROJ_LIB=/usr/local/share/proj
ENV GRAPHOS_PROJ=/usr/local/share/proj
ENV GRAPHOS_GDAL=/usr/local/share/gdal

RUN apt-get update && apt-get install -y \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libwebp-dev \
    libboost-all-dev \
    libsqlite3-dev \
    libexpat1-dev \
    libfreeimage-dev \
    libflann-dev \
    libmetis-dev \
    libsuitesparse-dev \
    libgflags-dev \
    libglew-dev \
    libgtk-3-dev \
    libgmp-dev \
    libmpfr-dev \
    qtbase5-dev \
    qttools5-dev \
    qttools5-dev-tools \
    qttranslations5-l10n \
    libqt5opengl5-dev \
    curl \
    libhdf5-dev \
    python3 \
    python3-pip \
    python3-setuptools \
    libgeotiff-dev \
    libssl-dev \ 
    libcurl4-openssl-dev \
    libzstd-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /code

COPY --from=builder /code /code
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /usr/local/lib/*.so* /usr/local/lib/
#COPY --from=builder /usr/local/lib /usr/local/lib
#COPY --from=builder /usr/local/include /usr/local/include
COPY --from=builder /usr/local/share /usr/local/share

RUN ldconfig

#COPY start_graphos.sh /usr/local/bin/start_graphos.sh
#COPY start_graphos.sh /var/www/start_graphos.sh
#RUN chmod +x /usr/local/bin/start_graphos.sh
#RUN chmod +x /var/www/start_graphos.sh



#COPY graphos/VERSION /code
#COPY graphos/run.sh /code
#COPY graphos/run.py /code
#COPY graphos/odm_options.json /code

#ODM

#RUN mkdir -p /code/opendm
#RUN mkdir -p /code/stages
#RUN git clone https://github.com/OpenDroneMap/ODM.git /tmp/odm
#RUN cp -r /tmp/odm/opendm /code/ && \
#    cp -r /tmp/odm/stages /code/ && \
#    rm -rf /tmp/odm

#RUN git clone https://github.com/OpenDroneMap/ODM.git /tmp/odm && \
#    cp -r /tmp/odm/opendm/ /code/ && \
#    cp /tmp/odm/settings.yaml /code/ && \
#    rm -rf /tmp/odm

#RUN apt-get update && apt-get install -y curl python3 python3-pip python3-setuptools

RUN pip3 install -U shyaml
#Para ODM
RUN pip install -r /code/requirements.txt

COPY graphos/VERSION /code
COPY graphos/run.sh /code
COPY graphos/run.py /code
COPY graphos/odm_options.json /code

RUN chmod +x /code/run.sh

EXPOSE 3000

# Esto creo que utiliza la imagen de ODM
#USER root
#RUN apt-get update && apt-get install -y curl gpg-agent
#RUN curl --silent --location https://deb.nodesource.com/setup_14.x | bash -
#RUN apt-get install -y nodejs unzip p7zip-full && npm install -g nodemon && \
#    ln -s /code/SuperBuild/install/bin/untwine /usr/local/bin/untwine && \
#    ln -s /code/SuperBuild/install/bin/entwine /usr/local/bin/entwine && \
#    ln -s /code/SuperBuild/install/bin/pdal /usr/local/bin/pdal

WORKDIR /var/www
COPY . /var/www

#RUN apt-get update && apt-get install -y curl python3 python3-pip python3-setuptools

#RUN pip3 install -U shyaml
#Para ODM
#RUN pip install -r /code/requirements.txt

RUN curl --silent --location https://deb.nodesource.com/setup_14.x | bash -
RUN apt-get install -y nodejs unzip p7zip-full && npm install -g nodemon
RUN npm install --production && mkdir -p tmp

RUN ln -s "$(which python3)" /usr/bin/python
ENV python="$(which python3)"

ENTRYPOINT ["/usr/bin/node", "/var/www/index.js"]
#ENTRYPOINT ["/bin/bash"]