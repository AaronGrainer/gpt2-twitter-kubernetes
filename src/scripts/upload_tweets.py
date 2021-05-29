from src.config import global_config as gc

from src.utils.database import insert_tweets

import os


if __name__ == '__main__':
    username = 'karpathy'
    tweet_filename = os.path.join(gc.tweet_predicted_path, f'{username}_predicted_tweets.txt')

    with open(tweet_filename, 'r', encoding="utf-8") as f:
        texts = f.read()

        tweets = [tweet.strip() for tweet in texts.split('###############')]
        insert_tweets(tweets)
