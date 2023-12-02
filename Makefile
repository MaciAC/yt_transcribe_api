help: ## Show this help message
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m  %-30s\033[0m %s\n", $$1, $$2}'

## run deps and build
install: deps build

deps: ## download dependencies
	sudo rm -r whisper
	git clone https://github.com/ggerganov/whisper.cpp.git -b v1.4.0 --depth 1 whisper

build: ## Build docker image
	docker build -t app_yt_transcriber .

serve: ## Serve API in 0.0.0.0:80
	docker run -i --rm --name yt_transcribe -p 80:80 -v ./app/data:/code/app/data app_yt_transcriber

serve_gpu: ## Serve API in 0.0.0.0:80 in a docker with access to gpu, only works with nvidia-container-toolkit installed in the host
	docker run -i --rm --gpus all --name yt_transcribe -p 80:80 -v ./app/data:/code/app/data app_yt_transcriber

clean: ## Clean data dir
	rm app/data/*
