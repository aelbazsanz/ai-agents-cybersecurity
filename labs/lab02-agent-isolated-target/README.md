# Lab 02 — Agent Isolated Target

## Objective

Lab 02 is the first cybersecurity-focused laboratory in the project.

The goal is to build a small autonomous reconnaissance agent that can investigate an isolated target through a set of network reconnaissance tools.

The lab intentionally does **not** implement security controls such as input validation, tool authorization policies, guardrails, or agent-specific restrictions.

The purpose is to establish a functional baseline that can later be assessed from a security perspective.

The laboratory follows the project's principle of building the system first and auditing its actual behavior afterwards.

---

## Architecture

Lab 02 uses two separate Docker networks.

```text
                         HOST
                           │
                 ┌─────────┴─────────┐
                 │                   │
           LLM Network          Target Network
         ai-agents-llm            internal
                 │                   │
              Ollama                Agent
                 ▲                ╱      │
                 │               ╱       │
                 └──────────────╯        │
                                         ▼
                                      Target
```

### LLM network

The shared `ai-agents-llm` network provides access to the Ollama service.

```text
ai-agents-llm

    ┌──────────┐
    │  Ollama  │
    └────▲─────┘
         │
         │
    ┌────┴─────┐
    │   Agent  │
    └──────────┘
```

This network is created and managed by the shared infrastructure in:

```text
infrastructure/
```

The Agent connects to Ollama using Docker DNS:

```text
http://ollama:11434
```

### Target network

Lab 02 creates a dedicated internal Docker network:

```text
target-network
```

Only the Agent and Target are connected to this network.

```text
target-network
     internal
        │
   ┌────┴────┐
   │         │
 Agent     Target
```

The network is `internal: true`.

This prevents the Target from directly reaching external networks and prevents external hosts from directly reaching the Target.

### Agent networking

The Agent has two network interfaces:

```text
Agent
 ├── ai-agents-llm
 └── target-network
```

The Agent is therefore able to communicate directly with both Ollama and the Target.

The Agent is **not configured as a router**.

It does not provide:

* IP forwarding
* NAT
* packet forwarding
* a proxy
* a generic routing service

The two network interfaces exist to give the Agent direct access to the two required network segments.

---

## Security Boundaries

The current laboratory intentionally provides a small but meaningful attack surface.

### Target isolation

The Target:

* has no published Docker ports;
* is only connected to `target-network`;
* cannot directly access Ollama;
* cannot directly access the Internet;
* cannot directly access the host;
* does not have access to the Docker socket.

### Agent isolation

The Agent:

* has access to Ollama through `ai-agents-llm`;
* has access to the Target through `target-network`;
* does not have access to the Docker socket;
* does not run privileged;
* does not provide arbitrary shell execution to the LLM.

The Agent's network capabilities are intentionally exposed through explicit tools.

---

## Target

The Target is a minimal HTTP service implemented specifically for the laboratory.

Location:

```text
target/
```

The service listens on:

```text
0.0.0.0:8080
```

Available endpoints:

| Endpoint       | Response        |
| -------------- | --------------- |
| `GET /`        | `200 OK`        |
| `GET /health`  | `200 OK`        |
| Any other path | `404 Not Found` |

Example response from `/`:

```text
Cyber Range Target
Service: HTTP
Environment: lab02
```

The Target is intentionally simple.

Its purpose is to provide observable network and application-layer behavior for the Agent rather than to emulate a complete production service.

---

## Agent

The Agent is implemented without LangChain, LangGraph, MCP, or other agent frameworks.

The runtime is responsible for:

1. Maintaining the conversation history.
2. Sending messages and tool definitions to Ollama.
3. Receiving tool calls from the model.
4. Dispatching tool calls.
5. Executing the corresponding Python functions.
6. Returning tool results to the model.
7. Continuing the agent loop until the model produces a final response.

Conceptually:

