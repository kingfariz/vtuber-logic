import pandas as pd
from config import *

# sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf8', buffering=1)

def get_identity(identity_path) -> str:
    with open(identity_path, "r", encoding="utf-8") as f:
        identity_context = f.read()
    
    return identity_context

def get_system_prompt(
    identity_path="characterConfig/Character/shopping_assistant.txt",
) -> dict[str, str]:
    identity_context = get_identity(identity_path)

    return {"role": "system", "content": identity_context}
    
def get_prompt(history: list[str]):
    total_len = 0

    # Get Vtuber identity/role
    identity = get_identity()
    prompt = [identity] + history

    # Step 3: Add a system message for response constraints
    if status_config == "VIEWER_MODE":
        prompt.append(
            {
                "role": "system",
                "content": f"Make sure your response is within {maxCharacters} characters. Avoid answering with more than {maxCharacters} characters by summarizing the response. Here is the latest conversation.",
            }
        )

    if status_config == "VIEWER_MODE":
        total_len = sum(len(d['content']) for d in prompt)
        while total_len > 4000:
            try:
                prompt.pop(1)  # Remove the third item (index 2) from prompt
                total_len = sum(len(d['content']) for d in prompt)
            except IndexError:
                print("Error: Prompt too long! Unable to remove more items.")
                break  # Exit the loop if no more items can be removed
    
    return prompt

if __name__ == "__main__":
    prompt = get_prompt()
    print(prompt)
    print(len(prompt))
