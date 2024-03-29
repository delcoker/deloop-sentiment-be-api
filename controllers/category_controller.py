from sqlalchemy.orm import Session, joinedload, lazyload

from auth import auth
from core.models import schema


# Get all Categories
def get_all_categories(db: Session, token: str):
    user = auth.get_user_from_token(db, token)
    # Limit and offset works like pagination
    return db.query(schema.Category) \
        .join(schema.GroupCategory) \
        .filter(schema.GroupCategory.user_id == user.id) \
        .all()


# Get all Group Categories
def create_category(db: Session, category_name: str, group_category_id: int, keywords: str):
    db_category = schema.Category(
        group_category_id=group_category_id,
        category_name=category_name
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)

    # if keywords:
    db_keywords = schema.Keyword(
        category_id=db_category.id,
        keywords=keywords
    )
    db.add(db_keywords)
    db.commit()
    db.refresh(db_keywords)
    return db_category


# Get a specific Category
def get_category(db: Session, token: str, category_id: int):
    user = auth.get_user_from_token(db, token)
    return db.query(schema.Category) \
        .join(schema.GroupCategory) \
        .filter(schema.Category.id == category_id,
                schema.GroupCategory.user_id == user.id) \
        .first()


# Update a particular category
def update_category(db: Session, category_id: str, category_name: str, group_category_id: int, keywords: str):
    keyword_list = keywords.split(',')
    new_keyword_list = []
    for keyword in keyword_list:
        keywrd = keyword.lower().strip()
        if len(keywrd) > 2:
            new_keyword_list.append(keywrd)

    keywords = ",".join(new_keyword_list)

    result = db.query(schema.Category) \
        .filter(schema.Category.id == category_id) \
        .update({"group_category_id": group_category_id,
                 "category_name": category_name})
    db.commit()
    if keywords:
        db.query(schema.Keyword) \
            .filter(schema.Keyword.category_id == category_id) \
            .update({"keywords": keywords})
    db.commit()
    return result


# Delete a particular category
def delete_category(db: Session, category_id: int):
    result = db.query(schema.Category) \
        .filter(schema.Category.id == category_id) \
        .delete()
    db.commit()
    return result


# get posts regarding the specified category
def get_category_posts(category_id: int, db: Session):
    # why doesn't this work
    # sth = db.query(schema.Post) \
    #     .options(joinedload(schema.Post.post_about_category)) \
    #     .options(joinedload(schema.Post.sentiment_scores)) \
    #     .filter(schema.PostSentimentScore.sentiment != "NEUTRAL") \
    #     .order_by(schema.Post.created_at.desc()) \
    #     .limit(50) \
    #     .all()

    # # returns one value
    # sth = db.query(schema.Post) \
    #     .join(schema.PostAboutCategory) \
    #     .filter(schema.PostAboutCategory.category_id == category_id) \
    #     .options(joinedload(schema.Post.sentiment_scores)) \
    #     .filter(schema.PostSentimentScore.sentiment != "NEUTRAL") \
    #     .order_by(schema.Post.created_at.desc()) \
    #     .limit(50) \
    #     .all()

    # sth = db.query(schema.Post) \
    #     .join(schema.PostAboutCategory) \
    #     .filter(schema.PostAboutCategory.category_id == category_id) \
    #     .options(joinedload(schema.Post.sentiment_scores)) \
    #     .order_by(schema.Post.created_at.desc()) \
    #     .limit(50) \
    #     .all()
    #
    # for post in sth:
    #     post.sentiment = post.sentiment_scores[0].sentiment

    # col_concat = functions.concat("https://www.twitter.com/", # schema.Post.data_user_name).label("link")
    # col_concat = func.concat("https://www.twitter.com/", schema.Post.data_user_name)
    sth = db.query(schema.Post.id,
                   schema.Post.data_user_name,
                   schema.Post.source_name,
                   schema.Post.state_name,
                   schema.Post.data_author_id,
                   schema.Post.data_user_location,
                   schema.Post.country_name,
                   schema.Post.text,
                   schema.Post.city_name,
                   schema.Post.created_at,
                   schema.Post.link,
                   schema.PostAboutCategory.category_id,
                   schema.PostSentimentScore.sentiment) \
        .join(schema.PostAboutCategory) \
        .filter(schema.PostAboutCategory.category_id == category_id) \
        .join(schema.PostSentimentScore) \
        .filter(schema.PostSentimentScore.sentiment != "NEUTRAL") \
        .order_by(schema.Post.created_at.desc()) \
        .limit(50) \
        .all()
    # print(sth)
    return sth