```text
User
 │
 ▼
LLM
 │
 │ tool call
 ▼
Agent Runtime
 │
 ▼
Tool
 │
 ▼
Target
 │
 ▼
Tool result
 │
 ▼
LLM
 │
 ▼
Final response
```

The LLM decides which available tool to call and which arguments to provide.

The Agent Runtime executes the requested tool.

---

## Reconnaissance Tools

Lab 02 currently provides three network reconnaissance tools.

### `resolve_host`

Resolves a hostname to an IP address using the container's DNS configuration.

Example:

```text
resolve_host("target")
```

Result:

```json
{
  "host": "target",
  "resolved": true,
  "ip": "172.18.0.2"
}
```

The IP address is dynamic and must not be hardcoded.

---

### `check_tcp_port`

Attempts to establish a TCP connection to a host and port.

Example:

```text
check_tcp_port("target", 8080)
```

Result:

```json
{
  "host": "target",
  "port": 8080,
  "reachable": true
}
```

A closed port produces a negative result, for example:

```json
{
  "host": "target",
  "port": 9999,
  "reachable": false,
  "error": "[Errno 111] Connection refused"
}
```

The tool uses a connection timeout and does not perform arbitrary packet-level scanning.

---

### `http_get`

Performs a simple HTTP GET request against a specified host, port, and path.

Example:

```text
http_get("target", 8080, "/")
```

Result:

```json
{
  "host": "target",
  "port": 8080,
  "path": "/",
  "status_code": 200,
  "body": "Cyber Range Target\nService: HTTP\nEnvironment: lab02\n"
}
```

HTTP application responses such as `404 Not Found` are returned as observable results rather than being treated as transport errors.

The current implementation intentionally does not support:

* HTTPS
* arbitrary HTTP methods
* configurable request headers
* authentication
* redirects as a separate control
* file downloads
* request bodies

---

## Observability

Tool execution is printed to the Agent console.

Example:

```text
[TOOL] check_tcp_port args={"host": "target", "port": 8080}
[RESULT] {"host": "target", "port": 8080, "reachable": true}
```

This provides basic visibility into:

* tool selection;
* tool arguments;
* tool results;
* the sequence of tool calls.

More advanced telemetry and security monitoring are outside the scope of the current baseline.

---

## Functional Validation

The following functionality has been validated.

### DNS resolution

```text
target → container IP
```

The IP address is assigned dynamically by Docker.

### TCP connectivity

The Agent successfully connected to:

```text
target:8080
```

A connection attempt to:

```text
target:9999
```

correctly returned `Connection refused`.

### HTTP

The Agent successfully retrieved:

```text
GET /
GET /health
GET /nonexistent
```

with the expected:

```text
200
200
404
```

responses.

### LLM tool calling

The LLM successfully selected and executed all three tools.

Examples:

```text
resolve_host
check_tcp_port
http_get
```

### Sequential tool usage

The Agent can perform multiple tool calls within a single investigation.

For example:

```text
resolve_host
    ↓
check_tcp_port
    ↓
http_get
    ↓
final response
```

### Autonomous reconnaissance

The Agent was also tested with:

```text
Investigate the target and determine which network services are exposed.
```

During the experiment, the model autonomously selected a set of common ports:

```text
22
80
21
443
25
```

The Agent did not test port `8080`, even though that port exposes the laboratory's HTTP service.

This demonstrates that the current reconnaissance behavior is model-driven rather than a systematic port-discovery algorithm.

The result is therefore dependent on the tools available and the decisions made by the LLM.

---

## Current Baseline Observations

The functional experiments revealed several behaviors that are intentionally preserved in this baseline.

### Tool argument selection

The LLM determines tool arguments from natural-language requests.

Ambiguous requests can therefore result in unexpected tool arguments.

This behavior is not corrected in Lab 02 because the laboratory is intended to represent the initial functional system.

### Limited reconnaissance strategy

The Agent does not currently implement a systematic port-scanning strategy.

It may select a limited set of common ports when asked to investigate network services.

Consequently, absence of evidence from the tested ports must not be interpreted as proof that no other services are exposed.

