KIND_CLUSTER := dev
NS := infra
RELEASE := mastodon-agent-mlops
CHART := .

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

# ---- Helm deployment ----
deploy:
	helm upgrade --install $(RELEASE) $(CHART) --namespace $(NS) --create-namespace

undeploy:
	helm uninstall $(RELEASE) --namespace $(NS) || true

template:
	helm template $(RELEASE) $(CHART) --namespace $(NS)

# ---- Observability ----
logs:
	kubectl -n $(NS) logs -l app.kubernetes.io/component=dashboard -f

port-forward:
	kubectl -n $(NS) port-forward svc/dashboard 58005:8000

# ---- Meta targets ----
all: build-images kind-load-images deploy
