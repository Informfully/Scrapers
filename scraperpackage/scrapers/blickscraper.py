from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import feedparser
import json
import urllib.request
from jsonpath_ng.ext import parse
from .utils.utils import create_article

# Define the default name and feed of the news outlet
NEWS_OUTLET = "BLICK"
NEWS_FEED = "https://www.blick.ch/rss.xml"
NEWS_LANGUAGE = "de-CH"

# Predefined prefex to access an articles JSON file using the URL from the RSS feed
API_VERSION = "1.6.2"

# A number of imwidth options are available: 375, 500, 750 & 1000 (larger images will slow down the app)
IMAGE_TEMPLATE = "https://img.blick.ch{path}?imwidth=500&ratio=16_9"

# The scraper will retrieve news article URLs from the RSS feed and parse the HTML documents
def scrape():
    rss_results = get_rss_feed() # Get partial article information from RSS feeds
    newsarticles_collection = [] # Collection to store complete articles

    for article in rss_results:
        try:
            new_article = scrape_article(article)

            if new_article:
                newsarticles_collection.append(new_article)
        except Exception as e:
            print(f"Couldn't scrape article: {article['url']}")
            print(e)

    return newsarticles_collection

# Extract other information through api
def scrape_article(article):
    json_url = article['url'].replace(
        "//www.blick.ch",
        "//api.blick.ch/" + API_VERSION
    )
    api_response = urllib.request.urlopen(json_url)
    json_content = api_response.read()
    article_content = json.loads(json_content.decode('utf-8'))

    # Retrieve article text via jsonpath and append them together
    jsonpath_expression = parse('$..content[?@.kind[1]="text-body"].text')
    body_html = ''.join([ match.value for match in jsonpath_expression.find(article_content) ])

    # Parse html to only keep the text of <p> elements
    body_soup = BeautifulSoup(body_html, 'html.parser')
    paragraphs = [ child.text for child in body_soup if child.name == 'p' ]

    # Transform article text into right format
    body = [ { "type": "text", "text": paragraph } for paragraph in paragraphs ]

    # Extract lead text
    lead = article_content["metadata"]["metaDescription"]

    # Get metadata and cut off decimal minutes (and timezone)
    publish_date_text = article_content["metadata"]["firstPublishedDate"][:16]
    date_published = datetime.strptime(publish_date_text, "%Y-%m-%dT%H:%M")

    modify_date_text = article_content["metadata"]["lastModifiedDate"][:16]
    modify_date = datetime.strptime(modify_date_text, "%Y-%m-%dT%H:%M")

    # Image metadata from API only contains the path
    # Format with domain name and parameters
    image = IMAGE_TEMPLATE.format(path=article_content["metadata"]["teaser"]["image"]["src"])

    # Extract category info
    primary_category = article_content["metadata"]["breadcrumbs"][1]["title"]
    sub_categories = [ category["title"] for category in article_content["metadata"]["breadcrumbs"][1:] ]

    # Filter out any articles that contain no text section (e.g., video-only)
    if not ( len(body) and len(lead) and len(image) ):
        return None

    document = create_article(
        url=article['url'],
        primary_category=primary_category,
        sub_categories=sub_categories,
        title=article['title'],
        lead=lead,
        author=article['author'],
        date_published=date_published,
        date_updated=modify_date,
        language=NEWS_LANGUAGE,
        outlet=NEWS_OUTLET,
        image=image,
        body=body
    )
    
    return document

# Read the RSS feed and retrieve URL and article metadata
def get_rss_feed():
    article_list = []
    newsFeed = feedparser.parse(NEWS_FEED)

    for rss_article in newsFeed.entries:

        # Collection to hold the article specific metadata
        article_props = {}
        article_props['url'] = rss_article.link
        article_props['title'] = rss_article.title

        # Some non-text articles (e.g., videos or photo slideshows) have no other and get filtered out
        try:
            article_props['author'] = rss_article.author
        except:
            continue

        article_list.append(article_props)

    return article_list
