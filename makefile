include .env
export
export MAKEFLAGS=--no-print-directory

download-tweets:
	python -m scripts.download_tweets --username=karpathy

run-local:
	uvicorn api.main:app --reload

docker-compose:
	docker-compose up --build

create-postgres-instance:
	gcloud sql instances create ${DB_INSTANCE} \
		--database-version=POSTGRES_11 \
		--tier=db-f1-micro \
		--region="asia-east1"
	gcloud sql users create ${DB_USERNAME} \
		--instance=${DB_INSTANCE}
		--password=${DB_PASSWORD}
	gcloud sql databases create ${DB_NAME} \
		--instance=${DB_INSTANCE}

docker-cloud-build:
	gcloud builds submit --tag gcr.io/${PROJECT_ID}/${DOCKER_INSTANCE_NAME}

docker-cloud-run:
	gcloud run deploy --image gcr.io/${PROJECT_ID}/${DOCKER_INSTANCE_NAME} \
		--platform managed \
		--port 8000 \
		--region asia-east1 \
		--allow-unauthenticated \
		--add-cloudsql-instances ${CONNECTION_NAME} \
		--update-env-vars INSTANCE_CONNECTION_NAME="${CONNECTION_NAME}"

docker-cloud-build-run:
	make docker-cloud-build
	make docker-cloud-run

add-scheduler:
	gcloud scheduler jobs create http ${SCHEDULER_JOB_NAME} \
		--schedule="0 9 * * *" \
		--uri=${CLOUD_RUN_URL}/tweet_currated/ \
		--description="Calls a Cloud Run endpoint for tweeting GPT2 generated tweets" \
		--headers=accept=application/json,x-token=${SECRET_TOKEN} \
		--http-method=POST \
		--time-zone=Asia/Kuala_Lumpur \
		--max-retry-attempts=5
