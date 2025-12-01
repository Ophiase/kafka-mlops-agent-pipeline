# Kubernetes Deployment

This directory contains the Kubernetes equivalent of the Docker Compose setup. 

Docker Compose is great for local development and testing, but Kubernetes provides a more robust and scalable environment for deploying applications.

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

# Build the Docker images
make build-dashboard
# Load the Docker images into the kind cluster
make kind-load-dashboard

# Deploy the application to the Kubernetes cluster
make deploy

# Check logs
make logs
# Port-forward for local access
make port-forward
```