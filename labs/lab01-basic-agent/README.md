# Lab 01 — Basic Agent

A minimal AI agent built from scratch to understand how LLM-based agents work internally and to establish the foundations for later cybersecurity experiments.

This lab intentionally avoids agent frameworks such as LangChain or LangGraph. The goal is to understand the underlying mechanics before introducing higher-level abstractions.

---

## Objective

Build a minimal agent capable of:

* interacting with a local LLM through Ollama
* maintaining conversation context
* exposing tools to the LLM
* receiving tool calls from the LLM
* validating and dispatching tool calls
* enforcing a basic tool permission policy
* executing multiple tools across multiple iterations
* passing tool results back to the LLM
* detecting when the LLM has produced a final response
* collecting basic execution metrics

The main objective is not to build a sophisticated production agent.

The objective is to understand the components that make an agent work and establish explicit security boundaries that can be attacked in later labs.

---

## Learning Goals

By completing this lab, the following concepts should be understood:

1. The difference between an LLM and an agent runtime.
2. How an LLM interacts with tools.
3. How tool calls are represented and executed.
4. How an agent loop works.
5. How multiple tool calls can be chained.
6. How sequential tool calls can depend on previous results.
7. How tool permissions can be enforced outside the LLM.
8. What happens when a requested tool is denied.
9. How the runtime determines that the LLM has finished.
10. Why tool authorization and model capabilities are different security concerns.
11. Why the runtime must not blindly trust LLM-generated tool requests.

---

# Architecture

The architecture intentionally separates the main components:

```text
                         ┌──────────────────┐
                         │      User        │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │       LLM        │
                         │     Ollama       │
                         └────────┬─────────┘
                                  │
                         tool call / response
                                  │
                                  ▼
                         ┌──────────────────┐
                         │  Agent Runtime   │
                         │                  │
                         │  Agent Loop      │
                         │  Dispatcher      │
                         │  Error Handling  │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │      Policy      │
                         │                  │
                         │  Is the tool     │
                         │  authorized?     │
                         └────────┬─────────┘
                                  │
                           allowed / denied
                                  │
                                  ▼
                         ┌──────────────────┐
                         │      Tools       │
                         │                  │
                         │ get_current_date │
                         │ get_current_time │
                         │ days_until_date  │
                         └──────────────────┘
```

The important security boundary is between the LLM and the tool execution layer.

The LLM can request a tool, but it does not directly execute the tool.

The Agent Runtime decides whether the requested operation is allowed and performs the actual execution.

---

# LLM vs Agent Runtime vs Tools

One of the most important concepts in this laboratory is that these components have different capabilities.

## LLM

The LLM is responsible for:

* generating text
* interpreting the conversation context
* deciding whether to request a tool
* generating tool arguments
* processing tool results
* generating the final response

The LLM does not directly execute Python functions.

For example, the LLM may generate a request equivalent to:

```text
days_until_date(
    current_date="2026-09-25",
    target_date="2026-10-01"
)
```

That is a request, not an execution.

---

## Agent Runtime

The Agent Runtime is the Python code implemented in this laboratory.

It is responsible for:

* sending messages to the LLM
* exposing available tools
* receiving tool calls
* checking whether tools exist
* checking whether tools are authorized
* executing authorized tools
* returning tool results to the LLM
* handling tool errors
* enforcing the iteration limit
* determining when the LLM has stopped requesting tools

The runtime therefore provides the operational capabilities of the agent.

---

## Policy

The policy determines which tools the Agent Runtime is allowed to execute.

For example:

```python
ALLOWED_TOOLS = {
    "get_current_date",
    "get_current_time",
}
```

If the LLM requests `days_until_date`, the tool exists but is not authorized.

The runtime rejects the request before executing the function.

This establishes an important distinction:

```text
Tool exists
    ≠
Tool is authorized
```

---

## Tools

Tools are normal Python functions that perform concrete operations.

For example:

```python
def get_current_date() -> str:
    ...
```

The tool itself does not decide whether it should be executed.

Authorization is handled by the Agent Runtime and its policy.

---

# Tool Registry and Dispatcher

Tools are registered in:

```text
src/lab01_basic_agent/tools/registry.py
```

The registry contains the available tools:

```python
TOOLS = {
    "days_until_date": days_until_date,
    "get_current_date": get_current_date,
    "get_current_time": get_current_time,
}
```

The dispatcher is responsible for:

1. looking up the requested tool
2. verifying that it exists
3. checking the permission policy
4. executing the tool
5. converting the result to a string

Conceptually:

```text
Tool request
     │
     ▼
Does the tool exist?
     │
   ┌─┴─┐
   │   │
  No  Yes
   │   │
   ▼   ▼
Error  Is it allowed?
           │
        ┌──┴──┐
        │     │
       No    Yes
        │     │
        ▼     ▼
      Deny   Execute
```

