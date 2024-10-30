from openai import OpenAI

def transcribe_audio(
    client: OpenAI,
    filepath="input.wav",
) -> str:
    
    try:
        audio_file= open(filepath, "rb")

        # Transcribe the audio to detected language
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="text",
        )

        print ("Question: " + transcript)
        
        return transcript
    
    except Exception as e:
        print("Error transcribing audio: {0}".format(e))
        return ""
