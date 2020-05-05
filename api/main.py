from typing import List, Optional

from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, Header
from pydantic import BaseModel
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY
import databases
import sqlalchemy
from sqlalchemy.sql.expression import func

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
ACCOUNT = os.environ.get("ACCOUNT")


assert all([CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET, ACCOUNT]
           ), "Not all Twitter environment variables have been specified in .env file"

# Cloud SQL environment variables
DB_USERNAME = os.environ.get("DB_USERNAME")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_NAME = os.environ.get("DB_NAME")
CONNECTION_NAME = os.environ.get("CONNECTION_NAME")

# Optional: Secret header token
SECRET_TOKEN = os.environ.get("SECRET_TOKEN")


## Initialize Database ##
## Run locally
# DATABASE_URL = "sqlite:///./tweets.db"

## Connecting to docker postgres server with docker compose
# DATABASE_URL = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@postgresserver/{DB_NAME}"

## Connecting with Cloud SQL Postgres server
DATABASE_URL = sqlalchemy.engine.url.URL(
  drivername='postgres+pg8000',
  username=DB_USERNAME,
  password=DB_PASSWORD,
  database=DB_NAME,
  query={
    'unix_sock': '/cloudsql/{}/.s.PGSQL.5432'.format(CONNECTION_NAME)
  }
)


metadata = sqlalchemy.MetaData()
tweets = sqlalchemy.Table(
  "tweets",
  metadata,
  sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
  sqlalchemy.Column("tweet", sqlalchemy.String),
  sqlalchemy.Column("account", sqlalchemy.String),
  sqlalchemy.Column("tweet_timestamp", sqlalchemy.DateTime),
  sqlalchemy.Column("tweet_url", sqlalchemy.String)
)
engine = sqlalchemy.create_engine(DATABASE_URL)
metadata.create_all(engine)

app = FastAPI()


class TweetBase(BaseModel):
  tweet: str

class TweetIn(TweetBase):
  pass

class TweetOut(TweetBase):
  id: int
  account: str
  tweet_timestamp: Optional[datetime] = None
  tweet_url: Optional[str] = None


async def verify_token(x_token: str = Header(...)):
  if SECRET_TOKEN and SECRET_TOKEN != x_token:
    raise HTTPException(status_code=400, detail="Invalid X-Token header")


@app.get("/tweets/", response_model=List[TweetOut], dependencies=[Depends(verify_token)])
async def get_tweets():
  with engine.connect() as connection:
    query = tweets.select()
    all_tweets = connection.execute(query).fetchall()
  return all_tweets


@app.post("/tweet_currated/", dependencies=[Depends(verify_token)])
async def tweet_currated():
  query = (tweets.select()
                 .where(tweets.columns.tweet_timestamp == None)
                 .where(tweets.columns.account == ACCOUNT)
                 .order_by(func.random())
                 .limit(1))
  with engine.connect() as connection:
    tweet = connection.execute(query).fetchone()

  if tweet is None:
    raise HTTPException(
      status_code=404,
      detail="No more tweets left",
      headers={"X-Error": "Error away"}
    )

  auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
  auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)

  api = tweepy.API(auth)
  t = api.update_status(tweet.tweet)

  tweet_timestamp = datetime.now()
  tweet_url = f"https://twitter.com/{t.user.screen_name}/status/{t.id_str}"

  query = (tweets.update()
                 .where(tweets.columns.id == tweet.id)
                 .values(tweet_timestamp=tweet_timestamp))
  with engine.connect() as connection:
    connection.execute(query)

  return {"response": f"New tweet posted @ {tweet_url}"}


@app.post("/add_tweets/", response_model=TweetOut, dependencies=[Depends(verify_token)])
async def add_tweets(tweet: TweetIn):
  with engine.connect() as connection:
    query = tweets.insert().values(tweet=tweet.tweet,
                                   account=ACCOUNT)
    record = connection.execute(query)
  return {**tweet.dict(), "account": ACCOUNT, "id": record.lastrowid}


@app.post("/add_tweets_file", dependencies=[Depends(verify_token)])
async def add_tweets_file(file: UploadFile = File(...)):
  bytes = await file.read()
  contents = bytes.decode("utf-8").split("\r\n====================\r\n")[:-1]

  # query = "INSERT INTO tweets(tweet, account) VALUES (:tweet, :account)"
  # values = [{"tweet": tweet, "account": ACCOUNT} for tweet in contents]
  # await database.execute_many(query=query, values=values)

  with engine.connect() as connection:
    for tweet in contents:
      query = tweets.insert().values(tweet=tweet, account=ACCOUNT)
      connection.execute(query)

  return {"filename": file.filename}

