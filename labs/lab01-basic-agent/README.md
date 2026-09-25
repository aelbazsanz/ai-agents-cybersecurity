# Lab 01 — Basic AI Agent

## Objective

Build a minimal AI agent from scratch using a local open-source LLM served through Ollama.

The goal of this lab is to understand the fundamental components of an AI agent before introducing higher-level frameworks such as LangChain or LangGraph.

The implementation is intentionally simple and explicit so that the agent's decision-making process, tool execution, and control flow remain visible.

---

## Learning Goals

By completing this lab, you will understand:

* How to interact with a local LLM.
* How to maintain conversational context.
* How LLMs can request tool execution.
* How an application exposes tools to an LLM.
* How to implement a tool registry and dispatcher.
* How to build a basic agent loop.
* How an agent can execute multiple tools.
* The difference between multiple tool calls and sequential multi-step tasks.
* The difference between an LLM, a conversational application, and an AI agent.
* Why the application, rather than the LLM, must control tool execution.
* Why tool execution represents an important security boundary.

These concepts will be used in later labs focused on cybersecurity and agent security.

---

## Architecture

The lab evolves incrementally.

### Initial architecture

```text
User
 ↓
Application
 ↓
LLM
 ↓
Response
```

This is an LLM-powered application, but it is not yet a complete agent.

### Tool calling

The next step introduces tools:

```text
User
 ↓
Application
 ↓
LLM
 ↓
Tool call
 ↓
Tool
 ↓
Tool result
 ↓
LLM
 ↓
Final response
```

### Current architecture

The lab now implements a basic agent loop:

```text
                    ┌───────────────┐
                    │      LLM      │
                    └───────┬───────┘
                            │
                       Tool call?
                       /       \
                     No         Yes
                     │           │
                     │      ┌────▼─────┐
                     │      │ Dispatcher│
                     │      └────┬─────┘
                     │           │
                     │         Tool
                     │           │
                     │      Tool result
                     │           │
                     │      ┌────▼─────┐
                     │      │    LLM    │
                     │      └────┬─────┘
                     │           │
                     └───────────┘
```

The loop continues until the LLM produces a final response or the maximum number of iterations is reached.

The agent can also process multiple tool calls returned by the LLM in the same response.

---

## Current State

The lab currently implements:

* Local LLM interaction through Ollama.
* Interactive conversation with message history.
* Tool definitions using Python functions.
* Tool calling through the Ollama API.
* A generic tool registry.
* A tool dispatcher.
* A basic agent loop.
* Multiple tool execution.
* A maximum iteration limit to prevent unbounded execution.
* Configuration through environment variables.

The current tools are intentionally harmless:

```text
get_current_date()
get_current_time()
```

Both operate using UTC.

---

## Important Concept: LLM vs Agent

An LLM by itself generates responses based on the input it receives.

A conversational application adds state and sends previous messages back to the model.

A tool-enabled application allows the model to request actions.

An agent introduces a control loop in which the model can repeatedly:

1. Observe the current state.
2. Decide whether it needs a tool.
3. Request a tool.
4. Receive the tool result.
5. Continue reasoning.
6. Produce a final response.

This distinction is important for cybersecurity.

An LLM does not inherently execute operating-system commands, access files, scan networks, or make HTTP requests.

Those capabilities are provided by the surrounding application.

Therefore, the application is responsible for deciding:

* Which tools exist.
* Which tools can be executed.
* Which arguments are accepted.
* Whether a tool call is authorized.
* How tool results are returned to the model.
* How many actions the agent can perform.

This boundary becomes increasingly important in later cybersecurity labs.

---

## Tool Registry and Dispatcher

The tool registry is implemented in:

```text
src/lab01_basic_agent/tools/registry.py
```

It maps tool names to Python functions:

```python
TOOLS = {
    "get_current_date": get_current_date,
    "get_current_time": get_current_time,
}
```

The dispatcher receives the name and arguments requested by the LLM:

```python
execute_tool(name, arguments)
```

and resolves the request against the registry.

Conceptually:

