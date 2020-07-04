# GPT-2 Twitter Cloud Run

<p align="center">
  <a href="https://github.com/aarongrainer/gpt2-twitter-cloud-run/blob/master/LICENSE">
    <img alt="GitHub" src="https://img.shields.io/github/license/aarongrainer/gpt2-twitter-cloud-run?color=blue">
  </a>
  <a>
    <img alt="Code Progress" src="https://img.shields.io/badge/Code-Completed-success">
  </a>
</p>

A FastAPI app designed to run a [GPT-2](https://openai.com/blog/better-language-models/) powered twitter bot on a schedule using Google Cloud Run, Cloud Scheduler and Cloud SQL. 

* The newest state-of-the-art GPT-2 language model from OpenAI is trained and fine-tuned on user tweets. 

* Due to the current unpredictibility of AI-generated language models, AI tweets are batch generated and human currated. 

* A centralized Postgres server in a Cloud SQL database is used to house the currated tweets.

* FastAPI endpoints are used to populate the database with new generated tweets as well as tweet out with a user account using Tweepy.

## Installation

```shell
git clone git@github.com:AaronGrainer/gpt2-twitter-cloud-run.git

conda create -n [ENV_NAME] python=3.7

conda activate [ENV_NAME]

pip install -r requirements.txt
```

## Downloading User Tweets

Twitter's API currently limits the users to retrieving only the latest 3,200 tweets from a given user, which is not nearly enough input data for training. Therefore, the python package [twint](https://github.com/twintproject/twint) is used to bypass the API limitation.

To download a list of tweets from any given user, call `download_tweets.py`, For example:

```shell
python download_tweets.py --username=karpathy --limit=6000
```

## Training GPT-2 on User Tweets

Given the downloaded user tweets, the python package [gpt_2_simple](https://github.com/minimaxir/gpt-2-simple) is used to easily train a GPT-2 model to generate tweets based on the tweeting pattern of the user. Train the model on the downloaded tweets by calling `models.py`, the provided filename should match the tweets file downloaded. For example:

```shell
python -m ml.model --filename=karpathy_tweets.csv --run_name=karpathy_production --steps=2000
```

This will train the GPT-2 model and generate an output tweet file that looks like this:

```text
My poor brain. I'm so tempted to plug this in and see if I can't decipher it as a self-supervised basic arithmetic problem. But no, I can't. It's too painful. Too much loss. Something must give. Please, gods above, let this be true.
====================
The 2D appearance of an image can be deceivingly complex. My head may be incomplete, but I assure you it's not incomplete.
====================
While coding, almost everything I write is saved. I don't want this.
====================
Spending extra time tuning my baselines, thinking about how much incentive I have not to, & how this is the reason we can't have nice things
====================
SpaceX Falcon 9 launch in ~20 minutes! + Another attempt at first stage recovery coming   #soexcite
====================
```

You are now able to currate the tweets above, removing an non-funny tweets perhaps? But please do keep the general format intact.

## Environment Variables

1. Create a new .env file using the .env_reference file as reference. Populate the .env file with the desired app settings. This file serves to provide all the environment variables necessary for deploying the app. 

* Note: Some of the variables are only obtainable after some of the steps below.

## Setting up Twitter Bot

To populate the .env file and run a Twitter bot, the `CONSUMER_KEY`, `CONSUMER_SECRET`, `ACCESS_KEY` and `ACCESS_SECRET` is required.

1. Create a normal twitter account and apply for a [twitter developer app](https://developer.twitter.com/en).

2. The 4 twitter variables can be obtained within the twitter developer app page.

## Trying the app out Locally / Docker / Production

To run the app localy, it's easier to use an sqlite database compared to a postgresql server since sqlite only utilizes a single file. (This is however not ideal for production)

If you would like to experience using a Postgres server locally, the provided docker-compose file builds and runs the FastAPI app and postgres server together.

For production, it is advised to use the provided Cloud SQL instance for better reliability and ease of use.

Simply comment in and out the following codes to change databases based on the runtime. 

```python
# Run locally
DATABASE_URL = "sqlite:///./tweets.db"
```

```python
# Connecting to docker postgres server with docker compose
DATABASE_URL = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@postgresserver/{DB_NAME}"
```

```python
# Connecting with Cloud SQL Postgres server
DATABASE_URL = sqlalchemy.engine.url.URL(
  drivername='postgres+pg8000',
  username=DB_USERNAME,
  password=DB_PASSWORD,
  database=DB_NAME,
  query={
    'unix_sock': '/cloudsql/{}/.s.PGSQL.5432'.format(CONNECTION_NAME)
  }
)
```

To run the app locally, call

```shell
make run-local
```

To run the app with docker-compose (equipped with a postgres server), call

```shell
make docker-compose
```

## Spinning up a Postgres server with Cloud SQL

Google Cloud SQL is choosen to house the postgres server separately from the API endpoints since it's not ideal to spin up a database server in Cloud Run's stateless environment.

1. Makefiles are used to simplify the resource creation process. After populating the .env files with the intended server configurations, simply call 

```shell
make create-postgres-instance
```

## Cloud Run

Cloud Build is used to build the docker image and save it within google registry and Cloud Run is used to run the container in a serverless environment. 

* Serverless provides the ideal situation for a hands-off approach to dev-ops; it will scale up with high traffic and even scale to zero when not in used. 

After populating the .env variables:

```shell
make docker-cloud-build-run
```

## Populating the server

After Cloud Run service is running, visit the [URL]/docs. You will be greeted with [FastAPI's](https://fastapi.tiangolo.com/) automatic interative documentation powered by [Swagger UI](https://github.com/swagger-api/swagger-ui). 

![](docs/fastapi-docs.png)

1. Select the `/add_tweets_file/` endpoint, enter the x-token and upload the currated tweets file generated during the model training phase.

2. You can use the `/tweets/` endpoint to verify that the postgres database has been populated with the currated tweets.

## Cloud Scheduler

Sets up an external cron to trigger the FastAPI endpoints

```shell
make add-scheduler
```

## Costs

* Cloud Run: Effectively zero, it only charges on compute time and since it runs mainly on a schedule, it will be scaled to zero most of the time.

* Cloud Scheduler: Effectively zero / 3 free jobs per month

* Cloud SQL: ~$7/mo for the lowest DB config. The most expensive part, cost here can be further minimized by spinning the DB instance on/off based on the scheduler. 

