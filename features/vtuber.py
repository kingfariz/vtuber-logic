import os
import shutil
import time
from typing import Literal

from openai import OpenAI

from features.agent import get_openai_answer
from features.audio import play_audio
from features.record import record_audio
from features.TTS import voicevox_tts
from features.transcribe import transcribe_audio
from features.translate_openai import translate_openai
from features.subtitle import generate_subtitle
from features.audio import play_audio_english
from features.prompt_maker import get_random_product_prompt
import threading

class VTuber():
    def __init__(self,
                 openai_client: OpenAI,
                 language: Literal["EN", "JA"] = "EN",
                 owner_name="Default Owner",
                 play_voice=True,
        ):
        self.openai_client = openai_client
        self.language = language
        self.owner_name = owner_name
        self.play_voice = play_voice
        
        self.new_input_flag = False
        self.latest_user_comment = ''
        self.conversation: list[dict[str, str]] = list()
    
    def update_background_image(self, product_value: str):
        prop_output_path = './assets/background-output/background-output.JPG'
        product_image_path = f'./assets/{product_value.lower()}.jpg'

        # Step 1: Delete the existing background-output.jpg if it exists
        if os.path.exists(prop_output_path):
            os.remove(prop_output_path)

        # Step 2: Copy the new product image to background-output
        if os.path.exists(product_image_path):
            shutil.copy(product_image_path, prop_output_path)
        else:
            print(f"Background image {product_image_path} does not exist. Skip saving the background image")

    def update_product_image(self, product_value: str):
        prop_output_path = './assets/prop-output/prop-output.jpg'
        product_image_path = f'./assets/{product_value.lower()}.jpg'

        # Step 1: Delete the existing prop-output.jpg if it exists
        if os.path.exists(prop_output_path):
            os.remove(prop_output_path)

        # Step 2: Copy the new product image to prop-output
        if os.path.exists(product_image_path):
            shutil.copy(product_image_path, prop_output_path)
        else:
            print(f"Product image {product_image_path} does not exist. Skip saving the product image")

    def start_voice_conversations(self):
        while True:
            self.voice_conversation()
    
    def voice_conversation(self):
        # Record and save mic input as a wave file
        record_audio()
        
        transcript = transcribe_audio(client=self.openai_client)
        content = self.owner_name + " said " + transcript
        self.conversation.append({'role': 'user', 'content': content})
        
        message, expression_value, product_value, background_value = get_openai_answer(
            conversation=self.conversation,
            client=self.openai_client,
        )

        # Update product image based on the product_value received
        self.update_product_image(product_value)

        # Update product image based on the product_value received
        self.update_background_image(background_value)
        
        self.conversation.append({'role': 'assistant', 'content': message})
        print("RAW Answer: " + message)
        
        if not self.play_voice:
            return
        
        if self.language == "EN":
            play_audio_english(message)
            
        elif self.language == "JA":
            text_jp = translate_openai(message, "JA")
            print("JP Answer: " + text_jp)
            
            # Japanese TTS
            voicevox_tts(text_jp)
            
            generate_subtitle(
                text=text_jp,
                translation=message,
                question=transcript,
            )
        
            play_audio()

    def start_text_conversations(self):
        prompt_thread = threading.Thread(target=self.get_text_input)
        prompt_thread.start()
        # respond_thread = threading.Thread(target=self.text_conversation)
        # respond_thread.start()
        
        try:
            while True:
                self.text_conversation()
        except KeyboardInterrupt:
            prompt_thread.join()
        # respond_thread.join()

    def get_text_input(self):
        while True:
            user_input = input("Enter new input: ")
            self.latest_user_comment = user_input  # Store new input
            self.new_input_flag = True

    def text_conversation(self):
        if self.new_input_flag:
            content = self.owner_name + " said " + self.latest_user_comment
            self.conversation.append({'role': 'user', 'content': content})
            self.new_input_flag = False
        else:
            # If not inputs, AI keeps talking
            continue_prompt = get_random_product_prompt()
            #continue_prompt = "Continue the conversation naturally from where you left off. When you've covered all aspects of the product, shift to introducing another product. Keep the tone conversational and avoid sounding like you're answering a question."
            self.conversation.append({'role': 'system', 'content': continue_prompt})
            self.latest_user_comment = ''

        message, expression_value = get_openai_answer(
            conversation=self.conversation,
            client=self.openai_client,
        )
        self.conversation.append({'role': 'assistant', 'content': message})
        print("RAW Answer: " + message)
        
        if not self.play_voice:
            return
        
        if self.language == "EN":
            play_audio_english(message)
            
        elif self.language == "JA":
            text_jp = translate_openai(message, "JA")
            
            print("JP Answer: " + text_jp)
            # time.sleep(10) # Mock speaking time
            
            # Japanese TTS
            # Saves .wav file
            voicevox_tts(text_jp)
            
            generate_subtitle(
                text=text_jp,
                translation=message,
                question=self.latest_user_comment,
            )
            
            # Plays the saved .wav file
            play_audio()

        # Clear the text files after the assistant has finished speaking
        # time.sleep(1)
        # # asyncio.sleep(1)
        # with open ("output.txt", "w") as f:
        #     f.truncate(0)
        # with open ("chat.txt", "w") as f:
        #     f.truncate(0)