The current implementation distinguishes between:

```text
ValueError
```

for an unknown tool and:

```text
PermissionError
```

for a known but unauthorized tool.

---

# Agent Loop

The agent operates through an iterative loop.

The simplified flow is:

```text
User input
    │
    ▼
LLM
    │
    ├── tool call ──────────┐
    │                       │
    │                       ▼
    │                  Agent Runtime
    │                       │
    │                  Policy check
    │                       │
    │                       ▼
    │                  Tool execution
    │                       │
    │                       ▼
    │                  Tool result
    │                       │
    └───────────────────────┘
                │
                ▼
               LLM
                │
                ▼
         Final response
```

The loop continues until either:

* the LLM does not request another tool, or
* the maximum number of iterations is reached.

The current default maximum is:

```python
max_iterations = 5
```

This prevents an uncontrolled tool-calling loop.

---

# How the Agent Detects the Final Answer

The runtime currently uses the presence of tool calls as the termination signal.

After each LLM response, it checks:

```python
if not response.message.tool_calls:
    return response.message.content
```

Therefore:

```text
LLM response
     │
     ▼
Contains tool calls?
     │
   ┌─┴─┐
  Yes  No
   │    │
   ▼    ▼
Continue Final answer
```

This means that:

```text
no tool_calls
```

is interpreted by the runtime as:

```text
the LLM has finished
```

The runtime does not independently verify whether the answer is correct.

This is an intentional simplification for this laboratory.

---

# Multiple Tool Calls

The agent can process more than one tool call across the same execution.

For example, a task may require:

```text
get_current_date()
get_current_time()
```

The runtime executes the requested tools and returns their results to the LLM.

The LLM can then use those results to continue the task.

---

# Sequential Multi-Step Tasks

The lab also demonstrates dependent tool calls.

The following task was used:

```text
Use the available tools to determine how many days remain until
October 1, 2026. First obtain today's UTC date, then use that
result to calculate the number of days.
```

The resulting sequence was:

```text
Iteration 1
    │
    ├── get_current_date()
    │
    └── result: 2026-09-25

Iteration 2
    │
    ├── days_until_date(
    │       current_date="2026-09-25",
    │       target_date="2026-10-01"
    │   )
    │
    └── result: 6

Iteration 3
    │
    └── final LLM response
```

The important property is that the output of the first tool became an input to the second tool.

```text
get_current_date()
        │
        ▼
2026-09-25
        │
        ▼
days_until_date(
    current_date="2026-09-25",
    ...
)
```

This is a basic example of agentic multi-step execution.

---

# Tool Permissions and Capabilities

The lab introduces a basic authorization layer in:

```text
src/lab01_basic_agent/tools/permissions.py
```

Example:

```python
ALLOWED_TOOLS = {
    "get_current_date",
    "get_current_time",
    "days_until_date",
}
```

The LLM is allowed to request any exposed tool, but the runtime only executes tools that are authorized by the policy.

This creates an explicit security boundary:

```text
                    LLM
                     │
                     │ tool request
                     ▼
              Agent Runtime
                     │
                     ▼
                  Policy
                ┌────┴────┐
                │         │
              ALLOW      DENY
                │         │
                ▼         ▼
             Execute    Reject
                │
                ▼
               Tool
```

The policy is enforced by Python code rather than by trusting the LLM to respect the policy.

---

# What Happens When a Tool Is Denied?

A denied tool request is not silently discarded.

The runtime converts the denial into a tool result:

```text
Tool execution denied by security policy:
Tool not allowed: days_until_date
```

That result is then returned to the LLM as part of the conversation context.

The LLM receives a new inference request and can decide how to continue.

For example:

```text
Iteration 1
    │
    └── get_current_date()
            │
            ▼
        2026-09-25

Iteration 2
    │
    └── days_until_date(...)
            │
            ▼
          DENIED

Iteration 3
    │
    └── LLM processes the denial
            │
            └── calculates the result itself
```

In this experiment, the LLM produced:

```text
The current date is September 25, 2026.
...
Total = 6 days.
```

No Python calculation was performed in the third iteration.

The calculation was performed as part of the LLM's own inference.

This demonstrates an important distinction:

```text
Tool authorization
        ≠
LLM capability
```

Preventing the runtime from executing a tool does not prevent the LLM from generating an answer using its own capabilities.

---

# Security Boundary

The laboratory establishes the following conceptual security model:

