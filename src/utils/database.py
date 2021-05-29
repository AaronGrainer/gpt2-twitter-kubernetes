import pymongo
from datetime import datetime


client = pymongo.MongoClient('localhost', 27017)
twitter_client = client['twitter']


def insert_tweets(tweets):
    tweet_doc = list()
    for tweet in tweets:
        tweet_doc.append({
            'createdAt': datetime.now(),
            'updatedAt': datetime.now(),
            'text': tweet,
            'tweet_timestamp': None,
            'tweet_url': None
        })
    twitter_client['tweets'].insert_many(tweet_doc)


def get_tweet():
    tweet = twitter_client['tweets'].find_one({
        'tweet_timestamp': None
    })        
    return tweet


def update_tweet(tweet, tweet_url):
    twitter_client['tweets'].update_one({
        '_id': tweet['_id']
    }, {
        '$set': {
            'tweet_timestamp': datetime.now(),
            'tweet_url': tweet_url
        }
    })

