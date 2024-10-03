# utils/downloader.py 

import requests
import os

def download_m3u8(vod_link, cache_dir):
    response = requests.get(vod_link)
    filename = vod_link.split('/')[-1]
    filepath = os.path.join(cache_dir, filename)

    with open(filepath, 'wb') as f:
        f.write(response.content)

    return filepath
 
