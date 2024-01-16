import requests
from bs4 import BeautifulSoup
from DatabaseManager import DatabaseManager
import csv
from sys import exit

dbm = DatabaseManager()
podcast = 'Flirting With Models'

url_list = []

with open('episode_urls.csv', 'r') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        url_list.append(row[0])

def get_episode_data(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the 'h2' tag, checking if it exists
    title_tag = soup.find('h2')
    title = title_tag.get_text() if title_tag else "Title not found"
    
    #strip the title of any escape characters:
    title = title.replace('\n', '').replace('\t', '').replace('\r', '')
    

    # Extract the transcript (adjust as needed)
    transcript_div = soup.find('div', class_='entry-content')
    transcript = transcript_div.get_text() if transcript_div else "Transcript not found."

    return {
        'URL': url,
        'Title': title,
        'Transcript': transcript
    }

for url in url_list:
    episode_data = get_episode_data(url)
    dbm.insert_podcast(podcast, episode_data['Title'], episode_data['URL'], episode_data['Transcript'])
