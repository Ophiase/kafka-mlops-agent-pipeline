# Mastodon Agent - MLOPS Project (WIP)

This repository is a simple MLOPS project that demonstrates the integration of a Mastodon agent with Kafka for data streaming and processing.

The point is to learn building scalable architectures using:
- ✅ Docker (with proper isolation and shared resources)
- ✅ Docker Compose $\to$ ❌ K8s/Helm
- ✅ Mounted secrets $\to$ ❌ Vault or K8s secrets
- ❌ Terraform (local AWS simulation with LocalStack)
- ✅ Ollama $\to$ ❌ vLLM
    - Agent managed with LangChain/LangGraph
- Django mono $\to$ ❌ Django back + Next.js/Tailwind front

Remark: The syntax $x \to y$ means I will start with $x$ and move to $y$.

The word agent here refers to a stateless (no internal memory) automated event-based system. Perhaps, a more appropriate name would be "Mastodon Listener".

The Mastodon agent listens to new posts on a Mastodon instance, processes them using a language model, and streams the results to Kafka for further analysis or storage.

## Setup Instructions

### Quick Start

1. Install docker (cli)
2. 🎛️ Configure your secrets in `/infra/secrets` file.
3. 🎛️ Configure your llm server in `/infra/llm-server.env` file.
4. Start the services:

```bash
cd infra
docker compose up -d --build
```

5. Open the front http://localhost:58005 to access the application.
