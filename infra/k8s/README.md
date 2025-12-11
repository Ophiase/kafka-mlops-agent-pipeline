# Helm Deployment

This directory now ships a single Helm chart that mirrors the Docker Compose topology (Kafka, mastodon-fetcher, metrics-processor, llm-server, dashboard). Use it for running the full stack on kind or any Kubernetes cluster.

Docker Compose still provides hot-reload via bind mounts. Kubernetes pods run exactly what is baked in the dev images, so rebuild the images first when you change code.

## Prerequisites
- Docker
- kind
- kubectl
- Helm
- make (optional, commands are in the Makefile)

## Typical flow
```bash
# One-time: create a kind cluster
make create-cluster

# Rebuild images after code changes
make build-images

# Load the dev images into kind so Helm can pull them
make kind-load-images

# Install/upgrade the chart into namespace infra
make deploy

# (Optional) inspect rendered manifests
make template

# Follow dashboard logs or port-forward locally
make logs
make port-forward

# Cleanup
make undeploy
```

Notes
- Release name defaults to `mastodon-agent-mlops` and the namespace to `infra` (see Makefile).
- Services keep the same DNS names as docker-compose (`kafka`, `mastodon-fetcher`, `metrics-processor`, `llm-server`, `dashboard`).
- Tweak images, ports, or env vars via `values.yaml` or `--set` flags when calling Helm.