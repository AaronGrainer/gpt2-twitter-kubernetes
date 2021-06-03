from typing import List, Optional

from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, Header
from pydantic import BaseModel
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from src.utils.database import get_tweet, insert_tweets
from src.scripts.post_tweets import PostTweets

import os
import time
from datetime import datetime
from dotenv import load_dotenv
import tweepy


load_dotenv()

# Twitter environment variables
CONSUMER_KEY = os.environ.get("CONSUMER_KEY")
CONSUMER_SECRET = os.environ.get('CONSUMER_SECRET')
ACCESS_KEY = os.environ.get("ACCESS_KEY")
ACCESS_SECRET = os.environ.get("ACCESS_SECRET")


assert all([CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET]
           ), "Not all Twitter environment variables have been specified in .env file"

# Optional: Secret header token
SECRET_TOKEN = os.environ.get("SECRET_TOKEN")


app = FastAPI()


class TweetBase(BaseModel):
  	tweet: str

class TweetIn(TweetBase):
  	pass

class TweetOut(BaseModel):
	text: str
	tweet_timestamp: Optional[datetime] = None
	tweet_url: Optional[str] = None


async def verify_token(x_token: str = Header(...)):
	if SECRET_TOKEN and SECRET_TOKEN != x_token:
		raise HTTPException(status_code=400, detail="Invalid X-Token header")


@app.post('/post_tweet/', response_model=TweetOut, dependencies=[Depends(verify_token)])
async def post_tweet():
    post_tweets = PostTweets()
    tweet = post_tweets.post()

    return tweet


@app.post("/add_tweets/", dependencies=[Depends(verify_token)])
async def add_tweets(tweet: TweetIn):
    insert_tweets(tweet.tweet)

    return {**tweet.dict()}


@app.post("/add_tweets_file", dependencies=[Depends(verify_token)])
async def add_tweets_file(file: UploadFile = File(...)):
    bytes = await file.read()

    tweets = [tweet.strip() for tweet in bytes.decode("utf-8").split('###############')]
    insert_tweets(tweets)

    return {"filename": file.filename}

