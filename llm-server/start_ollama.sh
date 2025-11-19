#!/bin/sh
ollama serve &
ollama pull qwen:0.6b
wait
