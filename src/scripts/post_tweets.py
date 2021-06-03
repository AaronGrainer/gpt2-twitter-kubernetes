from src.utils.database import get_tweet, update_tweet

import os
from dotenv import load_dotenv
import tweepy
import logging


logging.basicConfig(level = logging.INFO)
logger = logging.getLogger()


load_dotenv()


class PostTweets:
    def __init__(self):
        consumer_key = os.environ.get("CONSUMER_KEY")
        consumer_secret = os.environ.get('CONSUMER_SECRET')
        access_key = os.environ.get("ACCESS_KEY")
        access_secret = os.environ.get("ACCESS_SECRET")

        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_key, access_secret)

        self.api = tweepy.API(auth)

    def post(self):
        tweet = get_tweet()
        if tweet:
            t = self.api.update_status(tweet['text'])
            tweet_url = f'https://twitter.com/{t.user.screen_name}/status/{t.id_str}'
            
            tweet = update_tweet(tweet, tweet_url)

            logger.info(f'New tweet posted @ {tweet_url}')
        else:
            logger.info(f'No more tweets to post')

        return tweet


if __name__ == '__main__':
    post_tweets = PostTweets()
    post_tweets.post()

