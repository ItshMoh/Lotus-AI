import sounddevice as sd
import numpy as np
import pvcheetah
import queue
# import threading
import os
from dotenv import load_dotenv
load_dotenv

cheetah = pvcheetah.create(access_key=os.getenv("ACCESS_KEY"))

sample_rate = cheetah.sample_rate
frame_length = cheetah.frame_length

audio_queue = queue.Queue()

def audio_callback(indata, frames, time, status):
    audio_frame = indata[:,0].astype(np.int16)
    audio_queue.put(audio_frame)

def get_next_audio_frame():
    return audio_queue.get()  

stream = sd.InputStream(channels=1,callback=audio_callback,dtype= 'int16',samplerate=sample_rate,blocksize=frame_length)

stream.start()

try:
    while True:
        audio_frame = get_next_audio_frame()
        # print("audio frame",audio_frame)
        partial_transcript , is_endpoint = cheetah.process(audio_frame)

        if partial_transcript:
            print(partial_transcript)

finally:
    stream.stop()
    stream.close()
    cheetah.delete()
