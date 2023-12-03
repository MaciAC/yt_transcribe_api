# build from alpine
FROM nvidia/cuda:11.6.2-devel-ubuntu20.04

# install needed bin to compile whisper
WORKDIR /usr/local/src
RUN apt update && DEBIAN_FRONTEND=noninteractive apt install -y \
        bash git make vim wget g++ ffmpeg

# whisper.cpp setup

WORKDIR /code/app
RUN git clone https://github.com/ggerganov/whisper.cpp.git -b v1.4.0 --depth 1 whisper
WORKDIR /code/app/whisper
RUN bash ./models/download-ggml-model.sh tiny.en
RUN mv ./models/ggml-tiny.en.bin .
RUN make

# install python and libraries
RUN apt install software-properties-common -y
RUN add-apt-repository ppa:deadsnakes/ppa -y
RUN apt update
RUN apt install python3 pip -y

COPY requirements.txt /code/requirements.txt
COPY app /code/app
WORKDIR /code/app

RUN python3 -m pip install -r /code/requirements.txt

CMD ["python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
