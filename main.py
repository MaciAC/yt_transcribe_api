from fastapi import FastAPI
from pytube import YouTube
import whisper
from os import getcwd
from tqdm import tqdm
import scrapetube
import torch


app = FastAPI()
model = whisper.load_model("tiny")

"./main -f ~/{filename}"

def transcribe_audiofile(paths):
    results = model.transcribe(paths, fp16=False)
    return results

def download_youtube_audio(video_id, output_path):
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    try:
        yt = YouTube(video_url)
        audio = yt.streams.filter(only_audio=True)[0]
        print(f"Downloading: {yt.title}...")
        audio.download(output_path=output_path,
                       filename=f"{video_id}.mp4")
        print("Download complete!")
        return yt.title
    except Exception as e:
        print(f"Error: {str(e)}")


def get_n_video_ids_from_channel_name(channel_name, n):
    print(f"Getting {n} video ids from {channel_name}")
    videos = scrapetube.get_channel(channel_username=channel_name, limit=n)
    return [v['videoId'] for v in videos]


@app.get("/{channel_name}/{n}")
def process_channel(channel_name, n):
    video_ids = get_n_video_ids_from_channel_name(channel_name, int(n))
    response_list = []
    for video_id in tqdm(video_ids):
        filename = f"{video_id}.mp4"
        title = download_youtube_audio(video_id, "data/") + '.mp4'
        response_list.append({"video_id": video_id,
                              "title": title,
                              "filename": f"{getcwd()}/data/{filename}",})
    transcription = transcribe_audiofile([f["filename"] for f in response_list])
    return response_list, transcription

