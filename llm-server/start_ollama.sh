#!/bin/sh

ollama serve &
until curl -sf http://localhost:11434/api/tags >/dev/null; do
    sleep 1
done

ollama pull qwen3:0.6b
wait