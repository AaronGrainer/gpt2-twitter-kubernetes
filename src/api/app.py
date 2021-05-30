from typing import List, Optional

from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, Header
from pydantic import BaseModel
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from src.utils.database import get_tweet

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

class TweetOut(TweetBase):
	text: str
	tweet_timestamp: Optional[datetime] = None
	tweet_url: Optional[str] = None


async def verify_token(x_token: str = Header(...)):
	if SECRET_TOKEN and SECRET_TOKEN != x_token:
		raise HTTPException(status_code=400, detail="Invalid X-Token header")


@app.get("/tweet/", response_model=TweetOut, dependencies=[Depends(verify_token)])
async def get_tweets():
	return get_tweet()


# @app.post("/tweet_currated/", dependencies=[Depends(verify_token)])
# async def tweet_currated():
# 	query = (tweets.select()
# 					.where(tweets.columns.tweet_timestamp == None)
# 					.where(tweets.columns.account == ACCOUNT)
# 					.order_by(func.random())
# 					.limit(1))
# 	with engine.connect() as connection:
# 		tweet = connection.execute(query).fetchone()

# 	if tweet is None:
# 		raise HTTPException(
# 			status_code=404,
# 			detail="No more tweets left",
# 			headers={"X-Error": "Error away"}
# 		)

# 	auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
# 	auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)

# 	api = tweepy.API(auth)
# 	t = api.update_status(tweet.tweet)

# 	tweet_timestamp = datetime.now()
# 	tweet_url = f"https://twitter.com/{t.user.screen_name}/status/{t.id_str}"

# 	query = (tweets.update()
# 					.where(tweets.columns.id == tweet.id)
# 					.values(tweet_timestamp=tweet_timestamp))
# 	with engine.connect() as connection:
# 		connection.execute(query)

# 	return {"response": f"New tweet posted @ {tweet_url}"}


# @app.post("/add_tweets/", response_model=TweetOut, dependencies=[Depends(verify_token)])
# async def add_tweets(tweet: TweetIn):
# 	with engine.connect() as connection:
# 		query = tweets.insert().values(tweet=tweet.tweet,
# 									account=ACCOUNT)
# 		record = connection.execute(query)
# 	return {**tweet.dict(), "account": ACCOUNT, "id": record.lastrowid}


# @app.post("/add_tweets_file", dependencies=[Depends(verify_token)])
# async def add_tweets_file(file: UploadFile = File(...)):
# 	bytes = await file.read()
# 	contents = bytes.decode("utf-8").split("\r\n====================\r\n")[:-1]

# 	# query = "INSERT INTO tweets(tweet, account) VALUES (:tweet, :account)"
# 	# values = [{"tweet": tweet, "account": ACCOUNT} for tweet in contents]
# 	# await database.execute_many(query=query, values=values)

# 	with engine.connect() as connection:
# 		for tweet in contents:
# 			query = tweets.insert().values(tweet=tweet, account=ACCOUNT)
# 			connection.execute(query)

# 	return {"filename": file.filename}

