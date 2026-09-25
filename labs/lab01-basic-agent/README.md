# Lab 01 — Basic Agent

## Objective

Build a minimal AI agent from scratch using a locally hosted Large Language Model (LLM), without relying on agent frameworks such as LangChain or LangGraph.

The purpose of this lab is to understand the fundamental building blocks of an AI agent before introducing more advanced agent architectures, external tools, and cybersecurity attack scenarios.

The agent is intentionally implemented in a simple and explicit way so that its behavior can be inspected and modified easily.

---

## Learning Goals

By completing this lab, we learn how to:

* interact with a local LLM
* maintain conversation history
* expose tools to an LLM
* implement a tool registry
* dispatch tool calls
* implement an agent decision loop
* execute multiple tools
* execute dependent sequential tool calls
* collect basic execution observability
* understand the boundary between an LLM and an agent
* introduce tool permissions and capabilities
* establish basic authorization boundaries around tools

The lab intentionally avoids agent frameworks so that the underlying mechanisms remain visible.

---

## Architecture

The current architecture is intentionally simple:

```text
                    ┌─────────────────────┐
                    │       User          │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │       Agent         │
                    │                     │
                    │   Agent Loop        │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │        Ollama       │
                    │        + LLM        │
                    └──────────┬──────────┘
                               │
                         Tool Call
                               │
                    ┌──────────▼──────────┐
                    │    Tool Registry    │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │       Tool          │
                    └──────────┬──────────┘
                               │
                         Tool Result
                               │
                               ▼
                              LLM
```

The agent explicitly controls the interaction between the LLM and the available tools.

---

## Project Architecture

Lab 01 runs directly on the host machine.

This is intentional.

The project will later introduce containerized agents and vulnerable targets, but the first laboratory keeps the execution environment simple to make debugging and learning easier.

The broader project architecture is expected to evolve towards something similar to:

```text
                         Host
                          │
             ┌────────────┴────────────┐
             │                         │
             ▼                         ▼
       Shared Ollama              Docker Network
       Infrastructure                  │
                              ┌────────┴─────────┐
                              │                  │
                              ▼                  ▼
                         Agent Container   Vulnerable Target
```

Lab 01 does **not** implement this containerized architecture yet.

Future laboratories may introduce:

* containerized AI agents
* isolated vulnerable applications
* vulnerable services
* dedicated attacker/defender environments
* Docker networks separating components
* controlled communication between agents and targets

This separation will become particularly important when studying agent security and attack scenarios.

---

## Current State

The lab currently implements:

1. Direct LLM interaction
2. Interactive conversation
3. Tool calling
4. Tool registry and dispatcher
5. Agent decision loop
6. Multiple tool calls
7. Sequential dependent tool calls
8. Basic observability

The next stage is to introduce:

9. Tool permissions and capabilities
10. Input validation
11. Trust boundaries
12. Security-oriented tool usage

---

## LLM vs Agent

An important concept in this lab is the difference between an LLM and an agent.

A simple LLM interaction looks like:

```text
User
 │
 ▼
LLM
 │
 ▼
Response
```

The LLM generates text, but it does not independently execute actions.

The agent introduces an execution loop:

```text
User
 │
 ▼
Agent
 │
 ▼
LLM
 │
 ├── Final answer ───────────────► Agent
 │
 └── Tool call
        │
        ▼
      Tool
        │
        ▼
    Tool result
        │
        ▼
       LLM
        │
        ▼
   Final answer
```

The agent therefore acts as the control layer between the LLM and external capabilities.

This distinction becomes especially important from a cybersecurity perspective because the security boundary is not only the model itself.

The agent controls what the model is allowed to do.

---

## Tool Registry and Dispatcher

Tools are registered explicitly in:

```text
src/lab01_basic_agent/tools/registry.py
```

The registry currently exposes:

* `get_current_time`
* `get_current_date`
* `days_until_date`

The dispatcher receives the requested tool name and its arguments:

```text
LLM
 │
 │ tool name + arguments
 ▼
Tool Registry
 │
 ▼
Dispatcher
 │
 ▼
Tool
```

This explicit registry will later provide a natural place to introduce authorization and capability controls.

---

## Agent Loop

The agent repeatedly performs the following steps:

```text
1. Send conversation to LLM
2. Inspect LLM response
3. Check whether a tool call was requested
4. Execute the requested tool
5. Add the tool result to the conversation
6. Ask the LLM again
7. Stop when the LLM produces a final response
```

