from openai_t2t import get_openai_client

client = get_openai_client()

game_name = "attack on titan 2 nintendo switch"

prompt_str = f"Get the URL for a best-quality, full HD dimention image of the game: {game_name}"
prompt = [{"role": "system", "content": prompt_str}]

response = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=prompt,
        temperature=1,   # More creative and engaging responses
        top_p=0.9,       # Balances diversity
        frequency_penalty=0.2,  # Avoids repetitive responses
        presence_penalty=0.5,    # Encourages introducing new topics
)
print(response)
message = response.choices[0].message.content

print(message)