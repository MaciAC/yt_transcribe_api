from scrapetube import get_channel
from pytube import YouTube, exceptions
from os import getcwd
import subprocess
import threading
import multiprocessing
from json.decoder import JSONDecodeError
from pandas import read_csv


class ChannelManager:
    def __init__(self, channel_name: str):
        self.channel_name = channel_name

    def get_n_latest_video_ids(self, n: int):
        try:
            videos = get_channel(channel_username=self.channel_name, limit=int(n))
            self.video_ids = [video['videoId'] for video in videos]
            return True
        except JSONDecodeError:
            return False

    def download_videos_batch(self):
        tasks = []
        for video_id in self.video_ids:
            v_manager = VideoManager(video_id)
            tasks.append(threading.Thread(target=v_manager.download_youtube_audio()))
            tasks[-1].start()
            tasks[-1].join()

    def convert_videos_batch(self):
        tasks = []
        for video_id in self.video_ids:
            v_manager = VideoManager(video_id)
            tasks.append(threading.Thread(target=v_manager.convert_audio()))
            tasks[-1].start()
        for task in tasks:
            task.join()

    def transcribe_videos_batch(self):
        v_manager = VideoManager()
        with multiprocessing.Pool(processes=2) as pool:
            # Run the function in parallel using the pool.map() function
            results = pool.map(v_manager.transcribe_audiofile, self.video_ids)
        return results


class VideoManager:
    DATA_PATH = getcwd() + "/data"
    def __init__(self, video_id=None):
        if not video_id:
            return
        self.video_id = video_id
        self.filename_download = f"{video_id}.mp4"
        self.filepath_wav = f"{self.DATA_PATH}/{video_id}.wav"
        self.filepath_csv = f"{self.filepath_wav}.csv"
        try:
            self.yt_instance = YouTube(f"https://www.youtube.com/watch?v={video_id}")
        except exceptions.RegexMatchError:
            self.yt_instance = None


    def download_youtube_audio(self):
        try:
            audio = self.yt_instance.streams.filter(only_audio=True)[0]
            audio.download(output_path=self.DATA_PATH,
                        filename=self.filename_download)
            return True
        except Exception as e:
            print(f"Error: {str(e)}")
            return False


    def convert_audio(self):
        command = "ffmpeg -hide_banner -loglevel error -y " \
                f"-i '{self.DATA_PATH}/{self.filename_download}' " \
                "-acodec pcm_s16le -ar 16000 -ac 2 " \
                f"'{self.filepath_wav}'"
        print(command)
        p2 = subprocess.Popen([command], shell=True)
        out, err = p2.communicate()

    def transcribe_audiofile(self, video_id=None):
        if video_id:
            self.__init__(video_id)
        self.convert_audio()
        lib_path = getcwd() + "/whisper"
        command = f"'{lib_path}/main' -m '{lib_path}/models/ggml-base.bin' -l es -ocsv -ml 1 -sow -f '{self.filepath_wav}'"
        p2 = subprocess.Popen([command], shell=True)
        out, err = p2.communicate()
        try:
            df = read_csv(self.filepath_csv, delimiter=',', quotechar='"', escapechar='\\')
            word_offsets = [{"s": start, "e": end, "w": word} for start, end, word in zip(df['start'], df['end'], df['text']) if start != end]
            from pprint import pprint
            pprint(word_offsets)
            return {
                "video_id": self.video_id,
                "title": self.yt_instance.title,
                "results": {
                    "words": word_offsets,
                    "transcript": "".join(df['text'].astype(str).tolist()),
                }
            }
        except Exception as e:
            print(f"Error transcribing: {e}")
            return False