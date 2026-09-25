# Lab 01 — Basic AI Agent

## Objective

Build a minimal AI application that interacts with a local Large Language Model (LLM) through Ollama.

The laboratory starts with direct LLM interaction and progressively evolves toward an actual AI agent. The goal is to understand the underlying mechanisms before introducing agent frameworks such as LangGraph or LangChain.

## Learning Goals

This lab introduces:

* Local LLM interaction
* Ollama as an LLM runtime
* Python-based LLM clients
* Configuration through environment variables
* Multi-turn conversations
* Conversation history
* Tool calling
* Tool execution and dispatch
* The difference between an LLM, a conversational application, and an AI agent

The lab deliberately avoids agent frameworks at this stage.

---

## Architecture

The laboratory evolves incrementally.

### Initial architecture

```text
User
  │
  ▼
Python application
  │
  ▼
Ollama Client
  │
  ▼
Ollama
  │
  ▼
Qwen 3 8B
  │
  ▼
Response
```

### Current architecture

After introducing tool calling:

```text
                         ┌─────────────────┐
                         │      Qwen       │
                         │                 │
User ──────────────────►│  Decide whether │
                         │  to use a tool  │
                         └────────┬────────┘
                                  │
                             tool_call
                                  │
                                  ▼
                         ┌─────────────────┐
                         │     Python      │
                         │    dispatcher   │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │ get_current_    │
                         │ time()          │
                         └────────┬────────┘
                                  │
                             tool result
                                  │
                                  ▼
                         ┌─────────────────┐
                         │      Qwen       │
                         │                 │
                         │ final response  │
                         └─────────────────┘
```

---

## Current State

The laboratory currently supports:

* Interactive multi-turn conversations
* Conversation history
* LLM tool calling
* Tool dispatch
* Tool execution
* Returning tool results to the LLM
* Final responses generated using tool results

The first tool implemented is:

```python
def get_current_time() -> str:
    """Return the current UTC time."""
```

The model can request this tool when appropriate.

---

## Important Concept: LLM vs Agent

It is important to distinguish the different layers being built in this laboratory.

### LLM

An LLM receives context and generates a response:

```text
Prompt
  │
  ▼
LLM
  │
  ▼
Response
```

### Conversational application

The application adds conversation state:

```text
User
  │
  ▼
Application
  │
  ├── Conversation history
  │
  ▼
LLM
  │
  ▼
Response
```

### Tool-enabled application

The application can expose external capabilities to the model:

```text
User
  │
  ▼
Application
  │
  ▼
LLM
  │
  ├── Tool call
  │
  ▼
Application
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
Response
```

### AI Agent

The next stage will turn this mechanism into a reusable agent loop capable of repeatedly deciding whether an action is required:

```text
User
  │
  ▼
Agent
  │
  ▼
LLM
  │
  ▼
Decision
  │
  ├──────────────► Tool
  │                  │
  │                  ▼
  │              Tool result
  │                  │
  └──────────────────┘
           │
           ▼
          LLM
           │
           ▼
      Final answer
```

---

## Configuration

The application reads its configuration from `.env`.

Example:

```dotenv
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=qwen3:8b
```

The model and Ollama host are intentionally configurable rather than hardcoded into the application.

A template is provided in:

```text
.env.example
```

The real `.env` file is excluded from Git.

---

## Requirements

The laboratory uses:

* Python 3.13+
* uv
* Ollama
* An Ollama-compatible LLM
* The Python `ollama` package
* `python-dotenv`

The shared Ollama infrastructure is provided by the project's infrastructure directory:

```text
infrastructure/
```

---

## Installation

From the laboratory directory:

```bash
cd labs/lab01-basic-agent
```

Install dependencies:

```bash
uv sync
```

Create the local environment configuration:

```bash
cp .env.example .env
```

Adjust the values if necessary.

---

## Running the Lab

Start the shared Ollama infrastructure from the project root:

