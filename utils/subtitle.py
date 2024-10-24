def generate_subtitle(chat_now, result_id, tts):
    # output.txt will be used to display the subtitle on OBS
    with open("output.txt", "w", encoding="utf-8") as outfile:
        try:
            text = tts
            words = text.split()
            lines = [words[i:i+10] for i in range(0, len(words), 10)]
            for line in lines:
                outfile.write(" ".join(line) + "\n")
            # Write translated text (result_id)
            outfile.write("--- Translation ---\n")
            text = result_id
            words = text.split()
            lines = [words[i:i+10] for i in range(0, len(words), 10)]
            for line in lines:
                outfile.write(" ".join(line) + "\n")
            
            # Add separator and write original text (tts)
                
        except Exception as e:
            print(f"Error writing to output.txt: {e}")


    # chat.txt will be used to display the chat/question on OBS
    with open("chat.txt", "w", encoding="utf-8") as outfile:
        try:
            words = chat_now.split()
            lines = [words[i:i+10] for i in range(0, len(words), 10)]
            for line in lines:
                outfile.write(" ".join(line) + "\n")
        except:
            print("Error writing to chat.txt")

