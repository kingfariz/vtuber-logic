from openai import OpenAI

from utils.agent import openai_answer
from utils.record import handle_recording
from utils.transcribe import transcribe_audio

class VTuber():
    def __init__(self,
                 openai_client: OpenAI,
                 owner_name="Default Owner",
        ):
        self.openai_client = openai_client
        self.owner_name = owner_name
    
    def start_conversation(self):
        conversation: list[str] = list()
        chat_now = ""
        
        # Record and save mic input as "input.wav"
        handle_recording()
        
        transcript = transcribe_audio(client=self.openai_client)
        content = self.owner_name + " said " + transcript
        conversation.append({'role': 'user', 'content': content})

        message, expression_value = openai_answer()
        conversation.append({'role': 'assistant', 'content': message})

        translate_text(message, expression_value)
