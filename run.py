### Python Default ###
import time
import threading

### LLM ###
from openai import OpenAI

### Audio ###
import sounddevice as sd
import soundfile as sf

### Internal ###
from config import *
from utils.translate import *
from utils.TTS import *
from utils.subtitle import *
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

# translating is optional
def translate_text(text, expression_value):
    # Using openAI to translate
    text_jp = translate_openai(text, "JAPANESE")
    # tts_en = translate_openai(text_jp, "INDONESIA")

    try:
        print("RAW Answer: " + text)
        print("JP Answer: " + text_jp)
        # print("EN Answer: " + tts_en)
    except Exception as e:
        print("Error printing text: {0}".format(e))
        return

    # Choose between the available TTS engines
    # Japanese TTS
    voicevox_tts(text_jp)

    # Generate Subtitle
    # generate_subtitle(chat_now, text, tts_en)
    generate_subtitle(chat_now, text, "")

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
