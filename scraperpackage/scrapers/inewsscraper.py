from bs4 import BeautifulSoup
import requests, json, re, os
from utils.utils import create_article
from datetime import datetime, timedelta
from bson import json_util
import utils.utils as utility

NEWS_OUTLET = "INews"
NEWS_LANGUAGE = "en-UK"
NEWS_FEEDS = ["https://inews.co.uk/category/news/environment",
              "https://inews.co.uk/category/news/politics",
              "https://inews.co.uk/category/news/sport",
              "https://inews.co.uk/category/news/money",
              "https://inews.co.uk/category/news/culture",
              "https://inews.co.uk/category/news/health",
              "https://inews.co.uk/category/news/science"]
date = datetime.utcnow()
yesterday = date - timedelta(days=1)

def scrape_sitemap(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    news_posts = soup.find_all('div', {'class': 'inews__post-jot__content-headline'})
    
    # Retrieve URLs
    url_pattern = r'https?://\S+|www\.\S+'
    urls = re.findall(url_pattern, str(news_posts))
    return urls

def scrape_article(url):

    response = requests.get(url)

    # Determine category
    if url != "http://www.w3.org/2000/svg><defs><clippath":
        pattern1 = r'/news/([^/]+)/'
        pattern2 = r'co.uk/([^/]+)/'
        try:
            category = re.findall(pattern1, url)[0]
        except:
            category = re.findall(pattern2, url)[0]
    else:
        category = "None"

    # Remap categories
    if category == 'culture':
        category = 'entertainment&arts'
    if category == 'inews-lifestyle':
        category = 'lifeandstyle'

    soup = BeautifulSoup(response.content, 'html.parser')

    # Scrape title
    if hasattr(soup.find('h1', {'class': 'headline'}), 'text'):
        title = soup.find('h1', {'class': 'headline'}).get_text()
    else:
        title = "None"

    # Scrape lead
    lead = soup.find('h2').get_text()

    # Scrape author
    authorbox = soup.find('div', {'class': 'inews__post-byline__author-link'})
    if authorbox:
        author = authorbox.find('a').get_text()
    else:
        author = "None"

    # Scrape image
    image = soup.find('img', {'class': 'w-100'})
    if hasattr(image, 'src'):
        image_src = image.get('src')
    else:
        image_src = "None"

    # Scrape article body
    try:
        content = soup.find('div', {'class': 'article-content'})
        # content = filter(lambda element: len(element.attrs) <= 1, soup.find('div', {'class': 'article-content'}))
        paragraphs = content.find_all(['p', 'h1'])
        body = []
        for p in paragraphs:
            if "Let us know:" not in p.get_text() and 'pic.twitter.com' not in p.get_text():
                element_name = p.name
                if element_name == 'h1':
                    text = utility.clean_text(p.get_text())
                    body.append({"type": "headline", "text": text})
                else:
                    text = utility.clean_text(p.get_text())

                    # If the text starts and ends with double quotation marks, treat it as a quote
                    if text.startswith("'") and text.endswith("'"):
                        body.append({"type": "quote", "text": text})
                    else:
                        text = text.replace('INews', 'Informfully').replace(' i ', ' Informfully ').replace("’", "'")
                        body.append({"type": "text", "text": text})
    except:
        print("Something fishy here", url)
        body = []

    # Scrape date
    try:
        date_string = soup.find('span', {'class': 'inews__post__pubdate'}).get_text()
    except:
        date_string = date - timedelta(days = 10)
    date_format = "%B %d, %Y %I:%M %p"
    try:
        published = datetime.strptime(date_string, date_format)
    except:
        published = "None"
    try:
        updated = soup.find('span', {'class': 'inews__post__moddate'}).get_text()
    except:
        updated = 'None'

    # Create article
    document = create_article(
        url=url,                                # string
        primary_category=category,              # string
        sub_categories="None",                  # string
        title=utility.clean_text(title),        # string
        lead=utility.clean_text(lead),          # string
        author=author,                          # string
        date_published=published,               # datetime
        date_updated=updated,                   # string
        language=NEWS_LANGUAGE,                 # string
        outlet=NEWS_OUTLET,                     # string
        image=image_src,                        # string
        body=body                               # list of dictionaries
    )
    return document

# The scraper will retrieve news article URLs from the RSS feed and parse the HTML documents
def scrape():

    articles = []
    retrieved_articles = 0
    skipped_articles = 0

    for feed in NEWS_FEEDS:
        urls = scrape_sitemap(feed)
        for url in urls:
            url = url.replace('"', '')
            article = scrape_article(url)

            # Check if article is eligible for recommendation
            if len(article['body']) >= 7 and article['title'] != "None" and article["image"] != "None":
                articles.append(article)
                retrieved_articles += 1
            else:
                skipped_articles += 1

    print(retrieved_articles, skipped_articles)

    return articles
