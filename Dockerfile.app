FROM python:3.8-slim

COPY requirements.txt .

RUN apt-get update \
    && pip3 install -r requirements.txt

COPY ./src/api /src/api
COPY ./src/utils /src/utils
COPY ./src/config.py /src/config.py
COPY .env /src/api/.env