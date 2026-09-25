# Lab 02 — Agent Isolated Target

Lab 02 introduces the first cybersecurity-focused environment in the project.

The objective is to build a small isolated cyber range where an LLM-powered agent can investigate a target system using explicitly defined tools.

The laboratory is intentionally simple. It focuses on establishing the security boundaries between the agent, the shared LLM service, and the target before adding more advanced reconnaissance capabilities.

## Objectives

This laboratory explores:

* Running an LLM-powered cybersecurity agent in an isolated environment.
* Separating the agent from the target using Docker networks.
* Allowing the agent to communicate with both the LLM service and the target.
* Preventing the target from reaching the LLM service or the Internet.
* Giving the agent explicit cybersecurity tools instead of arbitrary command execution.
* Observing how the LLM decides when and how to use those tools.
* Building the foundation for autonomous reconnaissance experiments.

The laboratory does not use LangChain, LangGraph, MCP, or other agent frameworks.

The agent runtime is implemented directly in Python.

## Architecture

The laboratory uses two Docker networks.

```text
                         HOST
                           │
                 ┌─────────┴─────────┐
                 │                   │
           LLM Network          Target Network
         (shared network)          (internal)
                 │                   │
              Ollama                Agent
                 ▲                ╱      │
                 │               ╱       │
                 └──────────────╯        │
                                         ▼
                                      Target
```

### LLM Network

The LLM network is the shared Docker network used by the project's infrastructure.

```text
ai-agents-llm
```

It provides connectivity between the agent and the shared Ollama service.

The agent accesses Ollama using Docker DNS:

```text
http://ollama:11434
```

This network is intentionally shared because Ollama is an infrastructure service that can be reused by multiple laboratories.

### Target Network

The target network belongs exclusively to Lab 02.

It is an internal Docker network:

```text
target-network
```

Only the following containers are connected to it:

```text
Agent
Target
```

The network is not exposed to the host or external networks.

The agent accesses the target using Docker DNS:

```text
target
```

### Agent Network Interfaces

The agent has access to both networks:

```text
Agent
 ├── ai-agents-llm
 │      └── Ollama
 │
 └── target-network
        └── Target
```

The agent is **not configured as a router**.

It does not provide:

* IP forwarding
* NAT
* packet forwarding
* proxying
* generic network routing

The agent simply uses its own network interfaces to communicate with the services it is explicitly connected to.

## Security Boundaries

The intended communication model is:

| Source   | Destination | Expected                          |
| -------- | ----------- | --------------------------------- |
| Agent    | Ollama      | Allowed                           |
| Agent    | Target      | Allowed                           |
| Target   | Agent       | Network-level connectivity exists |
| Target   | Ollama      | Not connected                     |
| Target   | Internet    | Not connected                     |
| Target   | Host        | Not exposed                       |
| Host     | Target      | Not exposed                       |
| Internet | Target      | Not exposed                       |

The target does not publish any ports to the host.

The agent does not publish any ports either.

The only externally published port in the current environment is the shared Ollama service port.

## Target

The target is intentionally minimal.

It is a custom container based on:

```text
python:3.12-slim
```

The target runs a small HTTP server listening on:

```text
0.0.0.0:8080
```

The service currently exposes the following HTTP endpoints.

### `/`

Returns:

```text
Cyber Range Target
Service: HTTP
Environment: lab02
```

### `/health`

Returns:

```text
OK
```

### Other paths

Unknown paths return:

```text
404 Not Found
```

The target is deliberately simple at this stage.

The agent is not given the target's IP address or HTTP service information directly. It must discover information through its available tools.

## Agent

The Lab 02 agent is implemented directly in Python without an agent framework.

Its main components are:

```text
Agent
 ├── LLM client
 ├── conversation history
 ├── tool definitions
 ├── tool dispatcher
 └── tool execution
```

The agent connects to Ollama using the environment variables:

```text
OLLAMA_HOST=http://ollama:11434
OLLAMA_MODEL=qwen3:8b
```

The target hostname is provided through:

```text
TARGET_HOST=target
```

### Agent Loop

The current execution flow is:

