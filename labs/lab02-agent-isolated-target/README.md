# AI Agents Cybersecurity

A research and experimentation project focused on cybersecurity agents powered by Large Language Models (LLMs).

The project explores how autonomous AI agents can perform cybersecurity tasks, how their capabilities emerge from the interaction between the LLM, the agent runtime, tools, permissions and the surrounding environment, and how these systems can be evaluated from a cybersecurity perspective.

The goal is not to build a single cybersecurity product, but to create a collection of reproducible security laboratories where agent behavior can be observed, tested and analyzed.

---

## Project Goals

The project aims to explore:

* How LLMs can be used as autonomous cybersecurity agents.
* How an agent runtime translates LLM decisions into real actions.
* How tools extend an agent's capabilities.
* How permissions and security policies constrain agent behavior.
* How agents interact with isolated cybersecurity environments.
* How external information can influence agent decisions.
* How autonomous agents can perform reconnaissance and other security tasks.
* How agent architectures can introduce new security risks.
* How established cybersecurity frameworks can be applied to AI-driven security scenarios.
* How agent behavior can be observed and reproduced experimentally.

A core principle of the project is:

> **LLM capability != Agent Runtime capability != Tool capability**

The LLM may decide what should happen, but the runtime controls what can actually happen.

---

## Project Philosophy

The laboratories are designed as controlled experiments rather than demonstrations designed to prove a predefined security classification.

The general workflow is:

```text
Threat Scenario
      │
      ▼
Laboratory Architecture
      │
      ▼
Experiment
      │
      ▼
Observed Agent Behavior
      │
      ▼
Evidence
      │
      ▼
Security Analysis
      │
      ├── OWASP LLM
      ├── OWASP Agentic
      ├── MITRE ATLAS
      └── MITRE ATT&CK
```

Framework mappings are applied **after observing the behavior**, when a mapping is justified.

The project does not modify experiments simply to force them to demonstrate a particular OWASP or MITRE technique.

---

## Architecture

The project separates shared infrastructure from individual laboratories.

```text
ai-agents-cybersecurity/
│
├── infrastructure/
│   └── Shared services
│
├── labs/
│   ├── lab01-...
│   ├── lab02-...
│   └── ...
│
└── README.md
```

### Shared Infrastructure

The `infrastructure/` directory contains services shared by multiple laboratories.

Currently this includes:

* Ollama
* Shared LLM Docker network
* Persistent Ollama model storage

The shared infrastructure is intentionally kept separate from individual laboratory environments.

### Laboratories

Each laboratory owns its own:

* Agent
* Target systems
* Target networks
* Docker configuration
* Python environment
* Tools
* Experiments
* Documentation

A laboratory should be independently reproducible and removable without destroying shared infrastructure.

---

## AI and Agent Architecture

The project deliberately distinguishes several layers of an AI agent:

```text
                  ┌──────────────┐
                  │     User     │
                  └──────┬───────┘
                         │
                         ▼
                  ┌──────────────┐
                  │     LLM      │
                  │              │
                  │ Decision /   │
                  │ Reasoning    │
                  └──────┬───────┘
                         │
                    tool request
                         │
                         ▼
                  ┌──────────────┐
                  │ Agent Runtime│
                  │              │
                  │ Tool control │
                  │ Policy       │
                  │ Execution    │
                  └──────┬───────┘
                         │
                         ▼
                  ┌──────────────┐
                  │    Tools     │
                  └──────┬───────┘
                         │
                         ▼
                  ┌──────────────┐
                  │ Environment  │
                  │ / Target     │
                  └──────────────┘
```

This separation is important because an LLM's reasoning or tool-calling capability does not automatically imply that the agent has the corresponding real-world capability.

The runtime determines which actions can actually be executed.

---

## Security Boundaries

Security isolation is a fundamental part of the project.

The general model is:

```text
                    HOST
                      │
          ┌───────────┴───────────┐
          │                       │
     Shared LLM Network       Lab Network
          │                    (isolated)
          │                       │
       Ollama                Agent ─── Target
```

Laboratories should avoid unnecessary access to the host system.

Where appropriate:

* Targets run inside dedicated Docker networks.
* Target networks may be `internal`.
* Agents may have access to multiple isolated networks when required by the experiment.
* Targets should not have direct access to shared LLM infrastructure unless explicitly required.
* Host ports should only be exposed when required.
* Docker socket access is avoided.
* Privileged containers are avoided.
* Arbitrary host filesystem access is avoided.
* Arbitrary command execution is avoided unless explicitly required by a future experiment.

Security boundaries are part of the experiment itself and should be documented for every laboratory.

---

## Technology

The project currently uses:

* Python
* `uv`
* Docker
* Docker Compose
* Ollama
* Qwen models
* Git / GitHub

Agent frameworks such as LangChain or LangGraph are intentionally not introduced at the beginning of the project.

The initial laboratories implement the agent runtime directly in Python in order to make its behavior and security boundaries explicit.

Frameworks may be introduced later when they are themselves relevant to an experiment.

---

# Laboratories

## Lab 01 — Basic Agent

**Status:** Completed

Lab 01 establishes the basic architecture of an agent runtime without using an agent framework.

The laboratory explores:

* LLM communication
* Conversation history
* Tool definitions
* Tool registry
* Tool dispatch
* Tool calling
* Sequential tool calls
* Multiple tool calls
* Basic permissions
* Error handling
* Iteration limits
* Basic observability

The laboratory establishes the conceptual separation:

```text
LLM capability
      !=
Agent Runtime capability
      !=
Tool capability
```

Lab 01 is considered closed and is not modified as the project evolves.

