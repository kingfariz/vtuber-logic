from openai import OpenAI
# import winsound
import sys
import pytchat
import time
import re
import pyaudio
import keyboard
import wave
import threading
import json
import socket
from emoji import demojize
from config import *
from utils.translate import *
from utils.TTS import *
from utils.subtitle import *
from utils.promptMaker import *
from utils.translate_openai import translate_openai
from utils.twitch_config import *
from TikTokLive import TikTokLiveClient
from TikTokLive.events import ConnectEvent, CommentEvent, GiftEvent
import sounddevice as sd
import soundfile as sf
from pydantic import BaseModel
from enum import Enum
import pyautogui

# to help the CLI write unicode characters to the terminal
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf8', buffering=1)

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

class ExpressionEnum(str, Enum):
    Happy = "Happy"
    Neutral = "Neutral"
    Shocked = "Shocked"
    Angry = "Angry"
    Shy = "Shy"
    Excited = "Excited"
    Laugh = "Laugh"
    Sad = "Sad"

class AIChatResponse(BaseModel):
    message: str
    expression: ExpressionEnum

# function to get the user's input audio
def record_audio():
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    WAVE_OUTPUT_FILENAME = "input.wav"
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    frames = []
    print("Recording...")
    while keyboard.is_pressed('RIGHT_SHIFT'):
        data = stream.read(CHUNK)
        frames.append(data)
    print("Stopped recording.")
    stream.stop_stream()
    stream.close()
    p.terminate()
    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    transcribe_audio("input.wav")

# function to transcribe the user's audio
def transcribe_audio(file):
    global chat_now
    try:
        audio_file= open(file, "rb")
        # Translating the audio to English
        # transcript = openai.Audio.translate("whisper-1", audio_file)
        # Transcribe the audio to detected language
        # transcript = client.audio.transcriptions.create("whisper-1", audio_file)
        # chat_now = transcript.text
        transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file, response_format="text")
        chat_now = transcript
        print ("Question: " + chat_now)
    except Exception as e:
        print("Error transcribing audio: {0}".format(e))
        return

    result = owner_name + " said " + chat_now
    conversation.append({'role': 'user', 'content': result})
    openai_answer()

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

# function to capture livechat from youtube
def yt_livechat(video_id):
        global chat

        live = pytchat.create(video_id=video_id)
        while live.is_alive():
        # while True:
            try:
                for c in live.get().sync_items():
                    # Ignore chat from the streamer and Nightbot, change this if you want to include the streamer's chat
                    if c.author.name in blacklist:
                        continue
                    # if not c.message.startswith("!") and c.message.startswith('#'):
                    if not c.message.startswith("!"):
                        # Remove emojis from the chat
                        chat_raw = re.sub(r':[^\s]+:', '', c.message)
                        chat_raw = chat_raw.replace('#', '')
                        # chat_author makes the chat look like this: "Nightbot: Hello". So the assistant can respond to the user's name
                        chat = 'viewer named ' + c.author.name + ' say ' + chat_raw
                        
                        print(chat)
                        
                    time.sleep(1)
            except Exception as e:
                print("Error receiving chat: {0}".format(e))

def tiktok_livechat(username):
    # Create the TikTokLiveClient with the provided username
    client = TikTokLiveClient(unique_id=username)

    # Event handler for connection
    @client.on(ConnectEvent)
    async def on_connect(event: ConnectEvent):
        print(f"Connected to @{event.unique_id} (Room ID: {client.room_id})")

    # Event handler for comments
    @client.on(CommentEvent)
    async def on_comment(event: CommentEvent):
        global chat
        try:
            # Ignore chat from blacklisted users
            if event.user.nickname in blacklist:
                return
            # Process and format chat message
            chat_raw = re.sub(r':[^\s]+:', '', event.comment) 
            chat_raw = chat_raw.replace('#', '')
            chat = f'viewer named {event.user.nickname} say {chat_raw}'
            print(chat)
            time.sleep(1)
        except Exception as e:
            print(f"Error processing comment: {e}")

    # Event handler for gifts
    @client.on(GiftEvent)
    async def on_gift(event: GiftEvent):
        global chat
        try:
            gift_message = (
                f"viewer named {event.user.nickname} sent a gift: with {event.gift.name} (worth {event.value} coins)"
            )
            chat = gift_message
            print(chat)
            time.sleep(1)
        except Exception as e:
            print(f"Error processing gift: {e}")

    # Start the client and connect to TikTok live chat
    client.run()

def twitch_livechat():
    global chat
    sock = socket.socket()

    sock.connect((server, port))

    sock.send(f"PASS {token}\n".encode('utf-8'))
    sock.send(f"NICK {nickname}\n".encode('utf-8'))
    sock.send(f"JOIN {channel}\n".encode('utf-8'))

    regex = r":(\w+)!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :(.+)"

    while True:
        try:
            resp = sock.recv(2048).decode('utf-8')

            if resp.startswith('PING'):
                    sock.send("PONG\n".encode('utf-8'))

            elif not user in resp:
                resp = demojize(resp)
                match = re.match(regex, resp)

                username = match.group(1)
                message = match.group(2)

                if username in blacklist:
                    continue
                
                chat = username + ' said ' + message
                print(chat)

        except Exception as e:
            print("Error receiving chat: {0}".format(e))

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

def press_keys(expression):
    key_mapping = {
        ExpressionEnum.Happy: 'a',
        ExpressionEnum.Neutral: 'b',
        ExpressionEnum.Shocked: 'c',
        ExpressionEnum.Angry: 'd',
        ExpressionEnum.Shy: 'e',
        ExpressionEnum.Excited: 'f',
        ExpressionEnum.Laugh: 'g',
        ExpressionEnum.Sad: 'h'
    }

    if expression in key_mapping:
        key = key_mapping[expression]

        pyautogui.keyDown('ctrlright')
        time.sleep(0.05)
        pyautogui.keyDown('shiftleft')
        time.sleep(0.05)
        pyautogui.keyDown(key)
        time.sleep(0.05)
    else:
        print(f"No mapping found for expression: {expression}")

def release_keys(expression):
    key_mapping = {
        ExpressionEnum.Happy: 'a',
        ExpressionEnum.Neutral: 'b',
        ExpressionEnum.Shocked: 'c',
        ExpressionEnum.Angry: 'd',
        ExpressionEnum.Shy: 'e',
        ExpressionEnum.Excited: 'f',
        ExpressionEnum.Laugh: 'g',
        ExpressionEnum.Sad: 'h'
    }

    if expression in key_mapping:
        key = key_mapping[expression]
        # Release the keys
        pyautogui.keyUp('ctrlright')
        time.sleep(0.05)
        pyautogui.keyUp('shiftleft')
        time.sleep(0.05) 
        pyautogui.keyUp(key)
        time.sleep(0.05)
    else:
        print(f"No mapping found for expression: {expression}")

def handle_recording():
    print("Press and Hold Right Shift to record audio")
    while True:
        if keyboard.is_pressed('RIGHT_SHIFT'):
            record_audio()

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
            yt_livechat(live_id)

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