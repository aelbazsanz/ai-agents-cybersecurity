# AI Agents for Cybersecurity

A hands-on project for studying the design, implementation, and security of AI agents applied to cybersecurity.

The project is built around isolated, reproducible cybersecurity labs where AI agents interact with deliberately vulnerable environments. The goal is to understand both sides of the problem:

* how to build AI agents capable of performing cybersecurity tasks;
* how to attack, defend, and secure AI agents themselves.

## Goals

The project focuses on progressively exploring:

* AI agent fundamentals;
* LLM interaction and tool calling;
* autonomous agent loops;
* planning and memory;
* cybersecurity reconnaissance and analysis;
* offensive security agents;
* defensive security agents;
* prompt injection and indirect prompt injection;
* tool abuse and malicious tools;
* Skills and MCP security;
* observability and agent security.

The labs are designed to be incremental. Each lab introduces a small number of new concepts while building on the previous ones.

## Architecture

The project is divided into two main areas:

```text
ai-agents-cybersecurity/
├── infrastructure/
│   └── Shared services
│
└── labs/
    └── Independent cybersecurity labs
```

The shared infrastructure currently provides the local LLM through Ollama.

Each lab should remain as independent as possible and should contain everything required to reproduce the experiment.

## Infrastructure

The infrastructure is responsible for shared services used by the labs.

Currently:

* Docker Compose manages the infrastructure;
* Ollama provides the local LLM API;
* models are persisted in a Docker volume;
* the model can be changed through environment configuration.

See [`infrastructure/INFRASTRUCTURE.md`](infrastructure/INFRASTRUCTURE.md) for details.

## Labs

Labs will be added progressively under `labs/`.

Each lab should document:

1. Objectives
2. Background
3. Architecture
4. Environment
5. Challenge
6. Implementation
7. Execution
8. Expected behavior
9. Analysis
10. Lessons learned
11. Further experiments

Labs should use isolated and deliberately vulnerable targets. No real external systems should be required for the experiments.

## Development principles

The project follows these principles:

* **Incremental learning** — introduce complexity gradually.
* **Reproducibility** — labs should be easy to recreate.
* **Isolation** — cybersecurity targets must be deliberately vulnerable and isolated.
* **Observability** — agent decisions, LLM interactions, tool calls, and results should be visible whenever possible.
* **Minimal abstractions** — understand the underlying mechanisms before introducing agent frameworks.
* **Configurability** — infrastructure and model selection should not be hardcoded into individual labs.

## Technology

The initial technology stack includes:

* Python
* `uv`
* Docker
* Docker Compose
* Ollama
* Open-source LLMs

Additional frameworks and technologies will be introduced progressively as part of the labs.

## Roadmap

The project will evolve through several stages:

### 1. Agent fundamentals

* LLM client
* basic agent
* tool calling
* agent loop
* planning
* memory
* multi-step tasks

### 2. Cybersecurity agents

* reconnaissance
* network enumeration
* web reconnaissance
* vulnerability analysis
* exploitation in isolated environments

### 3. Defensive agents

* log analysis
* detection engineering
* incident investigation
* threat hunting
* SOC-style workflows

### 4. Agent security

* prompt injection
* indirect prompt injection
* tool abuse
* malicious tools
* privilege boundaries
* agent isolation

### 5. Skills and MCP security

* MCP fundamentals
* MCP tool security
* tool poisoning
* malicious MCP servers
* Skill security
* agent-to-agent interactions

The roadmap is intentionally flexible and will evolve as the labs are developed.

## Getting Started

Start the shared infrastructure:

```bash
cd infrastructure
docker compose up -d
```

Verify the Ollama service:

```bash
curl http://localhost:11434/api/tags
```

See [`infrastructure/INFRASTRUCTURE.md`](infrastructure/INFRASTRUCTURE.md) for configuration and troubleshooting information.
