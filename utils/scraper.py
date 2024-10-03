# utils/scraper.py 

import requests
from bs4 import BeautifulSoup

def scrape_vods(streamer_name):
    url = f"https://vodvod.top/search/{streamer_name}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    vods = []
    # Lógica para extrair os VODs
    for vod in soup.find_all('div', class_='vod-item'):
        title = vod.find('h3').text
        link = vod.find('a')['href']
        thumbnail = vod.find('img')['src']
        vods.append({
            'title': title,
            'link': link,
            'thumbnail': thumbnail
        })
    return vods

