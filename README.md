# Mastodon Agent (auto parser) - MLOPS Project

Work In Progress...

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