### Evidence and inference

The Agent can generate interpretations that go beyond the directly observed tool results.

For example, it may infer characteristics of an HTTP service from the response body.

The baseline does not currently enforce a distinction between:

```text
Observed evidence
```

and:

```text
LLM interpretation
```

These behaviors are intentionally preserved for later security assessment.

---

## Configuration

The Agent uses the following environment variables:

```text
OLLAMA_HOST=http://ollama:11434
OLLAMA_MODEL=qwen3:8b
TARGET_HOST=target
```

The shared infrastructure uses:

```text
OLLAMA_HOST_PORT=11434
```

The Target hostname is provided through Docker DNS rather than a hardcoded IP address.

---

## Running the Lab

Start the shared infrastructure first if it is not already running:

```bash
cd infrastructure
docker compose up -d
```

Then build the Lab 02 images.

The current Compose file references pre-built images rather than defining `build:` contexts, so the images are built explicitly.

From the Lab 02 directory:

```bash
docker build --no-cache -t ai-agents-lab02-agent:latest .
```

Build the Target image:

```bash
docker build --no-cache \
  -t ai-agents-lab02-target:latest \
  target/
```

Start the laboratory:

```bash
docker compose up -d
```

Check the containers:

```bash
docker compose ps
```

Start the Agent interactively:

```bash
docker compose exec agent \
  uv run python -m lab02_agent_isolated_target.main
```

Exit the Agent with:

```text
exit
```

Stop the laboratory:

```bash
docker compose down
```

The Lab 02 target network is removed when the laboratory is destroyed.

The shared Ollama infrastructure is not affected.

---

## Project Structure

```text
lab02-agent-isolated-target/
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── README.md
├── src/
│   └── lab02_agent_isolated_target/
│       ├── __init__.py
│       ├── main.py
│       ├── agent.py
│       └── tools/
│           ├── __init__.py
│           └── network.py
├── target/
│   ├── app.py
│   └── Dockerfile
└── uv.lock
```

---

## Framework Mapping

Lab 02 was **not designed around OWASP or MITRE frameworks**.

The current implementation deliberately focuses on building and observing a functional agent.

Security frameworks will be applied during the subsequent assessment phase, based on actual observed behavior and identified risks.

Potential future mapping may include:

* OWASP LLM Top 10
* OWASP Agentic AI
* MITRE ATLAS
* MITRE ATT&CK

A behavior will only be mapped to a framework when the evidence from the laboratory justifies the mapping.

Frameworks are therefore treated as **assessment lenses**, not as implementation checklists.

---

## Security Assessment Strategy

Lab 02 represents the functional baseline.

The next phase will create a separate laboratory:

```text
lab02-audit
```

The audit will assess the completed baseline without modifying it to introduce security controls.

The intended process is:

```text
Functional Lab
      ↓
Baseline
      ↓
Security Assessment
      ↓
Attack Scenario
      ↓
Experiment
      ↓
Evidence
      ↓
Finding / Risk
      ↓
Security Control
      ↓
Re-test
      ↓
Audit Report
```

The assessment will consider areas such as:

* tool authorization;
* tool argument validation;
* input validation;
* agent autonomy;
* untrusted tool results;
* prompt and instruction boundaries;
* network reachability;
* scope restrictions;
* egress controls;
* execution isolation;
* observability;
* guardrails.

Controls will be introduced only after the corresponding risks have been identified and demonstrated.

---

## Status

**Functional baseline complete.**

Implemented:

* Isolated Target container.
* Dedicated internal Target network.
* Shared Ollama network integration.
* Dual-network Agent.
* `resolve_host`.
* `check_tcp_port`.
* `http_get`.
* LLM tool calling.
* Sequential tool execution.
* Basic tool execution observability.
* Functional reconnaissance experiments.

The laboratory is now ready to be frozen as a baseline and used as the subject of a separate security assessment.

**No security controls specific to the audit phase have been implemented yet.**
