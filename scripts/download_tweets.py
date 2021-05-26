import twint
import fire
import re
import csv
from tqdm import tqdm
import logging
from datetime import datetime
from time import sleep
import os

logger = logging.getLogger()
logger.disabled = True


def is_reply(tweet):
    """Determines if the tweet is a reply to another tweet
    """
    # If not a reply to another user, there will only be 1 entry
    if len(tweet.reply_to) == 1:
        return False

    # Check if any other users "replied" are in the tweet text
    users = tweet.reply_to[1:]
    conversations = [user['username'] in tweet.tweet for user in users]

    # If usernames are not present in text, it is a reply
    if sum(conversations) < len(users):
        return True

    return False


class TweetDownloader:
    def __init__(self,
                 username=None,
                 limit=None,
                 include_replies=False,
                 strip_usertags=False,
                 strip_hashtags=False):
        """Download public Tweets from a given Twitter account
        into a format suitable for training with AI text generation tools.

        Args:
            username: Twitter @ username to gather tweets. Defaults to None.
            limit: @ of tweets to gether; None for all tweets. Defaults to None.
            include_replies: Whether to include replies to other tweets. Defaults to False.
            strip_usertags: Whether to remove user tags from the tweets. Defaults to False.
            strip_hashtags: Whether to remove hastags from the tweets. Defaults to False.
        """
        self.username = username
        self.limit = limit
        self.include_replies = include_replies
        self.strip_usertags = strip_usertags
        self.strip_hashtags = strip_hashtags

        self.tweet_data = list()
        self.num_retries = 4

        if self.limit:
            assert self.limit % 20 == 0, 'Limit must be a multiple of 20.'
        else:
            self._estimate_user_tweets()

        print(f'Retrieving tweets for @{username}.')

    def _estimate_user_tweets(self):
        """Estimate total number of tweets from profile
        """
        c_lookup = twint.Config()
        c_lookup.Username = self.username
        c_lookup.Store_object = True
        c_lookup.Hide_output = True

        twint.run.Lookup(c_lookup)
        assert twint.output.users_list, f'Tweeter user @{self.username} not found.'
        self.limit = twint.output.users_list[0].tweets

    def _regex_filter_init(self):
        self.pattern = r'http\S+|pic\.\S+|\xa0|…'
        if self.strip_usertags:
            self.pattern += r'|@[a-zA-Z0-9_]+'
        if self.strip_hashtags:
            self.pattern += r'|#[a-zA-Z0-9_]+'

    def _extract_tweets(self):
        c = twint.Config()
        c.Store_object = True
        # c.Hide_output = True
        c.Username = self.username
        c.Limit = 20
        # c.Resume = ".temp"

        c.Store_object_tweets_list = self.tweet_data
        
        twint.run.Search(c)
        print('self.tweet_data: ', self.tweet_data)

    def _preprocess_tweets(self):
        if not self.include_replies:
            tweets = [re.sub(self.pattern, '', tweet.tweet).strip()
                    for tweet in self.tweet_data
                    if not is_reply(tweet)]

            # On older tweets, if the cleaned tweet starts with an "@", it is a de-facto reply
            tweets = filter(lambda x: not x.startswith('@'), tweets)
        else:
            tweets = [re.sub(self.pattern, '', tweet.tweet).strip()
                    for tweet in self.tweet_data]

        return tweets

    def retrieve_tweets(self):
        with open(f'data/{self.username}_tweets.csv', 'w', encoding='utf-8', newline='') as f:
            w = csv.writer(f)
            w.writerow(['tweets'])  # CSV Header

            pbar = tqdm(range(self.limit), desc='Oldest Tweet')
            for i in range((self.limit // 20) - 1):
                # Twint may fail; give it up to `self.num_retries` tries to return tweets
                for _ in range(0, self.num_retries):
                    if len(self.tweet_data) == 0:
                        self._extract_tweets()

                #         # If it fails, sleep before retry
                #         if len(self.tweet_data) == 0:
                #             sleep(1.0)
                #     else:
                #         continue

                # # Return if all fails
                # if len(self.tweet_data) == 0:
                #     break

                # # Preprocess and write tweets
                # tweets = self._preprocess_tweets()
                # for tweet in tweets:
                #     if tweet != '':
                #         w.writerow([tweet])

                # if i > 0:
                #     pbar.update(20)
                # else:
                #     pbar.update(40)

                # if self.tweet_data:
                #     oldest_tweet = (datetime
                #                     .utcfromtimestamp(self.tweet_data[-1].datetime / 1000.0)
                #                     .strftime('%Y-%m-%d %H:%M:%S'))
                #     pbar.set_description(f'Oldest Tweet: {oldest_tweet}')






def download_tweets(username=None,
                    limit=None,
                    include_replies=False,
                    strip_usertags=False,
                    strip_hashtags=False):
    """Download public Tweets from a given Twitter account
    into a format suitable for training with AI text generation tools.

    Args:
        username: Twitter @ username to gather tweets. Defaults to None.
        limit: @ of tweets to gether; None for all tweets. Defaults to None.
        include_replies: Whether to include replies to other tweets. Defaults to False.
        strip_usertags: Whether to remove user tags from the tweets. Defaults to False.
        strip_hashtags: Whether to remove hastags from the tweets. Defaults to False.
    """
    tweet_downloader = TweetDownloader(username, limit, include_replies,
                                       strip_usertags, strip_hashtags)
    tweet_downloader.retrieve_tweets()


    # if limit:
    #     assert limit % 20 == 0, '`limit` must be a multiple of 20.'
    # else:
    #     # Estimate total number of tweets from profile
    #     c_lookup = twint.Config()
    #     c_lookup.Username = username
    #     c_lookup.Store_object = True
    #     c_lookup.Hide_output = True

    #     twint.run.Lookup(c_lookup)
    #     limit = twint.output.users_list[0].tweets

    # pattern = r'http\S+|pic\.\S+|\xa0|…'
    # if strip_usertags:
    #     pattern += r'|@[a-zA-Z0-9_]+'
    # if strip_hashtags:
    #     pattern += r'|#[a-zA-Z0-9_]+'

    # # Create an empty file to store pagination id
    # with open('.temp', 'w', encoding='utf-8') as f:
    #     f.write(str(-1))
    
    # print(f'Retrieving tweets for @{username}...')

    # with open(f'data/{username}_tweets.csv', 'w', encoding='utf-8', newline='') as f:
    #     w = csv.writer(f)
    #     w.writerow(['tweets'])  # CSV Header

    #     pbar = tqdm(range(limit), desc='Oldest Tweet')
    #     for i in range((limit // 20) - 1):
    #         tweet_data = list()
    #         # twint may fail; give it up to 5 tries to return tweets
    #         for _ in range(0, 4):
    #             if len(tweet_data) == 0:
    #                 c = twint.Config()
    #                 c.Store_object = True
    #                 c.Hide_output = True
    #                 c.Username = username
    #                 c.Limit = 20
    #                 c.Resume = ".temp"

    #                 c.Store_object_tweets_list = tweet_data

    #                 twint.run.Search(c)

    #                 # If it fails, sleep before retry
    #                 if len(tweet_data) == 0:
    #                     sleep(1.0)
    #             else:
    #                 continue
        
    #         # Return if all fails
    #         if len(tweet_data) == 0:
    #             break

    #         if not include_replies:
    #             tweets = [re.sub(pattern, '', tweet.tweet).strip()
    #                     for tweet in tweet_data
    #                     if not is_reply(tweet)]
                
    #             # On older tweets, if the cleaned tweet starts with an "@", it is a de-facto reply
    #             for tweet in tweets:
    #                 if tweet != '' and not tweet.startswith('@'):
    #                     w.writerow([tweet])

    #         else:
    #             tweets = [re.sub(pattern, '', tweet.tweet).strip()
    #                     for tweet in tweet_data]
                
    #             for tweet in tweets:
    #                 if tweet != '':
    #                     w.writerow([tweet])

    #         if i > 0:
    #             pbar.update(20)
    #         else:
    #             pbar.update(40)

    #         if tweet_data:
    #             oldest_tweet = (datetime
    #                             .utcfromtimestamp(tweet_data[-1].datetime / 1000.0)
    #                             .strftime('%Y-%m-%d %H:%M:%S'))
    #             pbar.set_description(f'Oldest Tweet: {oldest_tweet}')


if __name__ == '__main__':
    fire.Fire(download_tweets)
