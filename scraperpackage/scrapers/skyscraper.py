from bs4 import BeautifulSoup
import feedparser, requests, json, os
from utils.utils import create_article
from datetime import datetime
from dateutil import parser
from bson import json_util
import utils.utils as utility

# Define the default name and feed of the news outlet
NEWS_OUTLET = "SkyNews"
NEWS_FEEDS = [{'url': "https://feeds.skynews.com/feeds/rss/home.xml", 'category': "home"},
              {'url': "https://feeds.skynews.com/feeds/rss/uk.xml", 'category': "uk news"},
              {'url':"https://feeds.skynews.com/feeds/rss/world.xml", 'category': "world"},
              {'url':"https://feeds.skynews.com/feeds/rss/business.xml", 'category': "business"},
              {'url':"https://feeds.skynews.com/feeds/rss/politics.xml", 'category': "politics"},
              {'url':"https://feeds.skynews.com/feeds/rss/technology.xml", 'category': "technology"},
              {'url':"https://feeds.skynews.com/feeds/rss/entertainment.xml", 'category': "entertainment&arts"}]
NEWS_LANGUAGE = "en-UK"
DEFAULT_AUTHOR = "NONE"
DEFAULT_CATEGORY = "NONE"
date = datetime.utcnow()

# Read the RSS feed and retrieve URL and article metadata
def get_rss_feed(feed):

    article_list = []
    newsFeed = feedparser.parse(feed)

    # Collection to hold the article specific metadata
    for rss_article in newsFeed.entries:

        # Collection to hold the article specific metadata
        article_props = {}
        article_props['url'] = rss_article.link
        article_props['title'] = rss_article.title
        article_props['lead'] = rss_article.summary
        article_props['image'] = rss_article.media_content[0].get('url')
        article_list.append(article_props)

    return article_list

# Scrape individual articles and combine existing RSS meta-data with text from website
def scrape_article(article, category):

    response = requests.get(article['url'])
    soup = BeautifulSoup(response.content, 'html.parser')

    # Scrape image
    image = soup.find('img', {'class': 'sdc-article-image__item'})['src']

    # Scrape article text
    divs = soup.find_all('div', {'data-component-name': 'sdc-article-body'})
    all_paragraphs = []

    for div in divs:
        paragraphs = div.find_all('p')
        all_paragraphs.extend(paragraphs)

    filtered_paragraphs = [p for p in all_paragraphs if not p.has_attr('class')][1:]
    body = []

    for p in filtered_paragraphs:
        if "Read more" not in p.text:
            if p.find('strong'):
                text = utility.clean_text(p.text)
                body.append({"type": "headline", "text": text})
            else:
                text = utility.clean_text(p.text)
                body.append({"type": "text", "text": text})

    # Scrape date
    datestring = soup.find('p', {'class': 'sdc-article-date__date-time'}).text.split(',',1)[0]
    published = parser.parse(datestring)

    # Scrape author
    if hasattr(soup.find('span', {'class': 'sdc-article-author__name'}), 'text'):
        author = soup.find('span', {'class': 'sdc-article-author__name'}).text.replace('\n', "")
    else:
        author = DEFAULT_AUTHOR

    title = article['title'].replace('and #163;', 'GBP').replace('and #8364;', '€')

    # Create article
    document = create_article(
        url=article['url'],
        primary_category=category,          # string
        sub_categories=DEFAULT_CATEGORY,    # string
        title=utility.clean_text(article['title']),             # string
        lead=utility.clean_text(article['lead']),               # string
        author=author,                      # string
        date_published=published,           # datetime
        date_updated=published,             # datetime - NEEDS WORK
        language=NEWS_LANGUAGE,             # string
        outlet=NEWS_OUTLET,                 # string
        image=image,                        # image
        body=body                           # list of dictionaries
    )
    return document

# The scraper will retrieve news article URLs from the RSS feed and parse the HTML documents
def scrape():

    # Collection to store complete articles
    newsarticles_collection = []

    for e in NEWS_FEEDS:
        feed = e.get('url')
        category = e.get('category')

        # Get partial article information from RSS feeds
        rss_results = get_rss_feed(feed)
        retrieved_articles = 0
        skipped_articles = 0
        for article in rss_results:
            try:
                new_article = scrape_article(article, category)

                # Check if article is eligible for recommendation
                if new_article and len(new_article['body']) >= 7 and new_article['image'] != "None":
                   newsarticles_collection.append(new_article)
                   retrieved_articles += 1

            except Exception as e:
                print(f"Couldn't scrape article: {article['url']}")
                print(e)
                skipped_articles += 1

    print(retrieved_articles, skipped_articles)

    return newsarticles_collection