```bash
cd infrastructure
docker compose up -d
```

Then return to the lab:

```bash
cd ../labs/lab01-basic-agent
```

Run the interactive application:

```bash
uv run python src/lab01_basic_agent/main.py
```

The application starts an interactive conversation:

```text
Connecting to Ollama at: http://localhost:11434
Using model: qwen3:8b

Type 'exit' to quit.

You:
```

Enter `exit` to terminate the application.

---

## Project Structure

```text
lab01-basic-agent/
├── .env.example
├── .python-version
├── README.md
├── pyproject.toml
├── uv.lock
└── src/
    └── lab01_basic_agent/
        ├── __init__.py
        ├── main.py
        ├── tool_call_test.py
        └── tools/
            ├── __init__.py
            └── basic.py
```

The local `.env` and `.venv/` directories are intentionally excluded from Git.

---

## Experiments

### Experiment 1 — Direct LLM Interaction

The first version of the application sent a hardcoded prompt to the model.

```text
Python
  │
  ▼
Ollama
  │
  ▼
LLM
  │
  ▼
Response
```

This established basic connectivity between Python and the local LLM.

---

### Experiment 2 — Interactive Conversation

The second version introduced an interactive input loop.

```text
You: What is an AI agent?

Agent: ...

You: How is it different from a normal LLM?

Agent: ...

You: What did I ask you in my first question?

Agent: ...
```

Conversation history is maintained by the application:

```python
messages = []
```

Both user and assistant messages are added to this list and sent back to the model on subsequent requests.

This allows the model to use previous turns as conversational context.

---

### Experiment 3 — Tool Calling

The third stage introduced the first external capability available to the LLM.

A simple Python function was implemented:

```python
def get_current_time() -> str:
    """Return the current UTC time."""
    ...
```

The function is exposed to the model through Ollama's tool calling interface.

The model does not execute the function directly. Instead, it produces a structured tool call:

```text
ToolCall(
    function=Function(
        name="get_current_time",
        arguments={}
    )
)
```

The Python application then acts as the tool dispatcher.

```text
User
  │
  ▼
LLM
  │
  │ tool call
  ▼
Python dispatcher
  │
  ▼
get_current_time()
  │
  │ tool result
  ▼
LLM
  │
  ▼
Final response
```

The current dispatcher explicitly maps the requested tool name to a Python function:

```python
if tool_name == "get_current_time":
    tool_result = get_current_time()
```

This establishes an important security boundary:

> The LLM can request an action, but the application controls whether and how that action is executed.

---

## Security Relevance

This separation between model decision-making and tool execution is fundamental for agent security.

A model may eventually request tools such as:

```text
execute_command
read_file
scan_network
send_http_request
```

The application should not automatically assume that every requested action is safe.

Future stages will explore:

* Tool authorization
* Input validation
* Tool isolation
* Excessive agency
* Prompt injection leading to tool abuse
* Malicious or compromised tools
* MCP tool security

The current `get_current_time` tool is intentionally harmless and does not provide access to the network, filesystem, shell, or other external systems.

---

## Roadmap

The laboratory evolves incrementally:

1. **Direct LLM interaction** — completed
2. **Interactive conversation** — completed
3. **Tool calling** — completed
4. **Agent decision loop** — next
5. **Multi-step tasks**
6. **Observability**
7. **Cybersecurity-oriented tools**
8. **Security testing of the agent**

The exact scope may evolve as the project progresses.

---

## Key Takeaways

After the current stage:

1. An LLM is not automatically an agent.
2. Conversation history is application state.
3. The Python application controls what context is sent to the model.
4. The model can request a tool without executing it directly.
5. The application controls tool execution.
6. Tool execution creates a security boundary between model output and external actions.
7. Tool calling is one of the fundamental building blocks of an AI agent.

The next implementation step is to replace the isolated tool-calling experiment with a reusable agent decision loop.
