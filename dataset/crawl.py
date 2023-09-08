import json
import os
import re
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://bigbangtrans.wordpress.com"
STANDARD_TIMEOUT = 10.0



def get_all_episode_links(base_url):
    episode_links = []
    response = requests.get(f"{base_url}/sitemap.xml", timeout=STANDARD_TIMEOUT)
    if response.status_code != 200:
        return episode_links
    sitemap = BeautifulSoup(response.text, features='lxml')
    episode_links = [
        link.text
        for link in sitemap.findAll('loc')
        if 'episode-' in link.text
    ]
    return episode_links

def link_to_transcript(page_link):
    LINK_REGEX_PATTERN = r"/series-([\d]+)-episode-([\d]+)"

    response = requests.get(page_link, timeout=STANDARD_TIMEOUT)
    if response.status_code != 200:
        return None
    page_content = BeautifulSoup(response.text)
    transcript = page_content.findChild('div', {'class':['post', 'entrytext']})
    transcript = [_.text for _ in transcript.findAll('p')]
    series, episode = re.search(LINK_REGEX_PATTERN, page_link).groups()
    return {"series": series, "episode": episode, "transcript": transcript}

def save_transcripts():
    links = get_all_episode_links(BASE_URL)
    for transcript_json in map(link_to_transcript, links):
        filename = os.path.join(
            os.path.dirname(__file__),
            "transcripts",
            f"series-{transcript_json.get('series')}",
            f"episode-{transcript_json.get('episode')}.json"
        )
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as fp:
            fp.write(json.dumps(transcript_json))
        print("Saved transcript for ", filename)


if __name__ == '__main__':
    save_transcripts()