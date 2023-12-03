# yt transcribe api

## Description
Technical Test Submission

This submission showcases our use of FastAPI to create an API that utilizes Whisper from OpenAI. The API takes a YouTube video ID as input and returns the video transcription or a channel name and a number and returns the transcription of the last videos of the channel.

For this test, we assumed only English-language videos.

Initially, we implemented Whisper AI in Python but encountered limitations in performance due to unavailable GPU resources. As an improvement strategy, we explored Whisper's C++ implementation (https://github.com/ggerganov/whisper.cpp).

Our primary goal was to create an API capable of handling 10 video transcriptions per minute within a day, while avoiding external resources such as cloud hardware.

While the complete milestone wasn’t achieved, we successfully developed an API that handles up to two parallel request transcriptions. On a MacBook with an M1 chip, the response time for a 5-minute video averages around 15 seconds. However, deploying it within a Docker container on the same Mac resulted in slower responses.

Additionally, we implemented an endpoint that transcribes the latest N videos from a specific channel. Leveraging multiprocessing (utilizing 2 cores), this approach delivers 10 transcriptions from videos averaging 30 minutes in just 6 minutes. This approach does not work well when dockerizing the server.

To further enhance this system's performance, we envision setting up a computation cluster with a master and multiple slaves. The master would manage incoming requests, distributing them among available slaves. This design allows for horizontal scaling by increasing the number of parallel petitions (N) or vertical scaling by adding cores or leveraging GPUs to boost response times.

## Requirements

- docker

or

- python3 and ffmpeg

## Setup

Both options will run the server in local host port 80 (http://127.0.0.1:80)

### Run in a M1 mac

With the repo downloaded go inside it and run:
```bash
make local_setup
```
This will download and compile the c++ whisper implementation and the "tiny" model, then creates a python virtual environment and installs all the required libraries.

Then run this command to start the server.
```bash
make local_serve
```

### Run in a docker container
With the repo downloaded go inside it and run:
```bash
make docker_build
```
This will build a docker image ready to serve the API.

Then run this command to start a container with the server running.
```bash
make docker_serve
```


## Usage

Once the API is running you can check the automatically generated documentation to check the implemented endpoints:
http://127.0.0.1/docs#/default/


## License

[MIT](https://choosealicense.com/licenses/mit/)