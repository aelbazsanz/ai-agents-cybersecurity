# AI Agents for Cybersecurity - Project Context

## Overview
This project is a hands-on exploration of AI agents applied to cybersecurity, designed around incremental, reproducible labs where AI agents interact with deliberately vulnerable environments. The goal is to understand both how to build AI agents capable of performing cybersecurity tasks and how to attack, defend, and secure AI agents themselves.

## Project Structure
```
ai-agents-cybersecurity/
├── infrastructure/               # Shared services used by all labs
│   └── docker-compose.yml       # Ollama service for local LLM
├── labs/                         # Independent cybersecurity labs (incremental)
│   ├── lab01-basic-agent/       # Foundations: LLM interaction, tool calling, agent loop
│   ├── lab02-agent-isolated-target/ # Network reconnaissance in isolated environment
│   ├── lab02-audit/             # Security assessment of lab02 baseline
│   └── lab03-agent-stateful/    # Stateful agent with persistent side effects
```

## Infrastructure
The shared infrastructure provides a local LLM via Ollama:
- Runs as a Docker container exposing API on port 11434
- Model configurable via environment (default: qwen3:8b)
- Models persisted in Docker volume for reuse across labs
- Accessible via `http://ollama:11434` from lab containers

## Incremental Labs Approach

### Lab 01 — Basic Agent
**Focus**: Understanding LLM-agent mechanics without frameworks
- Build minimal agent from scratch interacting with Ollama
- Establish core components: LLM, Agent Runtime, Policy, Tools
- Key insight: Separation between LLM capability, runtime capability, and tool capability
- Security boundary: LLM-generated tool requests treated as untrusted input
- Tools: Date/time utilities with permission policy enforcement

### Lab 02 — Agent Isolated Target
**Focus**: Network-capable reconnaissance agent in isolated environment
- Dual-network architecture: LLM network (Ollama access) + Target network (isolated)
- Target: Minimal HTTP service on internal Docker network (no external access)
- Tools: Network reconnaissance (`resolve_host`, `check_tcp_port`, `http_get`)
- Security principle: Establish functional baseline for later security assessment
- Current status: Frozen baseline ready for audit (lab02-audit)

### Lab 02 Audit
**Focus**: Security assessment of Lab 02 baseline
- Independent copy of Lab 02 for controlled experimentation
- Systematic evaluation of: tool access, trust boundaries, data flows, authorization
- Uses OWASP GenAI and MITRE frameworks for structured assessment
- Methodology: Baseline → Threat hypothesis → Experiment → Evidence → Control → Re-test

### Lab 03 — Stateful Agent
**Focus**: Extending Lab 02 into stateful agent with persistent side effects
- Adds resource ownership, authorization decisions, and state-changing tools
- Target application: Record-oriented API with JSON-backed state
- Resource classes: Public (readable), Analyst-owned (read/modify), Restricted (denied)
- Agent identity: Explicit `X-Agent-User: analyst` header (not strong auth)
- Tools: Network tools (inherited) + Record tools (`get_record`, `list_records`, `create_record`, `update_record`)
- Security boundary: Authorization enforced by target application, not by LLM
- Current status: Implementing stateful capabilities (record.py modified recently)

## Security Principles Established
1. **LLM-generated tool calls are untrusted input** - Runtime must validate/authorize before execution
2. **Tool authorization must be enforced outside the model** - Programmatic policy enforcement required
3. **Model capabilities ≠ Tool capabilities** - LLM may reason about operations it cannot execute
4. **Tool execution creates a security boundary** - Impact scales with tool power (filesystem, network, etc.)
5. **Tool results become part of LLM context** - Output can influence subsequent model behavior

## Current Development Focus
Recent work (commit 3aa8a1a) modified `record.py` in Lab 03, indicating active development of stateful agent capabilities. The project follows the progression:
Lab 01 (Basic) → Lab 02 (Network) → Lab 02-Audit (Security) → Lab 03 (Stateful) → Lab 03-Audit (Security)

Each lab builds on previous concepts while introducing new security dimensions for incremental learning and controlled experimentation.

## Technology Stack
- Python 3.13+ with `uv` package manager
- Docker & Docker Compose for containerization
- Ollama for local LLM serving
- Open-source LLMs (configurable)
- Minimal abstractions to understand underlying mechanisms before frameworks