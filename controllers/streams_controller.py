# System Imports
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi_sqlalchemy import db

# Test for stream
import requests
import json
import base64
# Test for stream end

import socket
# from pythonping import ping

# Import os and dotenv to read data from env file
import os
from dotenv import load_dotenv

# custom
from core.models import schema

# from controllers.crud import get_current_user
from queue import Queue
import threading
from dependency.vader_sentiment_api import SentimentApi

import time
from controllers.rules_controller import Rules

load_dotenv()


# MyTwitter is inheriting from the parent class 'Rules' found in rules controller
class MyTwitter(Rules):

    def __init__(self) -> None:
        super().__init__()
        self.request_wait_time = 180
        try:
            with db():
                self.keywords = db.session.query(schema.Keyword, schema.Category, schema.GroupCategory) \
                    .join(schema.Category, schema.Keyword.category_id == schema.Category.id) \
                    .join(schema.GroupCategory, schema.GroupCategory.id == schema.Category.group_category_id).all()
                print(self.keywords[0].GroupCategory)
                # exit()
        except Exception as e:
            # print("NOT saved")
            print(e)

        # Start queues for streams and sentiment scores
        self.stream_queue = Queue()
        self.sentiment_queue = Queue()
        self.categorize_post_queue = Queue()

        # Threads so functions can be running in background asynchronously
        threading.Thread(target=self.store_streams, daemon=True).start()
        threading.Thread(target=self.score_sentiment, daemon=True).start()
        threading.Thread(target=self.check_post_is_about_category, daemon=True).start()
        # threading.Thread(target=self.ping_backend, daemon=True).start()

        # create headers
        headers = self.create_headers(os.getenv('TWITTER_BEARER_TOKEN'))
        # get rules
        # rules = self.get_rules(headers)
        # delete rules
        # self.delete_all_rules(headers, rules)
        # set rules is being called from the rules controller
        self.set_rules()
        # start stream
        self.get_stream(headers)

    def ping_backend(self):
        be_url = "https://dwm-social-media-backend.herokuapp.com"
        time_count = 60 * 25
        try:
            while True:
                # ping(be_url, verbose=True, timeout=2000)
                print("pinging BE")
                requests.get(be_url)
                time.sleep(time_count)
        except socket.error as e:
            print("Ping Error:", e)

    def check_post_is_about_category(self):
        while True:
            post_to_categorize = self.categorize_post_queue.get()
            # print(f"Tagging {post_to_categorize.text}")

            for keyword_record in self.keywords:

                if keyword_record.GroupCategory.user_id == post_to_categorize.user_id:
                    keyword_list = keyword_record.Keyword.keywords.split(",")
                    # print(keyword_list)
                    for keyword in keyword_list:
                        keyword = str.encode(keyword.lower().strip())
                        # print(keyword, post_to_categorize.text.lower())  #
                        if keyword != b'' and keyword.lower().strip() in post_to_categorize.text.lower():
                            db_categorization = schema.PostAboutCategory(
                                post_id=post_to_categorize.id,
                                category_id=keyword_record.Keyword.category_id
                            )
                            # print('categorized', keyword, post_to_categorize.id)
                            try:
                                with db():
                                    db.session.add(db_categorization)
                                    db.session.commit()
                                    db.session.refresh(db_categorization)
                            except Exception as e:
                                print("Could not categorize post")
                                print(e)
                            break
            # print(f"Finished attempt to categorize {post_to_categorize.text}")

    # Code for generating bearer token
    @staticmethod
    def generate_bearer_token():
        bearer_token = base64.b64encode(
            f"{os.getenv('TWITTER_CLIENT_ID')}:{os.getenv('TWITTER_CLIENT_SECRET')}".encode())
        headers = {
            "Authorization": f"Basic {bearer_token.decode()}",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        }
        resp = requests.post(
            url="https://api.twitter.com/oauth2/token",
            data={"grant_type": "client_credentials"},
            headers=headers,
        )
        data = resp.json()

        return data

    # Start getting tweets that contain the rules specified
    def get_stream(self, headers):  # , token:str set, bearer_token,
        print("getting streams method")
        count = 1
        while True:
            base_url = "https://api.twitter.com/2/tweets/search/stream?"
            # tweet_fields = "tweet.fields=author_id,created_at,entities,id,lang,possibly_sensitive,public_metrics,referenced_tweets,reply_settings,source,text,withheld"
            tweet_fields = "tweet.fields=created_at,id,lang,source"
            # place_fields = "&place.fields=contained_within,country,country_code,full_name,geo,id,name,place_type"
            expansions = "&expansions=author_id"
            user_fields = "&user.fields=name,username,location"

            # "tweet.fields=created_at & expansions = author_id & user.fields = created_at"

            url = base_url + tweet_fields + user_fields + expansions  # + place_fields
            # print(url)

            response = requests.get(url, headers=headers, stream=True)
            print(response)
            try:
                for response_line in response.iter_lines():
                    if response_line:
                        json_response = json.loads(response_line)
                        # print(json_response)
                        self.stream_queue.put(json_response)
                        count = 1
            except Exception as r:
                # if response.status_code == 429:
                print(' Put to sleep before retrying.')
                time_count = self.request_wait_time * count
                time.sleep(time_count)
                count += 1
                # print(r)
                print("Printed after " + str(time_count) + " seconds.")
                print(r)
                continue
                # else:
                #     print(' Put to sleep before retrying.')
                #     time.sleep(5)
                #     print("Printed after 5 seconds.")

    def score_sentiment(self):
        print("score sentiment method")
        while True:
            post_to_score = self.sentiment_queue.get()
            if post_to_score:
                # print(f"Scoring {post_to_score.id}")
                result = SentimentApi().getSentiment(str(post_to_score.text))

                db_sentiment = schema.PostSentimentScore(
                    post_id=post_to_score.id,
                    sentiment=result["sentiment"],
                    score=result["score"]
                )
                try:
                    with db():
                        db.session.add(db_sentiment)
                        db.session.commit()
                        db.session.refresh(db_sentiment)
                except Exception as e:
                    # print("NOT saved")
                    print(e)
                # print(f"Scored {post_to_score.id}")

    def store_streams(self):
        print("store streams method")
        while True:
            stream_results = self.stream_queue.get()
            if stream_results:
                user_location = ''
                if "location" in stream_results["includes"]["users"][0]:
                    user_location = stream_results["includes"]["users"][0]["location"]

                # Split user ids that are returned from twitter
                user_ids = stream_results['matching_rules'][0]["tag"].split(",")
                for user_id in user_ids:
                    db_stream = schema.Post(
                        user_id=user_id,
                        source_name="twitter",
                        data_id=stream_results["data"]["id"],
                        data_author_id=stream_results["data"]["author_id"],
                        data_user_name=stream_results["includes"]["users"][0]["username"],
                        data_user_location=user_location,
                        text=stream_results["data"]["text"],
                        full_object=json.dumps(stream_results, indent=4, sort_keys=True),
                        created_at=stream_results["data"]["created_at"]
                    )
                    try:
                        with db():
                            db.session.add(db_stream)
                            db.session.commit()
                            db.session.refresh(db_stream)

                            self.sentiment_queue.put(db_stream)
                            self.categorize_post_queue.put(db_stream)
                    except Exception as e:
                        # print("NOT saved")
                        print(e)
