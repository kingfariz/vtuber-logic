from openai import OpenAI

from features.agent import get_openai_answer
from features.audio import play_audio
from features.record import record_audio
from features.TTS import voicevox_tts
from features.transcribe import transcribe_audio
from features.translate_openai import translate_openai
from features.subtitle import generate_subtitle
from features.audio import play_audio_english

class VTuber():
    def __init__(self,
                 openai_client: OpenAI,
                 owner_name="Default Owner",
        ):
        self.openai_client = openai_client
        self.owner_name = owner_name
    
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
        
        # Clear the text files after the assistant has finished speaking
        # time.sleep(1)
        # # asyncio.sleep(1)
        # with open ("output.txt", "w") as f:
        #     f.truncate(0)
        # with open ("chat.txt", "w") as f:
        #     f.truncate(0)