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
        self.input_value = ''
    
    def start_voice_conversations(self):
        while True:
            self.voice_conversation()
    
    def voice_conversation(self):
        conversation: list[dict[str, str]] = list()
        
        # Record and save mic input as a wave file
        record_audio()
        
        transcript = transcribe_audio(client=self.openai_client)
        content = self.owner_name + " said " + transcript
        conversation.append({'role': 'user', 'content': content})
        
        message, expression_value = get_openai_answer(
            conversation=conversation,
            client=self.openai_client,
        )
        conversation.append({'role': 'assistant', 'content': message})

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
        respond_thread = threading.Thread(target=self.text_conversation)

        prompt_thread.start()
        respond_thread.start()

        prompt_thread.join()
        respond_thread.join()

    def get_text_input(self):
        while True:
            user_input = input("Enter new input: ")
            self.input_value = user_input  # Store new input
            self.new_input_flag = True

    def text_conversation(self):
        conversation: list[dict[str, str]] = list()
        conversation.append(({'role': 'user', 'content': "greet your customer"}))
        self.get_answer_in_japanese(conversation)

        while True:
            if self.input_value:
                content = self.owner_name + " said " + self.input_value
                conversation.append({'role': 'user', 'content': content})
                self.input_value = ''
            else:
                content = "Continue the conversation naturally from where you left off. When you've covered all aspects of the product, shift to introducing another product. Keep the tone conversational and avoid sounding like you're answering a question."
                conversation.append({'role': 'user', 'content': content})

            self.get_answer_in_japanese(conversation)

    def get_answer_in_japanese(self, conversation):
        message, expression_value = get_openai_answer(
            conversation=conversation,
            client=self.openai_client,
        )
        conversation.append({'role': 'assistant', 'content': message})
        
        text_jp = translate_openai(message, "JA")
        
        print("RAW Answer: " + message)
        print("JP Answer: " + text_jp)
        
        # Japanese TTS
        voicevox_tts(text_jp)
        
        generate_subtitle(
            text=text_jp,
            translation=message,
            question=self.input_value,
        )
        
        play_audio()
    
        # Clear the text files after the assistant has finished speaking
        # time.sleep(1)
        # # asyncio.sleep(1)
        # with open ("output.txt", "w") as f:
        #     f.truncate(0)
        # with open ("chat.txt", "w") as f:
        #     f.truncate(0)