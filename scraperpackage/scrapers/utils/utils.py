from bson.objectid import ObjectId
from datetime import datetime

def generate_id():
    return str(ObjectId())

def create_article(
    *,
    url,
    primary_category,
    sub_categories = [],
    title,
    lead,
    author = None,
    date_published,
    date_updated = None,
    language,
    outlet,
    image = None,
    body,
):
    return {
        "_id": generate_id(), # Generate custom ID because the backend uses strings instead of ObjectId()s
        "url": url,
        "primaryCategory": primary_category,
        "subCategories": sub_categories,
        "title": title,
        "lead": lead,
        "author": author,
        "datePublished": date_published,
        "dateScraped": datetime.now(),
        "dateUpdated": date_updated,
        "language": language,
        "outlet": outlet,
        "image": image,
        "body": body,
    }
