FROM ollama/ollama:0.13.0-rc0

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY start_ollama.sh /start_ollama.sh
RUN chmod +x /start_ollama.sh

ENTRYPOINT ["/start_ollama.sh"]
