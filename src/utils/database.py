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
            'tweeted': False
        })
    twitter_client['tweets'].insert_many(tweet_doc)


def get_new_tweet():
    tweet = twitter_client['tweets'].find_one({
        'tweeted': False
    })
    if tweet:
        twitter_client['tweets'].update_one({
            '_id': tweet['_id']
        }, {
            'tweeted': True
        })
        
    return tweet