---

## Lab 02 — Agent Isolated Target

**Status:** In development

Lab 02 introduces the first cybersecurity-oriented agent laboratory.

The objective is to build a small cyber range where an autonomous agent performs network reconnaissance against an isolated target.

The current architecture is:

```text
                         HOST
                           │
                 ┌─────────┴─────────┐
                 │                   │
           LLM Network          Target Network
                 │                   │
              Ollama                Agent
                                     │
                                     │
                                     ▼
                                   Target
```

The Agent has access to two Docker networks:

```text
ai-agents-llm
      │
      └── Agent ──── Ollama

target-network
      │
      ├── Agent
      └── Target
```

The target network is isolated from external networks.

The Agent is not configured as a router, NAT gateway or generic network forwarder.

### Current Target

The target is a minimal Python HTTP service running inside its own container.

It currently exposes:

```text
TCP/8080
```

with:

```text
GET /
GET /health
```

The target does not expose host ports through Docker Compose.

### Current Agent Capability

The first implemented reconnaissance tool is:

```text
resolve_host(host)
```

The agent can use this tool to resolve the target hostname through Docker DNS.

Further reconnaissance capabilities will be added incrementally.

---

# Security Frameworks

Security frameworks are used as **analysis and classification frameworks**, not as a checklist that every laboratory must satisfy.

The project currently considers four complementary perspectives.

## OWASP Top 10 for LLM Applications

Used primarily to analyze security risks associated with LLM-powered applications.

Examples may include:

* Prompt injection
* Sensitive information disclosure
* Improper output handling
* Supply-chain risks
* Other risks applicable to LLM-based systems

Mappings will only be made when the laboratory produces relevant evidence.

## OWASP Top 10 for Agentic Applications

Used to analyze risks arising specifically from autonomous agent architectures.

This is particularly relevant when laboratories include:

* Tool use
* Autonomous decisions
* Planning
* Permissions
* External systems
* Memory
* Agent-to-agent interaction
* Autonomous actions

## MITRE ATLAS

Used to analyze adversarial behavior targeting AI and machine-learning systems, including agentic AI systems.

ATLAS provides a perspective focused on attacks against AI-enabled systems and their capabilities.

## MITRE ATT&CK

Used to describe traditional cybersecurity behavior performed by an agent.

For example, an agent performing network service discovery may map to traditional ATT&CK reconnaissance or discovery techniques.

---

## Framework Mapping Philosophy

The project deliberately avoids designing laboratories solely to satisfy framework categories.

Instead:

```text
Experiment
    │
    ▼
Observed behavior
    │
    ▼
Security interpretation
    │
    ▼
Applicable framework mappings
```

A single experiment may map to:

* OWASP LLM
* OWASP Agentic
* MITRE ATLAS
* MITRE ATT&CK

or to none of them.

Mappings should be justified by the observed behavior and documented evidence.

---

# Laboratory Documentation

Each laboratory should document, where applicable:

* Objective
* Architecture
* Components
* Responsibilities
* Network topology
* Security boundaries
* Trust boundaries
* Agent capabilities
* Agent limitations
* Tools
* Experiment setup
* Experiment inputs
* Observed behavior
* Tool calls
* Results
* Security implications
* Framework mappings
* Lessons learned

Documentation should distinguish clearly between:

```text
Expected behavior
Observed behavior
Interpretation
Security classification
```

This distinction is important when studying autonomous systems because the behavior selected by the LLM may differ from the behavior expected by the experiment designer.

---

# Observability

Agent actions should be observable and reproducible.

Where possible, tool execution should record:

```text
timestamp
tool
arguments
result
duration
```

For example:

```text
[12:01:04] TOOL resolve_host
           args={"host":"target"}

[12:01:04] RESULT
           {"ip":"172.18.0.3"}
```

As the agent runtime becomes more sophisticated, observability will be extended to include decisions, policies, errors and execution flow.

---

# Development Principles

The project follows several development principles.

### Incremental development

Capabilities are added one at a time.

For example:

```text
resolve_host()
      ↓
check_tcp_port()
      ↓
http_get()
      ↓
more advanced capabilities
```

Each capability should be implemented, tested and committed independently whenever practical.

### Explicit runtime control

The LLM should not directly control the environment.

The runtime mediates access to tools and external systems.

### Minimal privileges

Agents and targets receive only the network and system capabilities required by the experiment.

### Reproducibility

Laboratories should be reproducible from the repository.

### Isolation

A laboratory should be independently startable, testable and destroyable without affecting unrelated laboratories or shared infrastructure.

### Evidence-driven analysis

Security conclusions should be based on observed behavior and collected evidence rather than assumptions about what the model "should" do.

---

# Git Workflow

Development is performed incrementally.

Changes should generally follow:

```text
Design
  ↓
Implementation
  ↓
Test
  ↓
Observe
  ↓
Document
  ↓
Git commit
  ↓
Next increment
```

Small commits are preferred because they make laboratory evolution and experimental results easier to understand.

---

# Project Status

The project is actively evolving.

Current status:

```text
Infrastructure
    └── Shared Ollama environment       ✓

Lab 01
    └── Basic agent runtime             ✓ Completed

Lab 02
    ├── Isolated target                 ✓
    ├── Dual-network agent              ✓
    ├── Ollama connectivity             ✓
    ├── Interactive agent runtime       ✓
    ├── resolve_host()                  ✓
    ├── check_tcp_port()                └── Planned
    ├── http_get()                      └── Planned
    └── Reconnaissance experiments      └── Planned
```

The project will evolve incrementally as new agent capabilities, security scenarios and experiments are introduced.
