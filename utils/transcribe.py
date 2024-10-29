from openai import OpenAI

def transcribe_audio(
    client: OpenAI,
    filepath="input.wav",
    # chat_now="",
    # owner_name="Default Owner",
) -> str:
    
    try:
        audio_file= open(filepath, "rb")
        # Translating the audio to English
        # transcript = openai.Audio.translate("whisper-1", audio_file)
        # Transcribe the audio to detected language
        # transcript = client.audio.transcriptions.create("whisper-1", audio_file)
        # chat_now = transcript.text
        transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file, response_format="text")
        print ("Question: " + transcript)
        
        return transcript
    
    except Exception as e:
        print("Error transcribing audio: {0}".format(e))
        return

    # result = owner_name + " said " + chat_now
    # conversation.append({'role': 'user', 'content': result})
    # openai_answer()