import json
import feedparser
from datetime import datetime
from urllib.request import Request, urlopen
import re
from os import getenv
from base64 import b64encode
from .utils.utils import create_article
import traceback

NEWS_OUTLET = "CH Media"
NEWS_OUTLETS = {
    "Solothurner Zeitung": "https://www.solothurnerzeitung.ch/recent.rss",
    "Oltner Tagblatt": "https://www.oltnertagblatt.ch/recent.rss",
    "Tagblatt": "https://www.tagblatt.ch/recent.rss",
}
NEWS_LANGUAGE = "de-CH"

API_URL_TEMPLATE = "https://delivery-livingdocs-chmedia.nzz-tech.ch/nzz/api/v1/documents/{id}/latestPublication/renditions?rendition_name=lovely"

def scrape():
    articles = []

    for news_outlet, rss_url in NEWS_OUTLETS.items():
        id_list = get_ids_from_rss(rss_url)
        for id in id_list:
            try:
                new_article = get_article_from_api(id, news_outlet)

                if new_article:
                    articles.append(new_article)
            except:
                print(API_URL_TEMPLATE.format(id=id))
                traceback.print_exc()

    return articles

def get_article_from_api(id, news_outlet):
    api_url = API_URL_TEMPLATE.format(id=id)
    request = Request(api_url)
    request.add_header("Authorization", f"Basic {getenv('CHMBASE64')}")
    page = urlopen(request)
    article = json.loads(page.read())

    metadata = article['metadata']
    url = metadata['origin'] + metadata['url']
    title = metadata['title']
    image = metadata.get('teaserImage', {}).get('url')
    lead = metadata.get('leadText')
    date_published = datetime.strptime(metadata['publicationDate'], "%Y-%m-%dT%H:%M:%S.%fZ")
    date_updated = datetime.strptime(metadata["publicationLastUpdated"], "%Y-%m-%dT%H:%M:%S.%fZ")

    author = metadata.get('author')

    # Check if author is None or ""
    if not author:

        # Check nzzAuthor field as second priority
        if metadata.get('nzzAuthors') != None and len(metadata.get('nzzAuthors')):
            author = metadata['nzzAuthors'][0].get('name')
        else:
            author = None

    body = []

    for item in article['channels']['lovely']['content']:
        if item['component'] == 'p':
            body.append({
                'type': 'text',
                'text': item['content']['text']
            })

    if not (image and lead and body):
        return None

    return create_article(
        url              = url,
        primary_category = "NONE",
        title            = title,
        lead             = lead,
        date_published   = date_published,
        date_updated     = date_updated,
        language         = NEWS_LANGUAGE,
        outlet           = news_outlet,
        image            = image,
        body             = body,
        author           = author
    )

def get_ids_from_rss(rss_url):
    newsfeed = feedparser.parse(rss_url)

    id_list = []

    for item in newsfeed['entries']:
        url = item['link']
        match = re.search(r"\d+$", url)

        if match != None:
            id = match.group(0)
            id_list.append(id)
    
    return id_list
