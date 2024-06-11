from bs4 import BeautifulSoup
import feedparser, requests, json, os
from utils.utils import create_article
from datetime import datetime
from dateutil import parser
import re
from bson import json_util
import utils.utils as utility

def remove_html_tags(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

# Define the default name and feed of the news outlet
NEWS_OUTLET = "EveningStandard"
NEWS_FEEDS = ["https://www.standard.co.uk/rss"]
NEWS_LANGUAGE = "en-UK"

date = datetime.utcnow()

# Read the RSS feed and retrieve URL and article metadata
def get_rss_feed(feed):
    article_list = []
    newsFeed = feedparser.parse(feed)

    for rss_article in newsFeed.entries:
        # Collection to hold the article specific metadata
        article_props = {}
        article_props['url'] = rss_article.link
        article_props['title'] = rss_article.title
        article_props['lead'] = rss_article.summary
        article_props['author'] = rss_article.author
        try:
            article_props['primaryCategory'] = rss_article.tags
        except:
            article_props['primaryCategory'] = "None"
        datestring = rss_article.published.split(" GMT")[0]
        published = parser.parse(datestring)
        article_props['date_published'] = published
        try:
            article_props['image'] = rss_article.media_content
        except:
            article_props['image'] = "None"
        article_props['date_updated'] = rss_article.updated

        article_list.append(article_props)

    return article_list

# Scrape individual articles and combine existing RSS meta-data with text from website
def scrape_article(article):
    response = requests.get(article['url'])
    soup = BeautifulSoup(response.content, 'html.parser')

    # Scrape article text
    divs = soup.find('div', {'class': 'sc-enDNfw iLaNIc'})
    paragraphs = []

    if divs:
        # Find all 'div' elements with class 'sc-kxZkPw kMnNar' and remove them
        for unwanted_div in divs.find_all('div', {'class': 'sc-kxZkPw kMnNar'}):
            unwanted_div.extract()
        # Find and add all 'p' and 'h2' tags within the modified 'divs' element
        block = divs.find_all(['p', 'h2'])
        paragraphs.extend(block)
        #print(block)

    body = []

    for p in paragraphs:
        if ("Read more:" not in p.text and "Read more here" not in p.text and
                "Sign up for exclusive newsletters" not in p.text and
                "By clicking Sign up you confirm that" not in p.text and
                "MORE ABOUT" not in p.text and "Additional report by PA Sport" not in p.text and
                "Have your say..." not in p.text and
                "This site is protected by reCAPTCHA" not in p.text):
            if p.get_text().startswith('"') and p.get_text().endswith('"'):
                # If the text starts and ends with double quotation marks, treat it as a quote
                cleaned_text = utility.clean_text(p.get_text())
                body.append({"type": "quote", "text": cleaned_text})
            elif p.name == 'h2':
                cleaned_text = utility.clean_text(p.get_text())
                body.append({"type": "headline", "text": cleaned_text})
            else:
                cleaned_text = utility.clean_text(p.get_text())
                body.append({"type": "text", "text": cleaned_text})

    # Scrape category
    category = article['primaryCategory'][0]['term']

    # Rename categories
    if category == 'Business' or category == 'Business News':
        category = 'business'
    if category == 'Crime':
        category = 'crime'
    if category == 'Environment':
        category = 'environment'
    if category == 'Film' or category == 'Music' or category == 'Showbiz' or category == 'Celebrity News':
        category = 'entertainment&arts'
    if category == 'Football':
        category = 'football'
    if category == 'Health':
        category = 'health'
    if category == 'Fashion' or category == 'Lifestyle':
        category = 'lifeandstyle'
    if category == 'Money':
        category = 'money'
    if category == 'Politics':
        category = 'politics'
    if category == 'Boxing' or category == 'Golf' or category == 'F1' or category == 'Tennis':
        category = 'sport'
    if category == 'Science':
        category = 'science'
    if category == 'Tech':
        category = 'technology'
    if category == 'UK':
        category = 'uk news'
    if category == 'World':
        category = 'world'

    # Sreate article
    document = create_article(
        url=article['url'],                                         # string
        primary_category=category,                                  # string
        sub_categories="None",                                      # string
        title=utility.clean_text(article['title']),                 # string
        lead=utility.clean_text(remove_html_tags(article['lead'])), # string
        author=article['author'],                                   # string
        date_published=article['date_published'],                   # datetime
        date_updated=article['date_updated'],                       # datetime
        language=NEWS_LANGUAGE,                                     # string
        outlet=NEWS_OUTLET,                                         # string
        image=article['image'][0]['url'],                           # string
        body=body                                                   # list of dictionaries
    )
    return document

# The scraper will retrieve news article URLs from the RSS feed and parse the HTML documents
def scrape():

    # Collection to store complete articles
    newsarticles_collection = []
    retrieved_articles = 0
    skipped_articles = 0

    for feed in NEWS_FEEDS:

        # Get partial article information from RSS feeds
        rss_results = get_rss_feed(feed)

        for article in rss_results:
            try:
                new_article = scrape_article(article)
                # Check if article is eligible for recommendation
                if new_article and len(new_article['body']) >= 7:
                    newsarticles_collection.append(new_article)
                    retrieved_articles += 1
            except Exception as e:
                print(f"Couldn't scrape article: {article['url']}")
                print(e)
                skipped_articles += 1

    print(retrieved_articles, skipped_articles)

    return newsarticles_collection