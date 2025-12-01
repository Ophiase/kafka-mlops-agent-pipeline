KIND_CLUSTER := dev
NS := infra

create-cluster:
	kind create cluster --name $(KIND_CLUSTER)

delete-cluster:
	kind delete cluster --name $(KIND_CLUSTER)

build-dashboard:
	docker build -t infra-dashboard:dev -f ../../dashboard/Dockerfile ../../

kind-load-dashboard:
	kind load docker-image infra-dashboard:dev --name $(KIND_CLUSTER)

deploy:
	kubectl apply -f namespace.yaml
	kubectl apply -f dashboard --recursive

undeploy:
	kubectl delete -f dashboard --namespace $(NS) || true
	kubectl delete namespace $(NS) || true

logs:
	kubectl -n $(NS) logs -l app=dashboard -f

port-forward:
	kubectl -n $(NS) port-forward svc/dashboard 58005:8000

all: build-dashboard kind-load-dashboard deploy
