import os
import fire
import csv
import tweepy
import re

import logging
from dotenv import load_dotenv

logging.basicConfig(level = logging.INFO)
logger = logging.getLogger()

load_dotenv()


class TweetDownloader:
    def __init__(self,
                 username=None,
                 exclude_replies=True,
                 strip_usertags=False,
                 strip_hashtags=False):
        """
        Download public Tweets from a given Twitter account
        into a format suitable for training with AI text generation tools.
        """
        self.username = username
        self.exclude_replies = exclude_replies
        self.strip_usertags = strip_usertags
        self.strip_hashtags = strip_hashtags

        consumer_key = os.environ.get("CONSUMER_KEY")
        consumer_secret = os.environ.get('CONSUMER_SECRET')
        access_key = os.environ.get("ACCESS_KEY")
        access_secret = os.environ.get("ACCESS_SECRET")

        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_key, access_secret)

        self.api = tweepy.API(auth)

        self.tweet_data = list()
        self.num_retries = 4

        self._regex_filter_init()

        logger.info(f'Retrieving tweets for @{username}.')

    def _regex_filter_init(self):
        self.pattern = r'http\S+|pic\.\S+|\xa0|…'
        if self.strip_usertags:
            self.pattern += r'|@[a-zA-Z0-9_]+'
        if self.strip_hashtags:
            self.pattern += r'|#[a-zA-Z0-9_]+'

    def _extract_tweets(self):
        oldest_id = None

        while True:
            tweets = self.api.user_timeline(self.username,
                                       count=200,
                                       include_rts=False,
                                       exclude_replies=self.exclude_replies,
                                       max_id=oldest_id,
                                       tweet_mode='extended')

            if len(tweets) == 0:
                break

            oldest_id = tweets[-1].id - 1
            self.tweet_data.extend(tweets)

            logger.info(f'{len(self.tweet_data)} of @{self.username} tweets downloaded.')

    def _preprocess_tweets(self):
        tweets = ['<|startoftext|> ' + re.sub(self.pattern, '', tweet.full_text).strip() + ' <|endoftext|>'
                  for tweet in self.tweet_data]
        return tweets

    def retrieve_tweets(self):
        self._extract_tweets()
        tweets = self._preprocess_tweets()

        with open(f'data/{self.username}_tweets.txt', 'w', encoding="utf-8") as f:
            f.write(' '.join(tweets))



def download_tweets(username=None,
                    exclude_replies=True,
                    strip_usertags=False,
                    strip_hashtags=False):
    """Download tweets from a specified user.

    Args:
        username: Twitter @ username to gather tweets. Defaults to None.
        limit: @ of tweets to gether; None for all tweets. Defaults to None.
        exclude_replies: Whether to include replies to other tweets. Defaults to False.
        strip_usertags: Whether to remove user tags from the tweets. Defaults to False.
        strip_hashtags: Whether to remove hastags from the tweets. Defaults to False.
    """
    tweet_downloader = TweetDownloader(username, exclude_replies,
                                       strip_usertags, strip_hashtags)
    tweet_downloader.retrieve_tweets()


if __name__ == '__main__':
    fire.Fire(download_tweets)


