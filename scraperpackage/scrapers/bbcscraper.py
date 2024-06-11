from bs4 import BeautifulSoup
import feedparser, requests, json, os, re
from utils.utils import create_article
from datetime import datetime
from bson import json_util
import utils.utils as utility

NEWS_OUTLET = "BBC"
NEWS_FEEDS = ["http://feeds.bbci.co.uk/news/rss.xml"]
NEWS_LANGUAGE = "en-UK"
DEFAULT_AUTHOR = "NONE"
DEFAULT_CATEGORY = "NONE"
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
        try:
            article_props['lead'] = rss_article.summary
        except:
            article_props['lead'] = "Click here to read more"

        # Added conversion to make it an actual string
        datestring = str(rss_article.published.split(" GMT")[0])
        # What the current date & time looks like, for reference: "Tue, 22 Aug 2023 09:44:11"

        # Conversion to datetime and match target format of database
        converted_datetime = (datetime.strptime(datestring, '%a, %d %b %Y %H:%M:%S'))
        formatted_datetime = converted_datetime.strftime('%Y%m%d')
        article_props['date_published'] = formatted_datetime
        # print(formatted_datetime)
        article_list.append(article_props)

    return article_list

# Filter out text snippets that should not be scraped for the main text
def should_filter(p):
    text = p.get_text()
    class_list = p.get('class')

    substrings_to_exclude = [
        "Watch:",
        "This video can not be played",
        "BBC is not responsible",
        "ssrcss-17zglt8-PromoHeadline",
        "Sign up for our morning newsletter",
        "Listen to Newsbeat live at",
        "Follow BBC ",
        "Follow the BBC "
    ]

    return all(substring not in text for substring in
               substrings_to_exclude) and "ssrcss-17zglt8-PromoHeadline" not in class_list

# Scrape individual articles and combine existing RSS meta-data with text from website
def scrape_article(article):

    response = requests.get(article['url'])
    soup = BeautifulSoup(response.content, 'html.parser')
    filtered_paragraphs = [p for p in soup.findAll({'p': {'data-component': 'text-block'}})]
    body = []
    primary_category = []
    sub_categories = []

    # Determine text type for main body
    for p in filtered_paragraphs:
        if should_filter(p):
            text = p.get_text()

            # If the text starts and ends with double quotation marks, treat it as a quote
            if text.startswith('"') and text.endswith('"'):
                cleaned_text = utility.clean_text(text)
                body.append({"type": "quote", "text": cleaned_text})
            else:
                cleaned_text = utility.clean_text(text)
                body.append({"type": "text", "text": cleaned_text})

    # Categories (scrape all categories of an article)
    categories = [item.text for item in soup.find_all('a', {'class': 'ssrcss-w6az1r-StyledLink ed0g1kj0'})]

    # Filter categories of interests
    if ("Science" in categories) and ("Climate change" in categories):
        # If there is a match, add the following custom category as primary category
        primary_category = 'environment'
        # Add all categories as subcategories
        sub_categories = ', '.join([str(c) for c in categories[0:]])
    else:
        # Else, add the first category as primary category
        primary_category = categories[0]
        # Add remaining categories as subcategories
        sub_categories = ', '.join([str(c) for c in categories[1:]])
    if len(sub_categories) == 0:
        sub_categories = DEFAULT_CATEGORY

    # Remap categories
    if primary_category == 'Business':
        primary_category = 'business'
    if primary_category == 'Entertainment & Arts':
        primary_category = 'entertainment&arts'
    if primary_category == 'Health':
        primary_category = 'health'
    if primary_category == 'Politics':
        primary_category = 'politics'
    if primary_category == 'Science':
        primary_category = 'science'
    if primary_category == 'Tech':
        primary_category = 'technology'
    if primary_category == 'UK':
        primary_category = 'uk news'
    if primary_category == 'World':
        primary_category = 'world'

    # Scrape image
    main_image = soup.find('img').get("src")

    # Scrape author
    author = soup.find('div', {'class': 'ssrcss-68pt20-Text-TextContributorName e8mq1e96'}).text.replace('By ', '')
    if len(author) == 0:
        author = DEFAULT_AUTHOR

    # Full article (JSON format document for database collection)
    document = create_article(
        url=article['url'],                         # string
        primary_category=primary_category,          # string
        title=utility.clean_text(article['title']), # string
        lead=utility.clean_text(article['lead']),   # string
        author=author,                              # string
        date_published=article['date_published'],   # datetime
        date_updated=article['date_published'],     # datetime
        language=NEWS_LANGUAGE,                     # string
        outlet=NEWS_OUTLET,                         # string
        image=main_image,                           # string
        body=body                                   # list of dictionaries
    )

    return document


# The scraper will retrieve news article URLs from the RSS feed and parse the HTML documents
def scrape():

    # Collection to store complete articles
    newsarticles_collection = []
    retrieved_articles = 0
    skipped_articles = 0

    # Get partial article information from RSS feeds
    for feed in NEWS_FEEDS:
        rss_results = get_rss_feed(feed)
        for article in rss_results:
            try:
                new_article = scrape_article(article)
                if new_article:
                    newsarticles_collection.append(new_article)
                    retrieved_articles += 1
            except Exception as e:
                print(f"Couldn't scrape article: {article['url']}")
                print(e)
                skipped_articles += 1

    print(retrieved_articles, skipped_articles)

    return newsarticles_collection
