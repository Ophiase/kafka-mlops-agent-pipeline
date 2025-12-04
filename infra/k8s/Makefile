KIND_CLUSTER := dev
NS := infra

DASHBOARD_IMAGE := infra-dashboard:dev
FETCHER_IMAGE := infra-mastodon-fetcher:dev
PROCESSOR_IMAGE := infra-metrics-processor:dev
LLM_IMAGE := infra-llm-server:dev
IMAGES := $(DASHBOARD_IMAGE) $(FETCHER_IMAGE) $(PROCESSOR_IMAGE) $(LLM_IMAGE)

# ---- Cluster lifecycle ----
create-cluster:
	kind create cluster --name $(KIND_CLUSTER)

delete-cluster:
	kind delete cluster --name $(KIND_CLUSTER)

# ---- Image helpers ----
build-images: build-dashboard build-mastodon-fetcher build-metrics-processor build-llm-server

build-dashboard:
	docker build -t $(DASHBOARD_IMAGE) -f ../../dashboard/Dockerfile ../../

build-mastodon-fetcher:
	docker build -t $(FETCHER_IMAGE) -f ../../mastodon-fetcher/Dockerfile ../../

build-metrics-processor:
	docker build -t $(PROCESSOR_IMAGE) -f ../../metrics-processor/Dockerfile ../../

build-llm-server:
	docker build -t $(LLM_IMAGE) -f ../../llm-server/Dockerfile ../../llm-server

kind-load-images:
	for image in $(IMAGES); do \
		kind load docker-image $$image --name $(KIND_CLUSTER); \
	done

# ---- Kubernetes manifests ----
deploy:
	kubectl apply -f namespace.yaml
	kubectl apply -f kafka --recursive
	kubectl apply -f mastodon-fetcher --recursive
	kubectl apply -f metrics-processor --recursive
	kubectl apply -f llm-server --recursive
	kubectl apply -f dashboard --recursive

undeploy:
	kubectl delete -f dashboard --namespace $(NS) --recursive || true
	kubectl delete -f llm-server --namespace $(NS) --recursive || true
	kubectl delete -f metrics-processor --namespace $(NS) --recursive || true
	kubectl delete -f mastodon-fetcher --namespace $(NS) --recursive || true
	kubectl delete -f kafka --namespace $(NS) --recursive || true
	kubectl delete namespace $(NS) || true

# ---- Observability ----
logs:
	kubectl -n $(NS) logs -l app=dashboard -f

port-forward:
	kubectl -n $(NS) port-forward svc/dashboard 58005:8000

# ---- Meta targets ----
all: build-images kind-load-images deploy