Conceptually:

```text
        ┌───────────────┐
        │     Agent     │
        └───────┬───────┘
                │
                ▼
             ┌─────┐
             │ LLM │
             └──┬──┘
                │
         ┌──────┴──────┐
         │             │
    Tool call       Final answer
         │
         ▼
       Tool
         │
         ▼
    Tool result
         │
         └──────────► LLM
```

---

## Multiple Tool Calls

The agent can execute more than one tool during a single task.

For example:

```text
LLM
 │
 ├── get_current_date
 │
 ├── get_current_time
 │
 └── days_until_date
```

The agent processes the requested tools and returns their results to the LLM.

This demonstrates that an agent can coordinate multiple capabilities rather than simply generating a single response.

---

## Sequential Multi-Step Tasks

A more important experiment is a task where one tool depends on the output of another.

Example:

```text
User
 │
 ▼
LLM
 │
 ▼
get_current_date()
 │
 ▼
2026-09-25
 │
 ▼
LLM
 │
 ▼
days_until_date(
    current_date="2026-09-25",
    target_date="2026-10-01"
)
 │
 ▼
6
 │
 ▼
LLM
 │
 ▼
Final answer
```

This demonstrates genuine agentic behavior because the result of the first tool call becomes an input to the next decision.

---

## Observability

The agent implements basic execution observability.

For each execution it records:

* iteration number
* LLM execution time
* tool execution time
* number of tool calls
* total execution time

Example:

```text
[Agent] Iteration 1
[Agent] LLM response received in 50.319s
[Agent] Tool requested: get_current_date
[Agent] Tool result: 2026-09-25
[Agent] Tool duration: 0.000022s

[Agent] Iteration 2
[Agent] LLM response received in 73.486s
[Agent] Tool requested: days_until_date
[Agent] Tool result: 6
[Agent] Tool duration: 0.002071s

[Agent] Run summary
[Agent] Iterations: 3
[Agent] Tool calls: 2
[Agent] LLM time: 147.784s
[Agent] Tool time: 0.002093s
[Agent] Total time: 147.787s
```

The purpose is not to build a complete observability platform at this stage.

The objective is to understand what happened during an agent execution.

More advanced tracing, structured logging, metrics, OpenTelemetry, and dashboards can be introduced in later laboratories when they become useful for security analysis.

---

## Tool Permissions and Capabilities

The next stage of the lab introduces a security boundary between the LLM and tool execution.

Currently the conceptual flow is:

```text
LLM
 │
 │ tool call
 ▼
execute_tool()
```

The next architecture will introduce authorization:

```text
LLM
 │
 │ tool call
 ▼
┌──────────────────────┐
│   Tool Permission    │
│       Policy         │
└──────────┬───────────┘
           │
      ┌────┴─────┐
      ▼          ▼
    ALLOW       DENY
      │
      ▼
 execute_tool()
```

This introduces several important security concepts:

* capabilities
* least privilege
* authorization
* allowlists
* denied operations
* trust boundaries

The key question is:

> What is the agent actually authorized to do, independently of what the LLM asks it to do?

This distinction will become increasingly important as the project introduces more powerful tools.

---

## Security Relevance

Although this lab is not yet an offensive security laboratory, it establishes the architecture that future security experiments will target.

An AI agent can be viewed as:

```text
LLM
 │
 ▼
Decision
 │
 ▼
Tool
 │
 ▼
External effect
```

Every transition represents a potential security boundary.

Future laboratories will investigate scenarios such as:

```text
Prompt Injection
       │
       ▼
      LLM
       │
       ▼
     Agent
       │
       ▼
  Tool Authorization
       │
       ▼
      Tool
       │
       ▼
External System
```

Possible future attack surfaces include:

* prompt injection
* tool misuse
* malicious tool descriptions
* excessive permissions
* tool poisoning
* malicious MCP servers
* malicious Skills
* filesystem access
* command execution
* network access
* vulnerable applications
* compromised external services

---

## Infrastructure

Ollama is provided as shared infrastructure for the project.

It is located outside the individual laboratories:

```text
infrastructure/
├── docker-compose.yml
├── .env
└── .env.example
```

The current model is:

```text
Ollama
└── qwen3:8b
```

Individual laboratories do not run their own Ollama instance.

This allows future labs to share the same LLM infrastructure while keeping their own agent implementations and security targets isolated.

---

## Environment

Lab 01 currently runs directly on the host.

Expected environment:

