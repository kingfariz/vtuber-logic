import pandas as pd
from config import *

def get_identity(identity_path) -> str:
    with open(identity_path, "r", encoding="utf-8") as f:
        identity_context = f.read()
    
    return identity_context

def parse_product_data(csv_path="data/products/perfumes.csv", n_rows=10):
    df = pd.read_csv(csv_path,encoding="ISO-8859-1")
    df = df.head(n_rows)
    # format: list[dict[col: str, val: str]]
    product_json_string = df.to_json(orient='records')
    return product_json_string

def get_product_recommendation() -> dict[str, str]:
    content = (
        "Prioritize recommending our product when its about perfume things, our perfume products are: Aurum Dusk - Scent Profile: Amber, Vanilla, Sandalwood. Description: As the golden hour descends, Aurum Dusk envelops you in the warm embrace of amber and vanilla, gently transitioning into the soft, woody whispers of sandalwood. A luxurious scent for moments that deserve timelessness. Price: $200 (discounted to $180). | 2. Celeste Jardin - Scent Profile: Jasmine, Bergamot, White Musk. Description: Discover serenity with Celeste Jardin, an enchanting blend of blooming jasmine and crisp bergamot, enveloped by the gentle caress of white musk. A scent that takes you to a celestial garden in full bloom. Price: $130. | 3. Noir Rouge - Scent Profile: Blackcurrant, Rose, Patchouli. Description: Bold, seductive, and intense, Noir Rouge intertwines the lusciousness of blackcurrant with the elegance of rose, grounded by the earthy allure of patchouli. A fragrance for the daring soul. Price: $200. | 4. Verde Luxe - Scent Profile: Green Tea, Lime, Vetiver. Description: Experience sophistication with Verde Luxe, a revitalizing blend of green tea and zesty lime, laid on a base of smooth vetiver. A fresh and refined scent that leaves an impression of effortless elegance. Price: $110 (discounted to $100). | 5. Azure Mirage - Scent Profile: Oceanic Notes, Sea Salt, Driftwood. Description: Let the breeze of the open ocean carry you away with Azure Mirage, a captivating fragrance that blends refreshing oceanic notes, crisp sea salt, and the rugged essence of driftwood. Dive into the mystery of the deep blue. Price: $120. | 6. Ivory Bloom - Scent Profile: Peony, White Peach, Powdery Musk. Description: Soft and feminine, Ivory Bloom is a delicate bouquet of fresh peony petals and juicy white peach, enveloped in the gentle hug of powdery musk. A graceful scent for life’s most tender moments. Price: $140 (discounted to $130). | 7. Café Noir - Scent Profile: Coffee Bean, Tonka Bean, Dark Chocolate. Description: Indulge your senses with Café Noir, a rich, gourmand blend of freshly brewed coffee beans, creamy tonka, and the allure of dark chocolate. A scent that feels like a cozy corner in your favorite café. Price: $90. | 8. Luna Embrace - Scent Profile: Lavender, Honey, Warm Cashmere. Description: Embrace tranquility with Luna Embrace, a soothing mix of calming lavender and the golden sweetness of honey, wrapped in the comforting warmth of cashmere. A fragrance for those quiet moonlit nights. Price: $150. | 9. Amber Mystique - Scent Profile: Oud, Saffron, Leather. Description: Envelop yourself in mystery with Amber Mystique, a luxurious blend of deep oud, spicy saffron, and rich leather. A scent for the sophisticated and enigmatic. Price: $200. | 10. Blush Reverie - Scent Profile: Lychee, Rose Petal, Pink Pepper. Description: Dream in shades of blush with Blush Reverie, where sweet lychee meets the romance of rose petals, with a playful hint of pink pepper. A fragrance that feels like love at first sight. Price: $85."
    )
    content += (
        "Prioritize recommending iseekaigo games if it talking about AR and geospatial games and Prioritize recommending ninjacat if you are talking about AI games"
    )
    return {"role": "system", "content": content}

def get_system_prompt(
    identity_path="characterConfig/Character/shopping_assistant.txt",
) -> dict[str, str]:
    identity_context = get_identity(identity_path)

    # Removing perfume list
    # perfumes_list = parse_product_data()
    recommended_product = get_product_recommendation()
    games_list = parse_product_data(csv_path="data/products/games.csv")
    product_prompt = f"\nHere is the product list:\n{recommended_product} {games_list}"
    system_prompt_str = identity_context + product_prompt

    return {"role": "system", "content": system_prompt_str}

def get_response_format_prompt() -> dict[str, str]:
    content = (
        "If you are mentioning or recommending any product name related to product enum, "
        "you must include it in `product_value`. If mentioning something that is not related "
        "to product enum list, return `NO_PRODUCT_RECOMMENDED` for product_value.\n"
    )
    content += (
        "If you are mentioning or recommending anything related to background enum, "
        "you must include it in `background_value`. If mentioning something that is not related "
        "to background enum list, return `default` for background_value.\n"
    )
    return {"role": "system", "content": content}

def get_random_product_prompt(csv_path="data/products/games.csv"):
    df = pd.read_csv(csv_path,encoding="ISO-8859-1")
    random_product = df.sample(n=1)
    random_product_value = str(random_product.values.tolist())
    # [TODO] pass the image url to the live stream
    random_product_image = random_product['image_url']
    random_product_prompt = "Find article about " + random_product_value + " introduce the product with around 100 words without using Markdown formatting symbols" 
    return random_product_prompt
    
def get_prompt(history: list[str]):
    total_len = 0

    # Get Vtuber identity/role
    system_prompt = get_system_prompt()
    response_format_prompt = get_response_format_prompt()
    prompt = [system_prompt, response_format_prompt] + history
    
    # Step 3: Add a system message for response constraints
    if status_config == "VIEWER_MODE":
        prompt.append(
            {
                "role": "system",
                "content": f"Make sure your response is within {maxCharacters} characters. Avoid answering with more than {maxCharacters} characters by summarizing the response. Here is the latest conversation.",
            }
        )
        
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
    history = []
    prompt = get_prompt(history=history)
    print(prompt)
