include .env
export
export MAKEFLAGS=--no-print-directory

download-tweets:
	python -m src.scripts.download_tweets --username=karpathy

run-local:
	uvicorn api.main:app --reload

docker-compose:
	docker-compose up --build -d


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

