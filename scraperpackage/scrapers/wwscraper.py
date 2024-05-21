from datetime import datetime
from bs4 import BeautifulSoup
from .utils.utils import create_article
from urllib import request, parse
import os

from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium import webdriver

# Define the default name and feed of the news outlet
NEWS_OUTLET = "Die Weltwoche"

# You can now log in directly via the overview page         
WEBSITE = "https://www.weltwoche.ch/inhaltsverzeichnis.html"    # OVERVIEW OF THE CURRENT ISSUE (ONE WEEK)

NEWS_LANGUAGE = "de-CH"

# International news (see overview page header) are exluded, for they are in English
FILTER_LIST = ['Editorial', 'Éditorial', 'Kommentare', 'Inside Washington',
               'intern-die-weltwoche', 'leserbriefe-die-weltwoche',
               'portraet-der-woche', 'leser-fragen']

def scrape():
    driver = get_driver()
    links = get_links()
    articles = []

    # Only log in if the scraper is used without a valid Firefox profile that holds
    # the site's credentials and a session cookie. Note, however, that by doing so the website might
    # not work for Selenium is unable to store login tokens for creating sessions.
    if os.getenv('WWLOGIN') == 'True':
        login(driver)

    for link in links:
        get_article_content(link, driver)

    # Terminate scraping session and close browser
    driver.close()
    driver.quit()

    return get_newsarticles()


def get_links(driver):
    article_links = []

    data = parse.urlencode({
        "tx_iafeditionmanager_editionmanager[requestThroughAjax]": 1,
        "tx_iafeditionmanager_editionmanager[pluginId]": 114,
        "tx_iafeditionmanager_editionmanager[argumentsFromAjax]":'{"getArguments":[],"flexOptions":{"overview":"41","epaper":"64","searchPid":"8","adminemail":"noreply@weltwoche.ch","ampPid":"82","articleDetailPid":"15","articleDetailPage":"15","characterLimit":"","login":"39","payment":"19","register":"45","myprofile":"70","articleIds":"","sliderArticleIds":"","topArticles":"","editionId":"","previousArticleIds":"","teaserLayout":"1"}}'
    }).encode()

    req = request.Request('https://www.weltwoche.ch/?tx_iafeditionmanager_editionmanager[action]=editionOverview', data=data)
    resp = request.urlopen(req)

    resp_json = json.loads(resp.read())
    soup = BeautifulSoup(resp_json['html'], 'html.parser')

    for element in soup.find_all('a'):
        print(element['href'])

    { element['href'] for element in soup.find_all('a') }

    # Exclude all outlet-specifc stories that contain no relevant information
    for word in FILTER_LIST:

        # Skip article if tag is found
        match = str(link_tag).find(word)
        if match > 1:
            continue


    return article_links


def get_article_content(driver, url):
    driver.get(url)
    source = driver.find_element_by_class_name("body-prev")
    html = source.get_attribute('outerHTML')

    # Pard the source of the website to better select end edit the necessary elements
    soup = BeautifulSoup(html, "html.parser", multi_valued_attributes=None)
    
    # Extract the image of the news article (4th image on page)
    image = ''
    image_raw = soup.find_all("img", class_="img-responsive")
    if len(image_raw) > 3:
        image = image_raw[3].get('src', '')

    # Extract article content
    detail = soup.find("div", class_="detail-content article_detail")

    title = ''
    if detail.h2:
        title = detail.h2.string

    lead = ''
    lead_tag = detail.find('p', class_='article-detail-lead')
    if lead_tag:
        lead = lead_tag.string

    publish_date = None
    date_tag = detail.find('h5', class_="font-blue")
    if date_tag:
        publish_date = datetime.strptime(date_tag.string, '%d.%m.%Y')

    author = ''
    author_tag = detail.find('div', class_='font-italic')
    if author_tag:
        author = author_tag.string

    # Extract the main text of the news article
    body = []
    for child in detail.children:
        if (
            child.name == 'p'
            and child.get('class') != 'article-detail-lead'
            and child.string
            and child.string.strip() != ''
        ):
            body.append({
                'type': 'text',
                'content': child.string
            })

    # Appent the scraped date to the property list that gets returned and stored in the datbase
    document = create_article(
        url,
        None,
        title,
        lead,
        publish_date,
        NEWS_OUTLET,
        NEWS_OUTLET,
        body,
        author,
        image
    )

    return document

def login(driver):
    driver.get(WEBSITE)
    driver.implicitly_wait(10)
    username = driver.find_element_by_id("mainloginEmail")
    username.clear()
    username.send_keys(os.getenv('WWUSER'))

    password = driver.find_element_by_id("mainloginPassword")
    password.clear()
    password.send_keys(os.getenv('WWPASS'))

    driver.find_element_by_id("mainloginSubmit").click()

def get_driver():
    # Retrieve browser profile that contains credentials and session cookies for online scraping
    firefox_profile = FirefoxProfile(os.getenv('FIREFOXPROFILEPATH'))
    firefox_profile.update_preferences()

    driver = webdriver.Firefox(firefox_profile = firefox_profile, executable_path = os.getenv('GECKODRIVERPATH'))

    return driver