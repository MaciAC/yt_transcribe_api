from scrapetube import get_channel
from pytube import YouTube
from os import getcwd
import subprocess


class ChannelManager:
    def __init__(self, channel_name: str):
        self.channel_name = channel_name

    def get_n_latest_video_ids(self, n: int) -> list[str]:
        videos = get_channel(channel_username=self.channel_name, limit=int(n))
        return [v['videoId'] for v in videos]

class VideoManager:
    DATA_PATH = getcwd() + "/data"
    def __init__(self, video_id):
        self.video_id = video_id
        self.yt_instance = YouTube(f"https://www.youtube.com/watch?v={video_id}")
        self.filename_download = f"{video_id}.mp4"
        self.filepath_wav = f"{self.DATA_PATH}/{video_id}.wav"
        self.filepath_txt = f"{self.filepath_wav}.txt"


    def download_youtube_audio(self):
        try:
            audio = self.yt_instance.streams.filter(only_audio=True)[0]
            print(f"Downloading: {self.yt_instance.title}...")
            audio.download(output_path=self.DATA_PATH,
                        filename=self.filename_download)
            print("Download complete!")
        except Exception as e:
            print(f"Error: {str(e)}")

    def convert_audio(self):
        command = "ffmpeg -hide_banner -loglevel error " \
                f"-i '{self.DATA_PATH}/{self.filename_download}' " \
                "-acodec pcm_s16le -ar 16000 -ac 1 " \
                f"'{self.filepath_wav}' -n"
        p2 = subprocess.Popen([command], shell=True)
        out, err = p2.communicate()

    def transcribe_audiofile(self):
        lib_path = "/Users/maciaac/Documents/build/whisper.cpp"
        command = f"{lib_path}/main -m {lib_path}/models/ggml-tiny.en.bin "
        command += f" -f '{self.filepath_wav}' -otxt"
        p2 = subprocess.Popen([command], shell=True)
        out, err = p2.communicate()
        with open(self.filepath_txt, "r") as f:
            self.transcription = f.read()