FROM ubuntu:16.04

RUN apt-get update && apt-get install -y \
    python3-pip \
    git \
    wrk

ARG MODEL_NAME=identity
WORKDIR /

COPY requirements.txt .
RUN pip3 install -r requirements.txt && rm requirements.txt

RUN git clone -b r1.0 https://github.com/tensorflow/serving.git && \
    cd serving && \
    git submodule update --init -- tensorflow

RUN cd serving && \
    mv tensorflow _tensorflow && mv _tensorflow/tensorflow . && \
    python3 -m grpc.tools.protoc tensorflow_serving/apis/*.proto \
        --python_out=/usr/local/lib/python3.5/dist-packages \
        --grpc_python_out=/usr/local/lib/python3.5/dist-packages \
        --proto_path=. && \
    cd .. && \
    rm -r serving

COPY benchmark_grpc_client.py .

CMD python3 benchmark_grpc_client.py