```text
┌─────────────────────────────────────┐
│                 LLM                 │
│                                     │
│  Generate text                      │
│  Request tools                      │
│  Generate arguments                 │
│  Process tool results               │
└──────────────────┬──────────────────┘
                   │
                   │ untrusted request
                   ▼
┌─────────────────────────────────────┐
│          AGENT RUNTIME              │
│                                     │
│  Validate tool existence            │
│  Enforce authorization              │
│  Execute tools                      │
│  Handle errors                      │
└──────────────────┬──────────────────┘
                   │
                   │ authorized operation
                   ▼
┌─────────────────────────────────────┐
│               TOOLS                 │
│                                     │
│  Concrete operations                │
│  External side effects (future)     │
└─────────────────────────────────────┘
```

The LLM-generated tool request must therefore be treated as untrusted input.

This principle will become increasingly important when tools gain access to:

* files
* operating system commands
* networks
* credentials
* external APIs
* MCP servers
* other agents

---

# Basic Observability

The agent records basic execution information for each run.

The current implementation measures:

* number of iterations
* number of requested tool calls
* LLM execution time
* tool execution time
* total execution time

Example:

```text
[Agent] Run summary
[Agent] Iterations: 3
[Agent] Tool calls: 2
[Agent] LLM time: 122.565s
[Agent] Tool time: 0.002208s
[Agent] Total time: 122.567s
```

The runtime also maintains structured internal events for:

```text
llm_call
tool_call
tool_denied
tool_error
```

The observability implemented here is intentionally basic.

Advanced tracing, persistent event storage, OpenTelemetry, distributed tracing, and dashboards are outside the scope of this lab.

---

# Experiments Performed

## Experiment 1 — Direct LLM Interaction

The initial implementation connected directly to the local Ollama instance and maintained a conversation history.

This established the difference between a simple LLM client and an agent.

---

## Experiment 2 — Tool Calling

Tools were exposed to the LLM through the Ollama client.

The LLM could request operations such as:

```text
get_current_date
get_current_time
days_until_date
```

---

## Experiment 3 — Tool Registry and Dispatcher

A centralized registry and dispatcher were introduced.

This created a clear execution boundary between:

```text
LLM tool request
        ↓
Registry
        ↓
Policy
        ↓
Tool execution
```

---

## Experiment 4 — Agent Decision Loop

The agent was changed from a single LLM request into an iterative loop.

The LLM can now:

```text
request tool
    ↓
receive result
    ↓
request another tool
    ↓
receive result
    ↓
produce final answer
```

---

## Experiment 5 — Multiple Tool Calls

The agent was tested with tasks requiring multiple tool calls.

---

## Experiment 6 — Sequential Tool Calls

A dependent workflow was tested where the result of one tool became an argument to another tool.

Example:

```text
get_current_date()
        ↓
2026-09-25
        ↓
days_until_date(...)
        ↓
6
```

---

## Experiment 7 — Basic Observability

Timing and execution metrics were added to the agent loop.

This made the internal behavior of the agent visible without introducing a full tracing framework.

---

## Experiment 8 — Tool Permissions

The tool authorization layer was tested in two configurations.

### Policy A — Tool denied

```python
ALLOWED_TOOLS = {
    "get_current_date",
    "get_current_time",
}
```

The LLM requested `days_until_date`, but the runtime rejected it.

The denial was returned to the LLM, which then solved the task without executing the tool.

### Policy B — Tool allowed

```python
ALLOWED_TOOLS = {
    "get_current_date",
    "get_current_time",
    "days_until_date",
}
```

The same request resulted in:

```text
get_current_date()
        ↓
2026-09-25

days_until_date(...)
        ↓
6

final answer
```

The comparison demonstrates the effect of runtime tool authorization on agent behavior.

---

# Installation

## Requirements

* Python 3.13+
* `uv`
* Docker
* Docker Compose
* Ollama infrastructure from the project root

The shared Ollama infrastructure must be running before executing the lab.

---

## Start the Shared Infrastructure

From the project root:

```bash
cd infrastructure
docker compose up -d
```

Verify Ollama:

```bash
curl http://localhost:11434/api/tags
```

The expected model is configured through:

```text
infrastructure/.env
```

Example:

```dotenv
OLLAMA_MODEL=qwen3:8b
OLLAMA_HOST_PORT=11434
```

---

# Lab Installation

From the lab directory:

```bash
cd labs/lab01-basic-agent
```

Create the environment and install dependencies:

```bash
uv sync
```

The lab uses:

```text
ollama
python-dotenv
```

---

# Configuration

Create a `.env` file:

```dotenv
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=qwen3:8b
```

The environment variables are loaded by the Python application.

---

# Running the Lab

The interactive client can be executed with:

```bash
uv run python src/lab01_basic_agent/main.py
```

The agent experiment can be executed with:

```bash
uv run python src/lab01_basic_agent/agent_test.py
```

---

# Project Structure

```text
lab01-basic-agent/
├── .env
├── .env.example
├── .python-version
├── pyproject.toml
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
│           ├── permissions.py
│           └── registry.py
└── uv.lock
```

---

