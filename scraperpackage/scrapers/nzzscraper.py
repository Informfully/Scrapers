import bs4
from datetime import datetime
import feedparser
import json
import re
import urllib.request
from .utils.utils import create_article
import traceback

# Define the default name and feed of the news outlet
NEWS_OUTLET = "NZZ"
RSS_FEED_LIST = ["https://www.nzz.ch/recent.rss",
                "https://www.nzz.ch/startseite.rss",
                "https://www.nzz.ch/international.rss",
                "https://www.nzz.ch/schweiz.rss",
                "https://www.nzz.ch/wirtschaft.rss",
                "https://www.nzz.ch/finanzen.rss",
                "https://www.nzz.ch/feuilleton.rss",
                "https://www.nzz.ch/zuerich.rss",
                "https://www.nzz.ch/panorama.rss",
                "https://www.nzz.ch/wissenschaft.rss",
                "https://www.nzz.ch/digital.rss"]

NEWS_LANGUAGE = "de-CH"

# Define the HTML tags that hold the information that needs to be scraped
CONTENT_TAG = ["container container--article layout--regular",
               "container container--article layout--opinion"]

def scrape():
    rss_results = get_rss_feed()
    newsarticles_collection = []

    for article in rss_results:
        try:
            new_article = scrape_article(article)

            if new_article:
                newsarticles_collection.append(new_article)
        except Exception as e:
            print(f"Couldn't scrape article: {article['url']}")
            print(e)
            traceback.print_exc()
            
    return newsarticles_collection

def scrape_article(article):
    
    # Retrieve and parse the HTML file the news article URL is pointing to
    page = urllib.request.urlopen(article['url'])
    soup = bs4.BeautifulSoup(page, "html.parser")


    if 'layout--regular' in str(soup):
        content = soup.find_all("section", attrs = {"class", CONTENT_TAG[0]})

    if 'layout--opinion' in str(soup):
        content = soup.find_all("section", attrs = {"class", CONTENT_TAG[1]})
    
    format = str(content[0])
    index = format.find('data-v-7eb9e870="" pagetype="Article">')
    offset = len('data-v-7eb9e870="" pagetype="Article">')
    format = format[index + offset : ]
    sections = format.split('</p> <!-- --><!-- -->')
    image = str(article["lead"]).replace('S=W200M,H200M', 'S=W640M,H640M')

    date = soup.find_all("time", attrs = {"class", 'metainfo__item metainfo__item--date'})
    dateStart = str(date[0]).find('>')
    dateEnd = str(date[0]).find('Uhr')
    publishDateRaw = str(date[0])[dateStart + 1 : dateEnd]
    publishDateRaw = publishDateRaw.replace(" ", "")
    publishDateRaw = publishDateRaw.replace("\n", "")
    publishDate = datetime.strptime(publishDateRaw, "%d.%m.%Y,%H.%M")

    errorFlag = 0
    
    # Collection for storing all the paragaphs of an article's main text
    body = []

    for section in sections:
        edit = section
        edit = re.sub('<(.*?)>', '', edit)
        edit = re.sub('\\n\\n(.*?)\\n', '', edit)
        edit = edit.replace("\u2005", "'")
        edit = edit.replace("\xa0", " ")
        edit = edit.replace("    ", "")
        edit = edit.replace("   ", "")
        edit = edit.replace("  ", " ")
        edit = edit.replace("\t", "")
        edit = re.sub('\\n(.*?).\dn', ' ', edit)
        edit = re.sub('Quelle(.*?).\\n', ' ', edit)
        edit = re.sub('\.(.*?)/ EPA', ' ', edit)
        edit = re.sub('\.(.*?)/ Reuters', ' ', edit)
        edit = re.sub('\.(.*?)/ Keystone', ' ', edit)
        edit = re.sub('(.*?)/ Asiapac', '', edit)
        edit = re.sub('(.*?)/ Getty Images', '', edit)

        if ('Mehr zum Thema\n' in edit) or ('Mehr zum Thema \n' in edit) or ('Mitarbeit: ' in edit):
            errorFlag = 1
        
        # Make sure the section still contains valid characters
        if (len(edit) > 1) and (errorFlag == 0):
            if '\n \n' not in edit:
                dbFormat = {"type": "text",
                            "text": edit}

                body.append(dbFormat)

    if not (len(body) and len(image) and len(article['lead']) and len(article['title'])):
        return None

    document = create_article(
        url              = article['url'],
        title            = article['title'],
        lead             = article['lead'],
        primary_category = None,
        date_published   = publishDate,
        language         = NEWS_LANGUAGE,
        outlet           = NEWS_OUTLET,
        image            = image,
        body             = body
    )

    return document

def get_rss_feed():
    article_list = []

    for rss_url in RSS_FEED_LIST:
        newsFeed = feedparser.parse(rss_url)

        for article in newsFeed['entries']:
            article_props = {}

            try:    
                article_props['url'] = article['link']
                article_props['title'] = article['title'].replace("\xa0", " ")
                article_props['lead'] = article['summary']
                article_props['datePublished'] = datetime(*article['published_parsed'][0:6])
            except:
                continue

            article_list.append(article_props)

    return article_list
