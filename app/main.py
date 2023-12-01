from fastapi import FastAPI
import whisper
from os import getcwd
import subprocess
import tempfile
from managers import ChannelManager, VideoManager


app = FastAPI()

model = whisper.load_model("tiny")

"time ./main -m models/ggml-tiny.en.bin" \
"-f ~/Documents/build/YT\ transcribe\ API/data/0lS8U6Rq6EY.wav" \
"-otxt ~/Documents/build/YT\ transcribe\ API/data/API/data/0lS8U6Rq6EY.txt"

def run_commands_multiprocess(commands: list[str], silent=True):
    commands_str = '\n'.join(commands)
    command = "printf '{}' | xargs -I % -n 1 -P 5 sh -c '{}'".format(
        commands_str.replace("'", r"'\"'\"'"), '' if silent else 'echo %;'
    )
    p2 = subprocess.Popen(command, shell=True, executable='/bin/bash')
    out, err = p2.communicate()
    print("Completed!")


def transcribe_multiple_audiofiles(paths):
    lib_path = "/Users/maciaac/Documents/build/whisper.cpp"
    command = f"{lib_path}/main -m {lib_path}/models/ggml-tiny.en.bin"
    command += "-f {} -otxt {}"
    comand_list = [command.format(p, p.replace("wav", "txt")) for p in paths]
    fp = tempfile.NamedTemporaryFile()
    fp.write(b"\n".join([bytes(c, 'utf-8') for c in comand_list]))
    fp.close()
    run_commands_multiprocess(fp)


def convert_audio_multiprocess(paths):
    command = "ffmpeg -hide_banner -loglevel error -i '{}' -acodec pcm_s16le -ar 16000 '{}' -n"
    comand_list = [command.format(p, p.replace(".mp4", ".wav")) for p in paths]
    fp = tempfile.NamedTemporaryFile()
    fp.write(bytes("\n".join([c for c in comand_list]), 'utf-8'))
    run_commands_multiprocess(fp)
    fp.close()



@app.get("/video/transcribe/")
def transcribe_video_id(video_id: str):
    v_manager = VideoManager(video_id)
    v_manager.download_youtube_audio()
    v_manager.convert_audio()
    v_manager.transcribe_audiofile()
    return {"video_id": video_id,
            "title": v_manager.yt_instance.title,
            "filename": f"{getcwd()}/data/{v_manager.filename_download}",
            "transcription": v_manager.transcription}

@app.get("/channel/transcribe/")
def transcribe_channel_n_latest_videos(channel_name:str, n:int):
    ch_manager = ChannelManager(channel_name)
    ch_manager.get_n_latest_video_ids(n)
    ch_manager.download_videos_batch()
    ch_manager.convert_videos_batch()
    ch_manager.transcribe_videos_batch()

