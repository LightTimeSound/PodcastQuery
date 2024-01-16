import requests
from bs4 import BeautifulSoup
import re
import csv
from sys import exit

url = "https://www.flirtingwithmodels.com/season-"

season_urls = []
for i in range(1, 8):
    if i == 7:
        season_urls.append(url + str(i) + '-2024/')
    else:
        season_urls.append(url + str(i) + '/')

def get_episode_urls(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    links = soup.find_all('div', class_='hover-content')
    links = [link.find('a')['href'] for link in links]

    return links


# Get all episode urls:
episode_urls = []
for season_url in season_urls:
    episode_urls.append(get_episode_urls(season_url))
    
#for each item in episode_urls, write it to a csv:
with open('episode_urls.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    for season in episode_urls:
        for episode in season:
            writer.writerow([episode])
    