import os
from dotenv import load_dotenv
import tweepy

class TwitterHandler:
    def __init__(self) -> None:
        self.access_token = os.getenv("ACCESS_TOKEN")
        self.access_secret = os.getenv("ACCESS_SECRET")
        self.consumer_key= os.getenv("CONSUMER_KEY")
        self.consumer_secret = os.getenv("CONSUMER_SECRET")
        self.bearer_token = os.getenv("BEARER_TOKEN")
        self.auth = tweepy.OAuth1UserHandler(self.consumer_key, self.consumer_secret, self.access_token, self.access_secret)
        self.api = tweepy.API(self.auth, wait_on_rate_limit=True)
        self.client = tweepy.Client(self.bearer_token, self.consumer_key, self.consumer_secret, self.access_token, self.access_secret)

    def get_media(self, tweet_entities):
        media = []
        media_type = ""
        for item in tweet_entities:
            media_type = item['type']
            if media_type == "photo":
                media.append(item["media_url_https"])
            elif media_type == "video" or media_type == "animated_gif":
                found = False
                video_info = item["video_info"]
                variants = video_info['variants']
                for variant in variants:
                    content_type = variant["content_type"]
                    if "video/mp4" in content_type and not found:
                        video_url = variant["url"]
                        media.append(video_url)
                        found = True
        return media, media_type
        
    
    #Just return the list of tweets to process elsewhere.
    def get_newest_tweet(self, user_id, since_id=None, count=10):
        tweets = self.api.user_timeline(user_id=user_id, count=count, since_id=since_id, tweet_mode="extended")
        for tweet in tweets:
            if tweet == None:
                return "-1"
        return tweets


    def get_user_id(self, screen_name):
        try:
            target_user = self.api.get_user(screen_name=screen_name)
            user_id = target_user.id
            return user_id
        except tweepy.NotFound:
            return -1
