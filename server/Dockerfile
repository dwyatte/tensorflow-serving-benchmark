FROM ubuntu:16.04

RUN apt-get update && apt-get install -y \
    curl \
    python3-pip

RUN echo "deb [arch=amd64] http://storage.googleapis.com/tensorflow-serving-apt stable tensorflow-model-server tensorflow-model-server-universal" | tee /etc/apt/sources.list.d/tensorflow-serving.list
RUN curl https://storage.googleapis.com/tensorflow-serving-apt/tensorflow-serving.release.pub.gpg | apt-key add -
RUN apt-get update && apt-get install -y tensorflow-model-server

ARG MODEL_NAME=identity
ENV MODEL_PATH=/root/models
ARG SERVING_PORT=8500

WORKDIR /

COPY requirements.txt .
RUN pip3 install -r requirements.txt && rm requirements.txt

COPY create_model.py .
RUN python3 create_model.py $MODEL_PATH/$MODEL_NAME && rm create_model.py

EXPOSE $SERVING_PORT

CMD tensorflow_model_server --port=$SERVING_PORT --model_name=$MODEL_NAME --model_base_path=$MODEL_PATH/$MODEL_NAME --enable_batching=true
