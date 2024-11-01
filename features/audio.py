import time

import sounddevice as sd
import soundfile as sf

from dotenv import load_dotenv
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
import os
from io import BytesIO
from typing import IO

load_dotenv()
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

def play_audio(audio_path="output.wav"):
    device_id = 8
    data, sampleRate = sf.read(audio_path)
    print(f"Playing {audio_path}")
    sd.play(data, sampleRate, device=device_id)
    time.sleep(len(data) / sampleRate)

def play_audio_english(message:str):
    response = client.text_to_speech.convert(
        voice_id="cTbfi6ZqvC5uwRC0447E",
        text=message,
        model_id="eleven_turbo_v2_5",
        voice_settings=VoiceSettings(
            stability = 0.0,
            similarity_boost = 0.9,
            # style: trade-off: might cause higher latency for higher style
            style=0.0,
        ),
    )
    audio_stream = BytesIO()
    for chunk in response:
        if chunk:
            audio_stream.write(chunk)

    audio_stream.seek(0)
    
    data,sampleRate = sf.read(audio_stream)
    device_id = 2
    sd.play(data,samplerate=sampleRate,device = device_id)
    sd.wait()

if __name__ == "__main__":
    play_audio_english("Hello, world! This is using the elevenlabs streaming API.")