```text
Host
├── Python
├── uv
├── Lab 01 agent
└── Shared Ollama
```

Future labs may use:

```text
Host
│
├── Shared Ollama
│
└── Docker
    ├── Agent
    ├── Vulnerable target
    ├── Supporting services
    └── Security tooling
```

Containerization will therefore be introduced when it provides a concrete security or isolation benefit rather than being added prematurely.

---

## Configuration

Create a `.env` file:

```dotenv
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=qwen3:8b
```

The corresponding `.env.example` should be kept in the repository without secrets.

---

## Requirements

* Python 3.13+
* `uv`
* Docker (for the shared infrastructure)
* Ollama infrastructure running
* `qwen3:8b` model available

---

## Installation

From the laboratory directory:

```bash
uv sync
```

Make sure the shared Ollama infrastructure is running.

---

## Running the Lab

Run the basic agent:

```bash
uv run python src/lab01_basic_agent/main.py
```

Run the agent tests:

```bash
uv run python src/lab01_basic_agent/agent_test.py
```

---

## Project Structure

```text
lab01-basic-agent/
├── .env
├── .env.example
├── pyproject.toml
├── .python-version
├── README.md
├── src/
│   └── lab01_basic_agent/
│       ├── __init__.py
│       ├── main.py
│       ├── agent.py
│       ├── agent_test.py
│       └── tools/
│           ├── __init__.py
│           ├── basic.py
│           └── registry.py
└── uv.lock
```

---

## Experiments Completed

### Experiment 1 — Direct LLM Interaction

Basic communication with the local LLM.

```text
User → LLM → Response
```

### Experiment 2 — Interactive Conversation

Maintaining message history across multiple user interactions.

```text
User
 ↓
LLM
 ↓
Conversation history
 ↓
LLM
```

### Experiment 3 — Tool Calling

Allowing the LLM to request execution of predefined tools.

```text
LLM → Tool → Result → LLM
```

### Experiment 4 — Tool Registry

Separating tool definitions from tool dispatch.

### Experiment 5 — Agent Decision Loop

Allowing the LLM to decide whether it needs a tool or can provide a final answer.

### Experiment 6 — Multiple Tool Calls

Executing multiple tools as part of a single task.

### Experiment 7 — Sequential Multi-Step Tasks

Using the result of one tool as input to a subsequent tool.

### Experiment 8 — Basic Observability

Measuring:

* iterations
* tool calls
* LLM execution time
* tool execution time
* total execution time

---

## Roadmap

```text
1.  Direct LLM interaction        — completed
2.  Interactive conversation      — completed
3.  Tool calling                  — completed
4.  Tool registry/dispatcher      — completed
5.  Agent decision loop           — completed
6.  Multiple tool calls           — completed
7.  Sequential multi-step tasks   — completed
8.  Basic observability           — completed
9.  Tool permissions/capabilities — next
10. Input validation              — planned
11. Trust boundaries              — planned
12. Security experiments          — planned
13. Cybersecurity-oriented tools  — planned
```

---

## Future Laboratory Architecture

Lab 01 is intentionally simple.

Future laboratories will progressively introduce more realistic environments:

```text
                        AI Agents Cybersecurity
                                  │
             ┌────────────────────┼────────────────────┐
             │                    │                    │
             ▼                    ▼                    ▼
        Agent Labs          Vulnerable Targets    Infrastructure
             │                    │                    │
             ▼                    ▼                    ▼
       Docker Agents       Vulnerable Apps       Shared Ollama
             │
             ▼
       Security Tools
```

The objective is to eventually build isolated environments where an agent can interact with intentionally vulnerable systems.

These environments will allow the project to study both:

* **Red Team:** how AI agents can be manipulated or abused
* **Blue Team:** how agent behavior can be monitored, constrained, and defended

---

## Key Takeaways

The main lessons from Lab 01 are:

1. An LLM is not automatically an agent.
2. An agent adds a control loop around an LLM.
3. Tools give an agent the ability to interact with external systems.
4. Tool registries define the capabilities available to the agent.
5. Tool results can become inputs to subsequent agent decisions.
6. Observability helps understand what happened during an execution.
7. The agent, not only the LLM, is part of the security boundary.
8. Tool permissions and capabilities are therefore fundamental security concepts.
9. Containerization will be introduced in later labs when isolation and realistic attack environments become necessary.
10. The ultimate goal is to understand how agentic systems can be built, attacked, monitored, and secured.
