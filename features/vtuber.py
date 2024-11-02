import time

from openai import OpenAI

from features.agent import get_openai_answer
from features.audio import play_audio
from features.record import record_audio
from features.TTS import voicevox_tts
from features.transcribe import transcribe_audio
from features.translate_openai import translate_openai
from features.subtitle import generate_subtitle
from features.audio import play_audio_english
import threading

class VTuber():
    def __init__(self,
                 openai_client: OpenAI,
                 owner_name="Default Owner",
        ):
        self.openai_client = openai_client
        self.owner_name = owner_name
        self.new_input_flag = False
        self.latest_user_comment = ''
        self.conversation: list[dict[str, str]] = list()
    
    def start_voice_conversations(self):
        while True:
            self.voice_conversation()
    
    def voice_conversation(self):
        # Record and save mic input as a wave file
        record_audio()
        
        transcript = transcribe_audio(client=self.openai_client)
        content = self.owner_name + " said " + transcript
        self.conversation.append({'role': 'user', 'content': content})
        
        message, expression_value = get_openai_answer(
            conversation=self.conversation,
            client=self.openai_client,
        )
        self.conversation.append({'role': 'assistant', 'content': message})

        # English TTS
        play_audio_english(message)
        
        text_jp = translate_openai(message, "JA")
        
        print("RAW Answer: " + message)
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
            content = "continue"
            self.conversation.append({'role': 'system', 'content': content})
            self.latest_user_comment = ''

        message, expression_value = get_openai_answer(
            conversation=self.conversation,
            client=self.openai_client,
        )
        self.conversation.append({'role': 'assistant', 'content': message})
        
        text_jp = translate_openai(message, "JA")
        
        print("RAW Answer: " + message)
        print("JP Answer: " + text_jp)
        # time.sleep(10) # Mock speaking time
        
        # Japanese TTS
        voicevox_tts(text_jp)
        
        generate_subtitle(
            text=text_jp,
            translation=message,
            question=self.latest_user_comment,
        )
        
        play_audio()
    
        # Clear the text files after the assistant has finished speaking
        # time.sleep(1)
        # # asyncio.sleep(1)
        # with open ("output.txt", "w") as f:
        #     f.truncate(0)
        # with open ("chat.txt", "w") as f:
        #     f.truncate(0)