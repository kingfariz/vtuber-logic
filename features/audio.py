import time

import sounddevice as sd
import soundfile as sf

def play_audio(audio_path="output.wav"):
    device_id = 8
    data, sampleRate = sf.read(audio_path)
    print(f"Playing {audio_path}")
    sd.play(data, sampleRate, device=device_id)
    time.sleep(len(data) / sampleRate)
