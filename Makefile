help: ## Show this help message
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m  %-30s\033[0m %s\n", $$1, $$2}'

deps: ## download dependencies
	git clone https://github.com/ggerganov/whisper.cpp.git --depth 1 whisper

local_setup: ## download model, compile whisper and create venv
	make deps
	cd whisper && bash ./models/download-ggml-model.sh base
	cd whisper && make
	python3 -m venv .venv
	. .venv/bin/activate && python3 -m pip install -r requirements.txt

local_serve: ## Serve API in 0.0.0.0:80
	. .venv/bin/activate && python3 app/main.py

docker_build: ## Build docker image
	docker build -t app_yt_transcriber .

docker_serve: ## Run docker that serve API in 0.0.0.0:80
	docker run -i --rm --name yt_transcribe -p 80:80 -v ./data:/code/data app_yt_transcriber

docker_serve_gpu: ## Run docker that serve API in 0.0.0.0:80 in a docker with access to gpu, only works with nvidia-container-toolkit installed in the host
	docker run -i --rm --gpus all --name yt_transcribe -p 80:80 -v ./app/data:/code/app/data app_yt_transcriber

clean: ## Clean data dir
	rm data/*
