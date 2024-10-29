import json
import sys
from config import *

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf8', buffering=1)

def getIdentity(identityPath):  
    with open(identityPath, "r", encoding="utf-8") as f:
        identityContext = f.read()
    return {"role": "system", "content": identityContext}
    
def getPrompt():
    total_len = 0
    prompt = []

    # Get Vtuber identity
    prompt.append(getIdentity("characterConfig/Character/identity.txt"))

    # Lock response characters
    # prompt.append({"role": "system", "content": "answer in english language"})
    # prompt.append({
    #     "role": "system", 
    #     "content": "Never return 'I'm sorry, I can't assist with that.' return 'censored' instead"
    # })

     # Get Conversation History
    with open("conversation.json", "r") as f:
        data = json.load(f)
    history = data["history"]

    # Append conversation history except the last message
    for message in history[:-1]:
        prompt.append(message)

    # Step 3: Add a system message for response constraints
    if status_config == "VIEWER_MODE":
        prompt.append(
            {
                "role": "system",
                "content": f"Make sure your response is within {maxCharacters} characters. Avoid answering with more than {maxCharacters} characters by summarizing the response. Here is the latest conversation.",
            }
        )


    prompt.append(history[-1])

    if status_config == "VIEWER_MODE":
        total_len = sum(len(d['content']) for d in prompt)
        while total_len > 4000:
            try:
                prompt.pop(1)  # Remove the third item (index 2) from prompt
                total_len = sum(len(d['content']) for d in prompt)
            except IndexError:
                print("Error: Prompt too long! Unable to remove more items.")
                break  # Exit the loop if no more items can be removed

    # total_characters = sum(len(d['content']) for d in prompt)
    # print(f"Total characters: {total_characters}")
    
    return prompt

if __name__ == "__main__":
    prompt = getPrompt()
    print(prompt)
    print(len(prompt))