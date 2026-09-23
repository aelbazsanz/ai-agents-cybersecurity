# Infrastructure

This directory contains the shared infrastructure used by the cybersecurity labs.

## Current Architecture

The current infrastructure consists of:

```text
Lab / Host
    |
    | HTTP
    v
Ollama
    |
    v
Local LLM
```

Ollama runs as a Docker container and exposes its API on port `11434`.

## Requirements

The infrastructure requires:

* Docker
* Docker Compose

The current setup is CPU-only. No NVIDIA GPU or CUDA configuration is required.

## Starting the Infrastructure

From the project root:

```bash
cd infrastructure
docker compose up -d
```

Check the container:

```bash
docker compose ps
```

Check the Ollama API:

```bash
curl http://localhost:11434/api/tags
```

## LLM Model

The model is configured through the `.env` file:

```dotenv
OLLAMA_MODEL=qwen3:8b
OLLAMA_HOST_PORT=11434
```

The current default model is `qwen3:8b`.

The model choice is intentionally configurable so that different models can be tested without changing the labs.

## Downloading a Model

Models are stored in the persistent Docker volume used by Ollama.

For example:

```bash
docker compose exec ollama ollama pull qwen3:8b
```

List installed models:

```bash
docker compose exec ollama ollama list
```

## Changing the Model

Change `OLLAMA_MODEL` in `.env`:

```dotenv
OLLAMA_MODEL=<model-name>
```

Then pull the model if it is not already installed:

```bash
docker compose exec ollama ollama pull <model-name>
```

Labs should read the configured model from their environment rather than hardcoding a specific model.

## Persistence

Ollama stores its models in the Docker volume:

```text
ai-agents-ollama-data
```

The volume allows downloaded models to survive container recreation.

List the volume:

```bash
docker volume ls
```

## Stopping the Infrastructure

Stop the services:

```bash
docker compose down
```

This does not remove the persistent model volume.

To remove the infrastructure and its stored models:

```bash
docker compose down -v
```

Use the second command only when the persisted models are no longer needed.

## Troubleshooting

### Check container status

```bash
docker compose ps
```

### View Ollama logs

```bash
docker compose logs ollama
```

### Check installed models

```bash
docker compose exec ollama ollama list
```

### Test the API

```bash
curl http://localhost:11434/api/tags
```

A healthy installation should return a JSON response containing the installed models.

## Future Infrastructure

The infrastructure may later include additional shared services such as:

* vulnerable target networks;
* databases;
* logging infrastructure;
* observability components;
* MCP servers;
* shared agent services.

These should only be added when they are required by a lab.
