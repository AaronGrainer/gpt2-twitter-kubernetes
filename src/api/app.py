from typing import Optional

from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, Header
from pydantic import BaseModel

from src.utils.database import insert_tweets
from src.scripts.post_tweets import PostTweets

import os
from datetime import datetime
from dotenv import load_dotenv


load_dotenv()


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

