### Python Default ###
import time
import re
import json
import socket
import threading

from pydantic import BaseModel
from emoji import demojize

### LLM ###
from openai import OpenAI

### Audio ###
import pyaudio
import wave
import sounddevice as sd
import soundfile as sf

### May NOT be compatible with UNIX ###
import keyboard

### Internal ###
from config import *
from utils.expressions import ExpressionEnum
from utils.translate import *
from utils.TTS import *
from utils.subtitle import *
from utils.promptMaker import *
from utils.translate_openai import translate_openai
from utils.keyboard_control import press_keys, release_keys
from streaming.tiktok import tiktok_livechat
from streaming.twitch import twitch_livechat
from streaming.youtube import youtube_livechat

# to help the CLI write unicode characters to the terminal
# sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf8', buffering=1)

client = OpenAI(api_key = api_key)

conversation = []
# Create a dictionary to hold the message data
history = {"history": conversation}

mode = 0
total_characters = 0
chat = ""
chat_now = ""
chat_prev = ""
is_Speaking = False
owner_name = "Farizi"
blacklist = ["Nightbot", "streamelements"]

class AIChatResponse(BaseModel):
    message: str
    expression: ExpressionEnum

# function to get an answer from OpenAI
def openai_answer():
    global total_characters, conversation

    if status_config == "VIEWER_MODE":
        total_characters = sum(len(d['content']) for d in conversation)
        while total_characters > 4000:
            try:
                # print(total_characters)
                # print(len(conversation))
                conversation.pop(1)
                total_characters = sum(len(d['content']) for d in conversation)
            except Exception as e:
                print("Error removing old messages: {0}".format(e))

    with open("conversation.json", "w", encoding="utf-8") as f:
        # Write the message data to the file in JSON format
        json.dump(history, f, indent=4)

    prompt = getPrompt()

    # response = client.chat.completions.create(
    response = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=prompt,
        max_tokens=max_token,
        temperature=1,   # More creative and engaging responses
        top_p=0.9,       # Balances diversity
        frequency_penalty=0.2,  # Avoids repetitive responses
        presence_penalty=0.5,    # Encourages introducing new topics
        response_format=AIChatResponse
    )
    # message = response.choices[0].message.content

    message = response.choices[0].message.parsed.message
    expression_value = response.choices[0].message.parsed.expression

    prompt_tokens = response.usage.completion_tokens
    completion_tokens = response.usage.prompt_tokens
    total_tokens = response.usage.total_tokens

    # Print the token usage and cost
    print(f"Prompt: {prompt}")
    print(f"Prompt Tokens: {prompt_tokens}")
    print(f"Completion Tokens: {completion_tokens}")
    print(f"Total Tokens: {total_tokens}")
    print(f"Expression: {expression_value}")
    print(f"___________")

    conversation.append({'role': 'assistant', 'content': message})

    translate_text(message, expression_value)

def play_audio(filename):
    device_id = 8
    data, sampleRate = sf.read(filename)
    sd.play(data, sampleRate, device=device_id)
    
    # Wait until the audio is done playing
    time.sleep(len(data) / sampleRate)
    # await asyncio.sleep(len(data) / sampleRate)

# translating is optional
def translate_text(text, expression_value):
    global is_Speaking
    # subtitle will act as subtitle for the viewer
    # subtitle = translate_google(text, "ID")

    ## When we are using googletrans to translate (rest of the code will be deprecated also)
    # tts will be the string to be converted to audio
    # detect = detect_google(text)
    # tts = translate_google(text, f"{detect}", "JA")
    # # tts = translate_deeplx(text, f"{detect}", "JA")
    # tts_en = translate_google(text, f"{detect}", "EN")

    ## When we are using openAI to translate
    # tts will be the string to be converted to audio
    # print("__________")
    # print("text")
    # print(text)
    # print("__________")
    # tts_en = translate_openai(text, "INDONESIA")
    tts = translate_openai(text, "JAPANESE")
    # tts = translate_openai(text, "JAPANESE")
    tts_en = translate_openai(tts, "INDONESIA")

    try:
        print("RAW Answer: " + text)
        print("JP Answer: " + tts)
        print("EN Answer: " + tts_en)
    except Exception as e:
        print("Error printing text: {0}".format(e))
        return

    # Choose between the available TTS engines
    # Japanese TTS
    voicevox_tts(tts)

    # Generate Subtitle
    # generate_subtitle(chat_now, text, tts_en)
    generate_subtitle(chat_now, tts_en, "")

    # time.sleep(1)

    # is_Speaking is used to prevent the assistant speaking more than one audio at a time
    is_Speaking = True

    press_keys(expression_value)
    # winsound.PlaySound("test.wav", winsound.SND_FILENAME)
    filename = 'test.wav'

    device_id = 8
    data, sampleRate = sf.read(filename)
    sd.play(data, sampleRate, device=device_id)
    time.sleep(len(data) / sampleRate)
    
    # play_audio(filename)
    release_keys(expression_value)
    
    is_Speaking = False


    # Clear the text files after the assistant has finished speaking
    time.sleep(1)
    # asyncio.sleep(1)
    with open ("output.txt", "w") as f:
        f.truncate(0)
    with open ("chat.txt", "w") as f:
        f.truncate(0)

def preparation():
    global conversation, chat_now, chat, chat_prev
    while True:
        # If the assistant is not speaking, and the chat is not empty, and the chat is not the same as the previous chat
        # then the assistant will answer the chat
        chat_now = chat
        if is_Speaking == False and chat_now != chat_prev:
            # Saving chat history
            print('<<processing>>')
            conversation.append({'role': 'user', 'content': chat_now})
            chat_prev = chat_now
            openai_answer()
        time.sleep(1)
        # await asyncio.sleep(1)  # Use asyncio.sleep instead of time.sleep to not block the event loop

def main():
    print(sd.query_devices())
    try:
        mode = input("Mode (1-Mic, 2-Youtube Live, 3-Twitch Live, 4-Tiktok Live): ")

        if mode == "1":
            handle_recording()
        
        elif mode == "2":
            live_id = input("Livestream ID: ")
            t = threading.Thread(target=preparation)
            t.start()
            youtube_livechat(live_id)

        elif mode == "3":
            print("To use this mode, make sure to change utils/twitch_config.py to your own config")
            t = threading.Thread(target=preparation)
            t.start()
            twitch_livechat()

        elif mode == "4":
            live_username = input("TikTok Livestream Username: ")
            t = threading.Thread(target=preparation)
            t.start()
            tiktok_livechat(live_username)
            
    except KeyboardInterrupt:
        t.join()
        print("Stopped")

if __name__ == "__main__":
    main()
