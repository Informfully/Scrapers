from bs4 import BeautifulSoup
from datetime import datetime
import feedparser
import urllib.request
from .utils.utils import create_article

NEWS_OUTLET = "SRF NEWS"
NEWS_LANGUAGE = "de-CH"
IMG_SIZE = '/320w/' # Available options are 1280, 640, 320, 160 and 80

RSS_FEED_LIST = [
    "https://www.srf.ch/news/bnf/rss/1890", # Schweiz
    "https://www.srf.ch/news/bnf/rss/1958", # Zürich
    "https://www.srf.ch/news/bnf/rss/1922", # International
    "https://www.srf.ch/news/bnf/rss/1926", # Wirtschaft
    "https://www.srf.ch/news/bnf/rss/1930", # Panorama
    "https://www.srf.ch/kultur/bnf/rss/454" # Kultur (Film & Serien, Musik, Literatur, Kunst, Bühne and Gesellschaft & Religion)
]

def scrape():
    rss_results = get_rss_feed() # Get partial article information from RSS feeds
    newsarticles_collection = []

    for article in rss_results:
        try:
            new_article = scrape_article(article)

            if new_article:
                newsarticles_collection.append(new_article)
        except Exception as e:
            print(f"Couldn't scrape article: {article['url']}")
            print(e)
    
    return newsarticles_collection

def scrape_article(article):

    # Retrieve and parse the HTML file from the url
    page = urllib.request.urlopen(article['url'])
    soup = BeautifulSoup(page, "html.parser")

    # Get meta content for publication date, lead text and image url
    publish_date_text = soup.find('meta', attrs = {'property': 'article:published_time'})['content']
    lead              = soup.find('meta', attrs = {'property': 'og:description'})['content']
    branded_image     = soup.find('meta', attrs = {'property': 'og:image'})['content']

    # Parse date and change url for unbranded image
    date_published = datetime.strptime(publish_date_text, "%Y-%m-%dT%H:%M:%S%z")
    image = branded_image.replace('/branded_srf_news/', IMG_SIZE)

    # Retrieve the article content and split the text
    content = soup.find("section", class_="article-content")
    paragraphs = [ child.text for child in content if child.name == 'p' ]
    body = [ { "type": "text", "text": paragraph } for paragraph in paragraphs ]

    # Filter out any articles that contain no text section (e.g., video-only)
    if not ( len(body) and len(lead) and len(image) ):
        return None

    document = create_article(
        url              = article['url'],
        primary_category = "NONE",
        title            = article['title'],
        lead             = lead,
        date_published   = date_published,
        language         = NEWS_LANGUAGE,
        outlet           = NEWS_OUTLET,
        image            = image,
        body             = body
    )

    return document

def get_rss_feed():
    article_list = []

    for rss_url in RSS_FEED_LIST:
        news_feed = feedparser.parse(rss_url)

        for article in news_feed['entries']:
            article_props = {}

            article_props['url'] = article['link']
            article_props['title'] = article['title']

            article_list.append(article_props)

    return article_list
