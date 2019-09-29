FROM mcr.microsoft.com/azureml/base-gpu:openmpi3.1.2-cuda10.0-cudnn7-ubuntu16.04

RUN apt-get update && apt-get install -y git curl
RUN apt-get install -y  protobuf-compiler python-pil python-lxml python-tk
COPY requirements.txt /tmp/requirements.txt

RUN ldconfig /usr/local/cuda/lib64/stubs && \
    pip install --no-cache-dir -r /tmp/requirements.txt && \
    ldconfig


ARG TF_DIR=/opt/miniconda/lib/python3.7/site-packages/tensorflow

WORKDIR $TF_DIR

RUN git clone --depth 1 https://github.com/tensorflow/models.git 

# Install pycocoapi
RUN cd / && git clone --depth 1 https://github.com/cocodataset/cocoapi.git && \
    cd cocoapi/PythonAPI && \
    make -j8 && \
    cp -r pycocotools "${TF_DIR}/models/research" && \
    cd ../../ && \
    rm -rf cocoapi

WORKDIR "models/research"
    
RUN curl -OL "https://github.com/google/protobuf/releases/download/v3.0.0/protoc-3.0.0-linux-x86_64.zip" && \
    unzip protoc-3.0.0-linux-x86_64.zip -d proto3 && \
    mv proto3/bin/* /usr/local/bin && \
    mv proto3/include/* /usr/local/include && \
    rm -rf proto3 protoc-3.0.0-linux-x86_64.zip 

# Run protoc on the object detection repo
RUN protoc object_detection/protos/*.proto --python_out=.


# Set the PYTHONPATH to finish installing the API
ENV PYTHONPATH="${TF_DIR}/models/research:${TF_DIR}/models/research/slim:${PYTHONPATH}"

#fall back to default workdir of  base image
WORKDIR /
