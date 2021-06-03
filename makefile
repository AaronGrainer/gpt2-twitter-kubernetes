include .env
export
export MAKEFLAGS=--no-print-directory

download-tweets:
	python -m src.scripts.download_tweets --username=karpathy

run-local:
	uvicorn api.main:app --reload

docker-compose:
	docker-compose up --build -d

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


# Minikube
k8-init:
	kubectl create namespace gpt2-twitter
	kubectl config set-context minikube --namespace=gpt2-twitter
	minikube dashboard

k8-deploy-mongo:
	kubectl apply -f kubernetes/mongo-volume.yaml
	kubectl apply -f kubernetes/mongo.yaml

k8-port-forward-mongo:
	kubectl port-forward svc/mongo 4321:27017

skaffold-dev:
	skaffold dev

skaffold-delete:
	skaffold delete

minikube-view-service:
	minikube service gpt2-tweet-app-service -n gpt2-twitter


# Docker
docker-build:
	docker image build -f "docker/Dockerfile.tweet" .

docker-push:
	docker login
	docker image tag gpt2-twitter:latest aarongrainer/gpt2-twitter:latest
	docker push aarongrainer/gpt2-twitter:latest

update-job: docker-build docker-push
	kubectl delete -f kubernetes/post-tweet.yaml
	kubectl apply -f kubernetes/post-tweet.yaml

