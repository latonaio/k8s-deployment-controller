apply:
	kubectl apply -f k8s/deployment.yml

delete:
	kubectl delete -f k8s/deployment.yml

exec:
	sh shell/exec.sh

run:
	sh shell/run.sh

docker-build:
	bash docker-build.sh

docker-push:
	bash docker-build.sh push