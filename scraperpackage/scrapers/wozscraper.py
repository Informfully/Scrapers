from bs4 import BeautifulSoup
from datetime import datetime
import feedparser
import urllib.request
from .utils.utils import create_article

# Define the default name and feed of the news outlet
NEWS_OUTLET = "WOZ"
RSS_FEED_LIST = [
    # 'https://www.woz.ch/t/schweiz/feed'
    # 'https://www.woz.ch/t/wirtschaft/feed'
    # 'https://www.woz.ch/t/international/feed'
    # 'https://www.woz.ch/t/kultur-wissen/feed'
    'https://www.woz.ch/t/startseite/feed'
]

NEWS_LANGUAGE = "de-CH"

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
    
    return newsarticles_collection


def scrape_article(article):
    page = urllib.request.urlopen(article['url'])
    soup = BeautifulSoup(page, "html.parser")

    lead = soup.find('meta', attrs={'property': 'og:description'}).get('content')
    image = soup.find('meta', attrs={'property': 'og:image'}).get('content')
    date_published = datetime.fromisoformat(
        soup.find(
            'meta', attrs={'property': 'article:published_time'}
        ).get('content')
    )

    # There are formating issues on the website where some content is misplaced and not within the
    # content tag filtered below. 
    content = soup.find("div", attrs = {"class", "article-content"})

    body = [
        {'type': 'text', 'text': child.text}
        for child in content.children
        if child.name == 'p'
        and len(child.attrs) == 0
    ]


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
            article_props['author'] = article.get('author')

            article_list.append(article_props)

    return article_list
        