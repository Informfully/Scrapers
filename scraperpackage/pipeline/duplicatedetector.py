from nltk import ngrams
from datetime import datetime, timedelta

TIME_WINDOW = 7 # Time window in days to check for duplicates
NGRAM_AMOUNT_THRESHOLD = 10 # Number of matching sentences to be detected as duplicates
NGRAM_SIZE = 5 # Sizes of one ngram

# Check for duplicates of articles in the database (limited to the last X days)
def duplicate_check(staging_collection, articles_collection):
    staging_cursor = staging_collection.find({})
    comparison_cursor = articles_collection.find({ 
        'dateScraped': {
            '$gte': datetime.now() - timedelta(days=TIME_WINDOW)
        },
    })

    new_count = 0
    duplicate_count = 0

    for staging_article in staging_cursor:
        duplicate_flag = False

        for comparison_article in comparison_cursor:

            if is_duplicate(staging_article, comparison_article):
                duplicate_flag = True
                duplicate_count += 1
                break

        comparison_cursor.rewind()

        if not duplicate_flag:
            articles_collection.insert_one(staging_article)
            new_count += 1

    return new_count, duplicate_count

def is_duplicate(article_1, article_2):
    if article_1['url'] == article_2['url']:
        return True

    ngrams_1 = set(article_ngrams(article_1))
    ngrams_2 = set(article_ngrams(article_2))

    common_ngrams = ngrams_1.intersection(ngrams_2)
    if len(common_ngrams) > NGRAM_AMOUNT_THRESHOLD:
        return True
    
    return False

def article_ngrams(article):
    n_grams = []
    for paragraph in article['body']:
        paragraph_ngrams = ngrams(paragraph['text'].split(), NGRAM_SIZE)
        n_grams.extend(paragraph_ngrams)

    return n_grams