```text
LLM
 │
 │ tool name + arguments
 ▼
Registry
 │
 │ resolve tool
 ▼
Python function
 │
 │ result
 ▼
Dispatcher
 │
 ▼
LLM
```

This creates an explicit boundary between the model's request and actual tool execution.

---

## Agent Loop

The agent implementation is located in:

```text
src/lab01_basic_agent/agent.py
```

The core loop is intentionally implemented without an agent framework.

At a high level:

```python
while iterations < max_iterations:

    response = llm(...)

    if no_tool_call:
        return final_response

    execute_requested_tools()

    add_tool_results_to_conversation()
```

A maximum iteration count is used to prevent an agent from entering an uncontrolled loop.

The current default is:

```text
5 iterations
```

This is a basic safety mechanism rather than a complete authorization system.

---

## Configuration

The lab uses environment variables for configuration.

Create a `.env` file:

```dotenv
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=qwen3:8b
```

The `.env` file is intentionally excluded from Git.

A template is provided as:

```text
.env.example
```

---

## Requirements

* Python 3.13+
* `uv`
* Docker
* Docker Compose
* Ollama infrastructure running locally
* An Ollama-compatible model

The shared Ollama instance is provided by the project's infrastructure layer.

---

## Installation

From the lab directory:

```bash
uv sync
```

If the dependencies have not been initialized yet:

```bash
uv init
uv add ollama python-dotenv
```

---

## Running the Lab

### Interactive application

Run:

```bash
uv run python src/lab01_basic_agent/main.py
```

The application maintains conversation history with the LLM.

### Agent test

The current agent loop can be tested with:

```bash
uv run python src/lab01_basic_agent/agent_test.py
```

A typical multi-tool execution looks like:

```text
[Agent] Tool requested: get_current_date
[Agent] Arguments: {}
[Agent] Tool result: 2026-09-25

[Agent] Tool requested: get_current_time
[Agent] Arguments: {}
[Agent] Tool result: 2026-09-25T08:32:22.226836+00:00

Final answer:
Today's UTC date is 2026-09-25, and the current UTC time is ...
```

The exact wording of the final response depends on the LLM.

---

## Project Structure

```text
lab01-basic-agent/
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
│           └── registry.py
└── uv.lock
```

### Main components

**`main.py`**

Interactive LLM application.

**`agent.py`**

Basic agent implementation containing the agent loop.

**`agent_test.py`**

Small executable test for the agent loop.

**`tools/basic.py`**

Contains the implementations of the available tools.

**`tools/registry.py`**

Contains the tool registry and dispatcher.

**`pyproject.toml`**

Python project configuration and dependencies.

**`uv.lock`**

Locked dependency versions for reproducible environments.

---

## Experiments

### Experiment 1 — Direct LLM Interaction

The first version of the lab connected directly to Ollama and sent user messages to the model.

This demonstrated basic LLM interaction.

---

### Experiment 2 — Interactive Conversation

Conversation history was introduced by maintaining a list of messages:

```text
User
Assistant
User
Assistant
...
```

This demonstrated how applications provide conversational context to an LLM.

---

### Experiment 3 — Tool Calling

A `get_current_time()` tool was exposed to the model.

The model could generate a structured tool call:

```text
get_current_time({})
```

The application then executed the function and returned its result to the model.

This demonstrated the distinction between:

```text
LLM requests an action
```

and:

```text
Application executes an action
```

---

### Experiment 4 — Tool Registry and Dispatcher

The tool was moved behind a generic registry:

```text
Tool name
    ↓
Registry
    ↓
Python function
```

The dispatcher allows the application to resolve and execute tools dynamically.

This removes tool-specific logic from the agent loop.

---

### Experiment 5 — Agent Loop

The final step introduced a reusable agent loop.

The agent can:

1. Send the conversation to the LLM.
2. Inspect the response for tool calls.
3. Resolve requested tools through the registry.
4. Execute the tools.
5. Add tool results to the conversation.
6. Send the updated conversation back to the LLM.
7. Repeat until a final response is produced.

This is the first point in the lab where the application behaves as a basic AI agent rather than simply being an LLM wrapper.

---

### Experiment 6 — Multiple Tool Calls

