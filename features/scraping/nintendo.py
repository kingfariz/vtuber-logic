import requests
from typing import Literal

import pandas as pd
# noa: North America, noe: Europe, noe: Japan
from nintendeals import noa
from nintendeals.api.prices import fetch_prices
from openai import OpenAI

from openai_t2t import get_openai_client

client = get_openai_client()


def chunked_list(list_data: list, chunk_size: int):
  for i in range(0, len(list_data), chunk_size):
      yield list_data[i:i + chunk_size]


def fetch_all_switch_games(save_path="", get_prices=False):
    ATTRIBUTES = ("title", "nsuid", "price_us", "description")
    
    # data = [
    #     {key: getattr(game, key) for key in ATTRIBUTES}
    #     for game in noa.list_switch_games()
    # ]
    data = list()
    
    for game in noa.list_switch_games():
        # row = {key: getattr(game, key) for key in ATTRIBUTES}
        row = {
            # "title": f'"{game.title}"',
            "title": game.title,
            "nsuid": game.nsuid,
            # "price_us": game.price(country="US"),
            # "price_us": nsuid_to_price.get(game.nsuid, default=None),
            # "description": f'"{game.description}"',
            "description": game.description,
        }
        data.append(row)
    
    if get_prices:
        nsuids = [row["nsuid"] for row in data]
        nsuid_to_price: dict[str, float] = dict()
        
        for chunked_nsuids in chunked_list(nsuids, chunk_size=50):
            # An API call limits up to 50 nsuids
            for (nsuid, price) in fetch_prices(country="US", nsuids=chunked_nsuids):
                nsuid_to_price[nsuid] = price.value
        
        for row in data:
            row["price_us"] = nsuid_to_price.get(row["nsuid"], None)
        
        columns = ATTRIBUTES
    else:
        columns = ("title", "nsuid", "description")
    
    df = pd.DataFrame(data=data, columns=columns)
    df = df.sort_values(by="title")
    
    if save_path != "":
        try:
            df.to_csv(save_path)
        except Exception as e:
            print
    
    return df
    

def search_nintendo_title_and_nsuid(
    query: str,
    region: Literal["NA", "EU", "JP"],
) -> str:
    """An nsuid is a 14 digit long string which Nintendo uses to 
    identify games on each region. Taking Breath of the Wild as an example,
    we have these 3 nsuids for it (one per region):
    * 70010000000025 (NA)
    * 70010000000023 (EU)
    * 70010000000026 (JP)
    
    https://github.com/fedecalendino/nintendeals
    """
    # title_to_nsuid = {game.title: game.nsuid for game in noa.search_switch_games(query)}
    # First match
    for game in noa.search_switch_games(query):
        print(game.title, game.nsuid)
    
    game = next(noa.search_switch_games(query))
    
    return game.title, game.nsuid
    

def fetch_nintendo_html(nsuid: str) -> str | None:
    url = f"https://store-jp.nintendo.com/item/software/{nsuid}"
    try:
        http_response = requests.get(url)
    except Exception as e:
        print(e)
        return None
    
    html = http_response.text
    
    return html


def parse_top_image_url_from_html_openai(client: OpenAI, nsuid: str):
    html = fetch_nintendo_html(nsuid=nsuid)
    
    prompt_str = f"From the below HTML, return the img url tag for the top image.\n\n{html}"
    prompt = [{"role": "system", "content": prompt_str}]

    http_response = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=prompt,
            temperature=1,   # More creative and engaging responses
            top_p=0.9,       # Balances diversity
            frequency_penalty=0.2,  # Avoids repetitive responses
            presence_penalty=0.5,    # Encourages introducing new topics
    )
    print(http_response)
    message = http_response.choices[0].message.content

    print(message)

if __name__ == "__main__":
    # client = get_openai_client()
    # parse_top_image_url_from_html_openai(client=client)
    # query = "attack on titan 2"
    # query = "Zelda"
    # query = "Zelda kingdom"
    # query = ""
    # title, nsuid = search_nintendo_title_and_nsuid(query=query, region="NA")
    # print(title, nsuid)
    
    save_path = f"data/switch_games.csv"
    df = fetch_all_switch_games(save_path, get_prices=True)
    print(df)
    
    # prices = fetch_prices(country="US", nsuids=["70010000063714"])
    # print(list(prices))