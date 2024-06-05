from fastapi import FastAPI, HTTPException
from os import getcwd
import time
from managers import ChannelManager, VideoManager
import uvicorn

description = """
# Youtube video transcriber.
## You can
* Transcribe 1 video.
* Transcribe the N last videos of a youtube channel.
"""

app = FastAPI(
    title="YTranscriber",
    description=description,
    version="0.0.1",
)


@app.get("/video/transcribe/")
def transcribe_video_id(video_id: str):
    start_time = time.time()
    v_manager = VideoManager(video_id)
    if not v_manager.yt_instance:
        raise HTTPException(status_code=404, detail="Video id not found")
    if not v_manager.download_youtube_audio():
        raise HTTPException(status_code=500, detail="Not able to download video")
    result = v_manager.transcribe_audiofile()
    if not result:
        raise HTTPException(status_code=500, detail="Not able to transcribe video")
    result['elapsed_time'] = int(time.time() - start_time)
    from pprint import pprint
    pprint(result)
    return result


@app.get("/channel/transcribe/")
def transcribe_channel_n_latest_videos(channel_name:str, n:int):
    start_time = time.time()
    ch_manager = ChannelManager(channel_name)
    if not ch_manager.get_n_latest_video_ids(n):
        raise HTTPException(status_code=404, detail="Channel name not found")
    ch_manager.download_videos_batch()
    results_list = ch_manager.transcribe_videos_batch()
    for i, result in enumerate(results_list):
        if not result:
            results_list[i] = {"video_id": ch_manager.video_ids[i],
                        "error": "There hsa been an error transcribing this video id.",}
    result = {"elapsed_time" : time.time() - start_time,
              "results" : results_list}
    return result


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=80, log_level="info")