A second tool, `get_current_date()`, was introduced alongside `get_current_time()`.

The test asks:

```text
Tell me today's UTC date and current UTC time.
```

The LLM returned two tool calls in the same response:

```text
get_current_date()
get_current_time()
```

The agent loop processed both calls:

```text
LLM
 ├── get_current_date()
 │       ↓
 │   2026-09-25
 │
 └── get_current_time()
         ↓
     2026-09-25T08:32:22...
         ↓
        LLM
         ↓
    Final response
```

This demonstrates that the agent is not limited to a single tool call per LLM response.

The implementation handles this through:

```python
for tool_call in response.message.tool_calls:
```

Each requested tool is resolved through the registry and executed by the dispatcher.

---

## Multiple Tool Calls vs Sequential Multi-step Tasks

These two concepts are related but not identical.

### Multiple tool calls

In the current experiment, the LLM requested both tools in the same response:

```text
LLM
 ├── Tool A
 └── Tool B
 ↓
LLM
 ↓
Final response
```

The tools are independent and their results do not determine which tool is requested next.

### Sequential multi-step task

A more advanced agent interaction would look like:

```text
LLM
 ↓
Tool A
 ↓
Tool A result
 ↓
LLM
 ↓
Tool B
 ↓
Tool B result
 ↓
LLM
 ↓
Final response
```

In this scenario, the result of the first tool becomes part of the agent's state and can influence the next decision made by the LLM.

This will be the next stage of the multi-step task experiment.

---

## Security Relevance

The architecture introduced in this lab establishes several security boundaries that will become important in later experiments.

### Tool execution

The LLM can request a tool, but the application executes it.

This distinction is fundamental.

A malicious or manipulated model output should not automatically translate into arbitrary system actions.

---

### Tool authorization

The current implementation does not yet provide fine-grained authorization.

Future implementations can introduce:

* Tool allowlists.
* Argument validation.
* User approval.
* Permission levels.
* Sandboxing.
* Execution timeouts.
* Resource limits.
* Audit logs.

---

### Excessive agency

Giving an agent access to powerful tools increases the potential impact of an incorrect or manipulated decision.

Examples of future tools could include:

```text
read_file
execute_command
send_http_request
scan_network
query_database
```

These capabilities will be introduced only in isolated environments as the project progresses.

---

### Prompt Injection

A later lab will investigate how untrusted input can influence an agent into requesting unintended actions.

The relevant attack chain is:

```text
Untrusted input
      ↓
Prompt injection
      ↓
LLM decision
      ↓
Tool call
      ↓
Application action
```

Understanding this chain is one of the main reasons this lab avoids hiding the agent logic behind a framework.

---

### Tool Security

Future labs will also investigate threats such as:

* Malicious tools.
* Compromised tools.
* Tool description manipulation.
* Unsafe tool arguments.
* Tool result manipulation.
* Excessive permissions.
* MCP-related attacks.
* Skill-related attacks.

---

## Roadmap

The current progression is:

```text
1. Direct LLM interaction        — completed
2. Interactive conversation      — completed
3. Tool calling                  — completed
4. Tool registry/dispatcher      — completed
5. Agent decision loop           — completed
6. Multiple tool calls           — completed
7. Sequential multi-step tasks   — next
8. Observability                 — planned
9. Cybersecurity-oriented tools  — planned
10. Security testing of agent    — planned
```

The next step will introduce a task where the result of one tool call becomes relevant to the agent's next decision.

---

## Key Takeaways

At the end of the current stage:

* An LLM generates text and can request structured tool calls.
* The surrounding application controls actual tool execution.
* A tool registry provides a controlled interface between the LLM and application capabilities.
* A dispatcher resolves tool requests to concrete functions.
* An agent loop allows repeated model/tool interactions.
* An agent can process multiple tool calls returned in the same LLM response.
* Multiple tool calls are not necessarily the same as a sequential multi-step task.
* Maximum iteration limits provide a basic control against unbounded execution.
* Tool access creates a security boundary that must be explicitly designed.

The next experiment will investigate true sequential multi-step behavior, where the result of one tool execution becomes relevant to the next agent decision.
