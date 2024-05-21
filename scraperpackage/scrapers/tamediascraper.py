import json
import traceback
import urllib.request
from bs4 import BeautifulSoup
from datetime import datetime
from .utils.utils import create_article
import traceback

# Define the default name and feed of the news outlet
NEWS_OUTLET = 'Tamedia'
NEWS_LANGUAGE = 'de-CH'
INPUT_FILE = '20minfeed.json'
JSON_FEED_URLS = {
    '20 Minuten': 'https://partner-feeds.20min.ch/uzh/rss/20minuten/index?token=partner-uzh-e87z8e7rf8e7h8d00w09e',
    'Tagesanzeiger': 'https://partner-feeds.publishing.tamedia.ch/uzh/rss/tagesanzeiger/index?token=partner-uzh-e87z8e7rf8e7h8d00w09e'
}

def scrape():
    new_articles = []
    items_dict = get_feed_items()

    for newsoutlet, items_list in items_dict.items():

        for item in items_list:
            try:
                new_article = scrape_article(newsoutlet, item)
                new_articles.append(new_article)
            except:
                print("Could'nt scrape article")
                traceback.print_exc()

    return new_articles


def scrape_article(newsoutlet, item):
    # Retreive first image in slideshow
    if len(item['mediaSlideshow']):
        image = item['mediaSlideshow'][0]['url']
    else:
        image = None
    
    # Split article content into paragraphs
    body = []
    soup = BeautifulSoup(item['content'], 'html.parser')
    
    for index, child in enumerate(soup.children):
        # If there is no media slide show, the image is likely in the text
        if image == None and child.name == 'img':
            image = child['src']

        # Skip the first paragraph that is the lead
        # Only take text from <p> and <a> elements
        # 
        if (
            index == 0
            or (child.name != 'p' and child.name != 'a')
            or child.text.startswith("<strong>")
        ):
            continue

        body.append({
            'type': 'text',
            'text': child.text
        })
            
    document = create_article(
        url              = item['link'],
        primary_category = "NONE",
        title            = item['title'],
        lead             = item['description'],
        date_published   = datetime.strptime(item['pubDate'], "%Y-%m-%dT%H:%M:%S.%fZ"),
        language         = NEWS_LANGUAGE,
        outlet           = newsoutlet,
        image            = image,
        body             = body
    )

    return document

def get_feed_items():
    article_items = {}

    for newsoutlet, json_feed_url in JSON_FEED_URLS.items():
        json_feed = urllib.request.urlopen(json_feed_url)
        json_object = json.load(json_feed)
        
        article_items[newsoutlet] = json_object['items']

    return article_items
