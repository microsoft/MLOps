FROM nvidia/cuda:10.0-base-ubuntu16.04

RUN apt-get update \
  && apt-get install -y python3-pip python3-dev \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip

COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
RUN pip install -r requirements.txt

RUN apt-get update && apt-get install -y \
    libboost-python1.58-dev \
    curl \
    libcurl4-openssl-dev

RUN apt-get install -y \
    libatlas-base-dev \
    libopenjp2-7 \
    libtiff-tools \
    i2c-tools \
    libsm6 \
    libxext6 \
    libwebp-dev \
    libpng16-16 \
    libjasper-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libgtk-3-dev \
    libatlas-base-dev \
    gfortran \
    libilmbase-dev \
    libopenexr-dev \
    libgstreamer1.0-dev \
    libqtgui4 \
    libqt4-test 

RUN rm -rf /var/lib/apt/lists/* \
    && apt-get -y autoremove

ADD /app/ .

ENTRYPOINT [ "python3", "-u", "main.py" ]