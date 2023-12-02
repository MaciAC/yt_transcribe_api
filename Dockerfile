# build from alpine
FROM nvidia/cuda:11.6.2-devel-ubuntu20.04

# install needed bin to compile whisper
WORKDIR /usr/local/src
RUN apt update && DEBIAN_FRONTEND=noninteractive apt install -y \
        bash git make vim wget g++ ffmpeg

# get repo
COPY ./whisper /code/whisper

# whisper.cpp setup
WORKDIR /code/whisper
RUN bash ./models/download-ggml-model.sh tiny.en

# quantize a model with Q5_0 method
RUN make quantize
RUN ./quantize models/ggml-tiny.en.bin models/ggml-tiny.en-q5_0.bin q5_0
RUN make

# install python and libraries
RUN apt install software-properties-common -y
RUN add-apt-repository ppa:deadsnakes/ppa -y
RUN apt update
RUN apt install python3 pip -y

COPY ./requirements.txt /code/requirements.txt
COPY ./app /code/app

RUN python3 -m pip install -r /code/requirements.txt

WORKDIR /code/app
CMD ["python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
