from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String, TIMESTAMP, types
from sqlalchemy.orm import relationship, column_property

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    password = Column(String)

    # These are links to the other tables so this table can fetch data from the other tables and thos tables
    # can fetch data from this table. it does this via the foreign key join
    social_accounts = relationship("SocialAccount", back_populates="owner", cascade="all, delete",
                                   passive_deletes=True)  # so oncascade it should delete the data in other tables that are linked to it
    group_categories = relationship("GroupCategory", back_populates="owner_of_group_category", cascade="all, delete",
                                    passive_deletes=True)
    scopes = relationship("Scope", back_populates="creator", cascade="all, delete", passive_deletes=True)
    posts = relationship("Post", back_populates="post_user", cascade="all, delete", passive_deletes=True)


class SocialAccount(Base):
    __tablename__ = "social_accounts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    oauth_token = Column(String, index=True)
    oauth_token_secret = Column(String, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))

    owner = relationship("User", back_populates="social_accounts")


class GroupCategory(Base):
    __tablename__ = "group_categories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"))
    group_category_name = Column(String, index=True)

    owner_of_group_category = relationship("User", back_populates="group_categories")
    categories = relationship("Category", back_populates="group_category")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    group_category_id = Column(Integer, ForeignKey('group_categories.id'))
    category_name = Column(String, index=True)

    group_category = relationship("GroupCategory", back_populates="categories")
    keywords = relationship("Keyword", back_populates="category")


class Keyword(Base):
    __tablename__ = "keywords"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey('categories.id'))
    keywords = Column(String, index=True)

    category = relationship("Category", back_populates="keywords")


class LowerCaseText(types.TypeDecorator):
    """ Converts strings to lower case on the way in. """
    """ NOT IN USE """

    impl = types.Text

    def process_bind_param(self, value, dialect):
        return value.lower()


class Country(Base):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True, index=True)
    country_name = Column(LowerCaseText, index=True)
    country_initials = Column(Integer, index=True)


class State(Base):
    __tablename__ = "states"

    id = Column(Integer, primary_key=True, index=True)
    state_name = Column(LowerCaseText, index=True)
    country_id = Column(Integer, index=True)


class City(Base):
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, index=True)
    city_name = Column(LowerCaseText, index=True)
    state_id = Column(Integer, index=True)


class Scope(Base):
    __tablename__ = "scopes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    scope = Column(String, index=True)

    creator = relationship("User", back_populates="scopes")


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    source_name = Column(String, index=True)
    data_id = Column(String, index=True)
    data_author_id = Column(String, index=True)
    data_user_name = Column(String, index=True)
    data_user_location = Column(String, index=True)
    text = Column(String, index=True)
    full_object = Column(String, index=True)
    country_name = Column(String, index=True)
    state_name = Column(String, index=True)
    city_name = Column(String, index=True)
    created_at = Column(TIMESTAMP, index=True)
    link = column_property('https://www.' + source_name + '.com/' + data_user_name + '/status/' + data_id)

    post_user = relationship("User", back_populates="posts")
    sentiment_scores = relationship("PostSentimentScore", back_populates="sentiment_post")
    post_about_category = relationship("PostAboutCategory", back_populates="posts")


class PostSentimentScore(Base):
    __tablename__ = "post_sentiment_scores"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey('posts.id'))
    sentiment = Column(String, index=True)
    score = Column(Float, index=True)

    sentiment_post = relationship("Post", back_populates="sentiment_scores")


class PostAboutCategory(Base):
    __tablename__ = "post_is_about_category"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey('posts.id'))
    category_id = Column(Integer, ForeignKey('categories.id'))

    # category = relationship("Category", back_populates="post_is_about_category")
    posts = relationship("Post", back_populates="post_about_category")


class PostDataCategorisedView(Base):
    __tablename__ = "post_data_categorised_view"

    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    post_id = Column(Integer, ForeignKey('posts.id'))
    category_id = Column(Integer, ForeignKey('categories.id'))
    keywords = Column(String, index=True)
    text = Column(String, index=True)
    post_source = Column(String, index=True)
    region = Column(String, index=True)
    sentiment_score_value = Column(Float, index=True)
    sentiment_score = Column(String, index=True)
    created_at = Column(TIMESTAMP, index=True)

# class Tweet(Base):
#     # __tablename__ = "post_is_about_category"
#
#     id = Column(Integer, primary_key=True, index=True)
#     post_id = Column(Integer, ForeignKey('posts.id'))
#     category_id = Column(Integer, ForeignKey('categories.id'))
