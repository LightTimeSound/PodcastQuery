import requests
from bs4 import BeautifulSoup
import csv
from sys import exit
import re

index_url = "https://feeds.captivate.fm/flirting-with-models/"  # Replace with the actual URL

def get_all_episode_urls(index_url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(index_url, headers=headers)
    soup = BeautifulSoup(response.content, features='xml')
    
    items = soup.find_all('link')
    links = [item for item in items if item.string and re.match(r'https://www.flirtingwithmodels.com/\d{4}/\d{2}/\d{2}/.*', item.string)]
    
    print(links)

    return links

episode_urls = get_all_episode_urls(index_url)

with open('episode_urls.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['URL'])
    for url in episode_urls:
        writer.writerow([url])
