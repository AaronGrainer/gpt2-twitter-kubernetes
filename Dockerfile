FROM python:3.7-slim

COPY ./api /api/api
COPY .env /api/api/.env

RUN apt-get update \
    && pip3 install -r api/api/requirements.txt

ENV PYTHONPATH=/api
WORKDIR /api

EXPOSE 8000

ENTRYPOINT ["uvicorn"]
CMD ["api.main:app", "--host", "0.0.0.0"]