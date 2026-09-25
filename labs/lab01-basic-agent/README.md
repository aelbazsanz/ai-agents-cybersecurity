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
* The difference between an LLM, a conversational application, and an AI agent

The lab deliberately avoids agent frameworks at this stage.

---

## Architecture

The current implementation is intentionally simple:

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
  │
  └──────────────► Conversation history
```

The conversation history is maintained by the Python application and sent to Ollama with each request.

---

## Current State

The lab currently supports interactive multi-turn conversations.

Example:

```text
You: What is an AI agent?

Agent: ...

You: How is it different from a normal LLM?

Agent: ...

You: What did I ask you in my first question?

Agent: Your first question was "What is an AI agent?"
```

The application keeps both user and assistant messages in an in-memory list:

```python
messages = []
```

User messages are added to the conversation:

```python
messages.append(
    {
        "role": "user",
        "content": user_input,
    }
)
```

Assistant responses are also added:

```python
messages.append(
    {
        "role": "assistant",
        "content": assistant_message,
    }
)
```

The complete conversation is then sent to the model on each request.

---

## Important Concept: This Is Not Yet an Agent

Although the application currently displays the name `Agent`, it is important to distinguish the concepts.

### LLM

An LLM receives a context and generates a response:

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

Our current application adds conversation state:

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

### AI Agent

A real agent will introduce decision-making and actions:

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

The next stages of this laboratory will progressively implement these capabilities.

---

## Configuration

The application reads its configuration from `.env`.

Example:

```dotenv
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=qwen3:8b
```

The model is intentionally configurable rather than hardcoded into the application.

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

Run the application:

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
└──
```