# Security Relevance

Although this is a simple laboratory, it establishes several concepts that are fundamental to AI agent security.

## 1. LLM-generated tool calls are untrusted input

The LLM decides what tool it wants to use and generates the arguments.

The runtime must therefore validate and authorize the request before execution.

---

## 2. Tool authorization must be enforced outside the model

The model should not be trusted to enforce security policy by itself.

The runtime should enforce authorization programmatically.

---

## 3. Model capabilities and tool capabilities are different

An LLM may be able to reason about an operation without having access to the corresponding tool.

For example:

```text
Tool denied
    ≠
LLM unable to answer
```

---

## 4. Tool execution creates a security boundary

As tools become more powerful, the consequences of an incorrect or malicious tool call increase.

A tool that only returns the current date has negligible impact.

A tool that executes shell commands may have access to:

* the filesystem
* environment variables
* credentials
* network resources
* operating system functionality

The same agent architecture can therefore become a significant security boundary as tool capabilities increase.

---

## 5. Tool results become part of the LLM context

The LLM receives tool results as new context.

This means that future laboratories can investigate what happens when tool output is:

* malicious
* manipulated
* misleading
* attacker-controlled
* excessively large
* designed to influence subsequent model behavior

This will become particularly relevant for MCP and other external tool protocols.

---

# Current Limitations

This laboratory deliberately keeps the implementation simple.

The current agent does not yet provide:

* structured input validation
* schema-based argument validation
* trust-level classification for tools
* persistent audit logs
* authentication
* authorization by user or identity
* sandboxing
* filesystem isolation
* network isolation
* command execution
* MCP
* Skills
* prompt-injection defenses
* tool-output sanitization
* advanced tracing
* production-grade error handling

These are intentionally deferred to later laboratories.

---

# Future Laboratory Architecture

The initial laboratory runs directly on the host because this makes development and debugging easier.

Future laboratories may introduce containerization when isolation provides a concrete security benefit.

A possible future architecture is:

```text
                        Host
                         │
              ┌──────────┴──────────┐
              │                     │
              ▼                     ▼
       Shared Ollama          Docker Network
                                    │
                         ┌──────────┴──────────┐
                         │                     │
                         ▼                     ▼
                  Agent Container       Vulnerable Target
                         │
                         ▼
                  Tools / MCP / Skills
```

The shared Ollama infrastructure remains common across laboratories.

Individual laboratories can introduce their own vulnerable targets and isolated execution environments.

---

# Future Labs

The project will progressively introduce more realistic and security-sensitive agent environments.

Potential future topics include:

```text
Lab 01 — Basic Agent
    │
    ├── LLM interaction
    ├── Tool calling
    ├── Agent loop
    ├── Tool authorization
    └── Basic observability
    │
    ▼
Lab 02 — Input Validation and Trust Boundaries
    │
    ▼
Lab 03 — Prompt Injection
    │
    ▼
Lab 04 — Filesystem Access
    │
    ▼
Lab 05 — Command Execution
    │
    ▼
Lab 06 — MCP Security
    │
    ▼
Lab 07 — Skills Security
    │
    ▼
Further Agent Security Experiments
```

The exact scope and ordering of future laboratories may evolve as the project develops.

---

# Key Takeaways

This laboratory establishes the following mental model:

```text
                         ┌─────────────┐
                         │    User     │
                         └──────┬──────┘
                                │
                                ▼
                         ┌─────────────┐
                         │     LLM     │
                         │             │
                         │ Reasoning   │
                         │ Generation  │
                         │ Tool calls  │
                         └──────┬──────┘
                                │
                         untrusted request
                                │
                                ▼
                    ┌─────────────────────┐
                    │   Agent Runtime     │
                    │                     │
                    │ Agent loop          │
                    │ Dispatcher          │
                    │ Error handling      │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │       Policy        │
                    │                     │
                    │ Authorization       │
                    └──────────┬──────────┘
                               │
                         authorized call
                               │
                               ▼
                    ┌─────────────────────┐
                    │       Tools         │
                    │                     │
                    │ Concrete operations │
                    └─────────────────────┘
```

The most important distinction is:

```text
LLM capability
    ≠
Agent Runtime capability
    ≠
Tool capability
```

The LLM can generate a request.

The Agent Runtime decides whether that request can be executed.

The Tool performs the actual operation.

This separation provides the foundation for studying attacks against AI agents in subsequent laboratories.

---

# Status

**Lab 01 — Completed**

Implemented concepts:

* Direct LLM interaction
* Conversation history
* Tool calling
* Tool registry
* Tool dispatcher
* Agent decision loop
* Multiple tool calls
* Sequential dependent tool calls
* Basic observability
* Tool permissions and capabilities
* Tool denial handling
* Separation between LLM, Agent Runtime, Policy, and Tools
