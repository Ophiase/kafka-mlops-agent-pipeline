# Kubernetes Deployment

This directory contains the Kubernetes equivalent of the Docker Compose setup.

Docker Compose is still great for hot-reload development because it mounts `/app` and `/shared`. In Kubernetes the containers run exactly as they are baked in their images, so there are **no bind mounts**. Because of that, make sure the dev images (e.g. `infra-mastodon-fetcher:dev`) already exist locally before deploying.

The manifests now cover every service from `docker-compose`:

- `kafka/` – single broker using `confluentinc/cp-kafka:8.1.0`.
- `mastodon-fetcher/` – FastAPI control plane for the fetcher loop.
- `metrics-processor/` – FastAPI control plane plus LLM integration.
- `llm-server/` – Ollama server pod the processor talks to.
- `dashboard/` – Django dashboard that orchestrates the other services.

## Setup Instructions

Requirements
- ``Docker``: Containerization platform to build and run containerized applications.
- ``kind``: Create the environment for deploying applications using Kubernetes.
- ``kubectl``: Applying configurations and managing the cluster.
- ``Make``: Automate the build and deployment process.
    - You can type directly the commands from the Makefile if you prefer not to use Make.

```bash
# Create the Kubernetes cluster using kind
make create-cluster

# (Optional) rebuild & reload the dev images if you changed them
make build-images
make kind-load-images

# Deploy every manifest (namespace + kafka + services)
make deploy

# Check dashboard logs or expose it locally
make logs
make port-forward
```

If you update the other service images, rebuild them with the same tags that `docker-compose` uses (`infra-*-service:dev`) and run `kind load docker-image <tag> --name dev` before redeploying.