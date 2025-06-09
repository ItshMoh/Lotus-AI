import sounddevice as sd
import numpy as np
import pvcobra
import queue
# import threading
import os
from dotenv import load_dotenv
load_dotenv()
def get_next_audio_frame_sounddevice(cobra_instance, audio_queue):
    """
    Get the next audio frame using sounddevice.
    
    Args:
        cobra_instance: An instance of pvcobra.Cobra
        audio_queue: Queue containing audio frames
    
    Returns:
        numpy.ndarray: Audio frame as 16-bit PCM data
    """
    # Get audio frame from queue (blocks until available)
    print("going to get next audio frame")
    audio_frame = audio_queue.get()
    # print("audio frame",audio_frame)
    
    # Convert float32 to int16 (sounddevice uses float32 by default)
    if audio_frame.dtype == np.float32:
        audio_frame = (audio_frame * 32767).astype(np.int16)
        
    
    return audio_frame.flatten()

def setup_sounddevice_stream(cobra_instance):
    """Setup sounddevice stream with callback."""
    print("goiing to setup sounddevice stream")
    audio_queue = queue.Queue()
    # print("audio queue created",audio_queue)
    def audio_callback(indata, frames, time, status):
        if status:
            print(f"Audio callback status: {status}")
        # Put audio data into queue
        audio_queue.put(indata.copy())
    
    # Start input stream
    stream = sd.InputStream(
        channels=1,
        samplerate=cobra_instance.sample_rate,
        blocksize=cobra_instance.frame_length,
        dtype=np.float32,
        callback=audio_callback
    )
    
    return stream, audio_queue

# Example usage
def main_sounddevice():
    access_key = os.getenv("ACCESS_KEY")
    cobra = pvcobra.create(access_key=access_key)
    
    stream, audio_queue = setup_sounddevice_stream(cobra)
    
    with stream:
        print("Recording with sounddevice...")
        while True:
            try:
                audio_frame = get_next_audio_frame_sounddevice(cobra, audio_queue)
                voice_probability = cobra.process(audio_frame)
                
                if voice_probability > 0.5:
                    print(f"Voice detected! Probability: {voice_probability:.2f}")
                    
            except KeyboardInterrupt:
                break
    
    cobra.delete()

main_sounddevice()    
