from scraperpackage.scrapers import tamediascraper, blickscraper, srfscraper, wozscraper, chmediascraper
from scraperpackage.pipeline import duplicatedetector
from scraperpackage.mongomanager import MongoManager
from scraperpackage.logger import Logger
from dotenv import load_dotenv
from traceback import print_exc
from os import getenv

def main():

    # Set environment variables from .env file
    load_dotenv() 

    # Load the website-specific scrapers
    scraper_modules = [srfscraper]

    with Logger() as logger:
        with MongoManager() as db:
            
            # Initialize PyMongo collections
            staging_collection = db[getenv("COLLECTIONSTAGING")]
            articles_collection = db[getenv("COLLECTIONARTICLES")]

            # Empty staging collection for new articles
            staging_collection.delete_many({})

            # Scraping phase
            for scraper_module in scraper_modules:
                try:
                    new_articles = scraper_module.scrape()
                    result = staging_collection.insert_many(new_articles)
                    logger.log(f'Inserted {len(result.inserted_ids)} articles into staging from {scraper_module.NEWS_OUTLET}', 'Scraping Phase')
                except Exception as e:
                    logger.log(str(e), scraper_module.NEWS_OUTLET, is_error=True)
                    print_exc()

            # Check if any articles were scraped
            if staging_collection.count_documents({}) == 0:
                logger.log('No articles have been scraped', 'Scraping phase', is_error=True)
                return 0
            else:
                logger.log(f'{staging_collection.count_documents({})} articles have been scraped', 'Scraping phase')

            # Duplication detection
            try:
                new_count, duplicate_count = duplicatedetector.duplicate_check(staging_collection, articles_collection)
                
                logger.log(f'Duplication detection finished. {new_count} new articles / {duplicate_count} duplicates', 'Duplication Detection')
            except Exception as e:
                logger.log(str(e), 'Duplication detection phase', is_error=True)

if __name__ == "__main__":
    main()