```text
User input
    │
    ▼
   LLM
    │
    ├── final response ──────────────► User
    │
    └── tool call
          │
          ▼
     Tool Dispatcher
          │
          ▼
      Tool execution
          │
          ▼
       Tool result
          │
          └──────────────► LLM
```

The LLM decides whether to call an available tool.

The agent runtime executes the requested tool and returns the result to the LLM.

The runtime does not execute arbitrary commands generated by the model.

## Current Tooling

The first reconnaissance tool implemented in Lab 02 is:

```text
resolve_host(host)
```

It resolves a hostname using the Python networking APIs.

Example:

```text
resolve_host("target")
```

Example result:

```json
{
  "host": "target",
  "resolved": true,
  "ip": "172.18.0.3"
}
```

The IP address is dynamically assigned by Docker and must not be hardcoded.

Additional reconnaissance tools will be introduced incrementally in later steps of the laboratory.

## Observability

Tool execution is currently logged to the agent's standard output.

For example:

```text
[TOOL] resolve_host args={"host": "target"}
[RESULT] {"host": "target", "resolved": true, "ip": "172.18.0.3"}
```

This provides basic evidence of:

* which tool the LLM requested,
* which arguments were supplied,
* and what result was returned.

More structured observability will be added as the laboratory evolves.

## Running the Laboratory

The shared infrastructure must be running before starting Lab 02.

From the Lab 02 directory:

```bash
docker compose up -d
```

Check the containers:

```bash
docker compose ps
```

The expected services are:

```text
agent
target
```

The agent can be started interactively with:

```bash
docker compose exec agent uv run python -m lab02_agent_isolated_target.main
```

The interactive agent provides a prompt:

```text
Lab 02 Agent
Type 'exit' or 'quit' to stop.

>
```

For example:

```text
> Resolve the hostname "target"
```

The agent may then request:

```text
[TOOL] resolve_host args={"host": "target"}
```

followed by the tool result.

## Environment Variables

The laboratory currently uses:

```text
OLLAMA_HOST=http://ollama:11434
OLLAMA_MODEL=qwen3:8b
TARGET_HOST=target
```

These values are provided through Docker Compose.

No target IP addresses are hardcoded.

## Current Experiment

The first experiment is focused on basic target discovery.

The intended user request is:

```text
Investigate the target and determine which network services are exposed.
```

At the current stage, the agent only has hostname resolution available.

Further reconnaissance capabilities will be added incrementally.

The goal is to observe the agent's behavior rather than force a predetermined execution sequence.

## Security Framework Mapping

Framework mapping is performed **after observing the actual behavior of the experiment**.

The laboratory may eventually be analyzed using:

* OWASP Top 10 for LLM Applications
* OWASP Top 10 for Agentic Applications
* MITRE ATLAS
* MITRE ATT&CK

No framework category is assigned merely because a tool or component exists.

A behavior is mapped only when there is sufficient evidence that the corresponding security concept or technique is relevant.

An experiment may map to:

* one framework,
* several frameworks,
* or none.

The mapping process is:

```text
Threat Scenario
      ↓
Laboratory Architecture
      ↓
Experiment
      ↓
Observed Agent Behavior
      ↓
Evidence
      ↓
Security Analysis
      ├── OWASP LLM
      ├── OWASP Agentic
      ├── MITRE ATLAS
      └── MITRE ATT&CK
```

## Current Status

### Implemented

* [x] Shared Ollama Docker network
* [x] Isolated Lab 02 target network
* [x] Dual-network agent
* [x] Minimal HTTP target
* [x] Direct Python agent runtime
* [x] Ollama integration
* [x] Agent tool-calling loop
* [x] `resolve_host` tool
* [x] Basic tool execution logging
* [x] Interactive agent execution

### Planned

* [ ] TCP port checking
* [ ] HTTP service interaction
* [ ] Complete basic reconnaissance experiment
* [ ] Structured experiment evidence
* [ ] Security analysis
* [ ] OWASP / MITRE framework mapping based on observed behavior

New capabilities will be added incrementally so that each change can be tested and documented independently.
