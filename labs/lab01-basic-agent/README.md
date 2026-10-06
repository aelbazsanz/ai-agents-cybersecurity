# lab01-basic-agent — Basic Agent

This lab demonstrates the basic agent architecture and workflow with real LLM integration (Ollama):

- An **interactive agent** (`app.py`) that sends user prompts to the local LLM with a list of available tools
- The LLM (Ollama, e.g. `qwen3:8b`) decides whether to answer directly or invoke a tool
- The full agent flow is shown in real time: LLM decision → tool execution → tool result sent back to LLM → LLM final response
- Three built-in sample tools (`echo`, `get_time`, `calculator`)
- Session logs saved to `logs/` as JSON Lines files

## Structure

```
labs/lab01-basic-agent/
├── app.py                     # Interactive agent (menu + agent loop + logging)
├── tools.py                   # 3 built-in sample tools
├── logs/                      # Session logs (auto-generated, not in git)
│   └── {session_id}.json      # JSON Lines file per session
├── pyproject.toml             # uv project config
└── README.md                  # This file
```

## Session Logging

Each interactive session is logged to a JSON Lines file in the `logs/` folder.

- **Filename**: `{session_id}.json` (UUID generated per session)
- **Format**: JSON Lines (one JSON object per line)
- **Fields per entry**:
  - `timestamp`: ISO 8601 UTC timestamp
  - `session_id`: Unique session identifier
  - `model`: LLM model used (e.g. `qwen3:8b`)
  - `user_prompt`: The user's input prompt
  - `response`: Final LLM response (or tool execution result)
  - `turn`: Turn number within the session

> **Note**: The `logs/` folder is in `.gitignore` — session logs are never committed to git.

## Commands

| Command | Description |
|---------|-------------|
| `/help` | Show this help menu |
| `/tools` | List the available tools |
| `/exit` | Exit the interactive session |
| `echo Hola` | User prompt — LLM decides which tool to use |
| `get_time` | User prompt — LLM decides which tool to use |
| `calculator add 5 3` | User prompt — LLM decides which tool to use |

## Tools

| Tool | Description |
|------|-------------|
| `echo` | Echo the provided message at the screen |
| `get_time` | Get the current UTC date and time |
| `calculator` | Perform a basic arithmetic operation: add, subtract, multiply, divide |

## Quick Start

```bash
cd labs/lab01-basic-agent

# Main command — runs the interactive agent
uv run python3 -m app

# Or run directly with python3
python3 app.py
```

Make sure the shared infrastructure (Ollama) is running first:

```bash
cd ../infrastructure
docker compose up -d
curl http://localhost:11434/api/tags
```

The LLM model is configured through environment variables (`OLLAMA_URL`, `OLLAMA_MODEL`) and read from the project-wide `.env` via `OLLAMA_MODEL`.

## qwen3 Thinking Mode

The default model (`qwen3:8b`) is a reasoning model that can return thinking/reasoning content in addition to the final answer. The agent handles this transparently:

- **Tagged thinking** — `<thinking>...</thinking>` tags are stripped from the final response
- **Separate thinking field** — If the model returns a `thinking` field, it is used as a fallback when `content` is empty
- **Bare reasoning** — Leading `Thinking...` lines are also stripped

This ensures only the final answer is shown to the user, regardless of how the model formats its reasoning.

### Debug Mode

Enable debug output to see the raw Ollama response structure:

```bash
DEBUG=1 uv run python3 -m app
```

This shows the raw message JSON, including any `thinking` fields, which is useful when troubleshooting model-specific behavior.

## Agent Flow

1. **User prompt** — The user types a prompt (or a tool name).
2. **LLM decision** — The prompt + tool definitions are sent to Ollama. The LLM decides whether to answer directly or call a tool (`[AGENT] LLM decided to invoke tool(s)`).
3. **Tool execution** — The agent executes the tool with the LLM's arguments and prints the result (`[TOOL] Result`).
4. **Final response** — The tool result is used directly as the final response (`[LLM] Final response`).

If the LLM answers directly (no tool call), the answer is printed immediately.

## Interactive Session Example

```
[AGENT] === lab01-basic-agent — Basic Agent ===
  Commands: /help, /tools, /exit
  Or type a user prompt, e.g.: echo Hola
  Press Ctrl+C to quit

> /tools
[AGENT] Registered tools:
  - calculator: Perform a basic arithmetic operation: add, subtract, multiply, divide.
  - echo: Echo the provided message at the screen. Useful to check that the agent is working.
  - get_time: Get the current UTC date and time.

> echo Hola
[AGENT] Sending prompt to LLM (model: qwen3:8b)...
[LLM] LLM decided to invoke tool(s):
  -> tool: echo, arguments: {"message": "Hola"}
[TOOL] Executing echo...
[TOOL] Result: Echo: Hola
[LLM] Final response: Echo: Hola

> calculator add 5 3
[AGENT] Sending prompt to LLM (model: qwen3:8b)...
[LLM] LLM decided to invoke tool(s):
  -> tool: calculator, arguments: {"operation": "add", "a": 5, "b": 3}
[TOOL] Executing calculator...
[TOOL] Result: Result: 5 + 3 = 8
[LLM] Final response: Result: 5 + 3 = 8

> get_time
[AGENT] Sending prompt to LLM (model: qwen3:8b)...
[LLM] LLM decided to invoke tool(s):
  -> tool: get_time, arguments: {}
[TOOL] Executing get_time...
[TOOL] Result: Current UTC time: 2026-10-06T12:00:00+00:00
[LLM] Final response: Current UTC time: 2026-10-06T12:00:00+00:00

> What is the capital of France?
[AGENT] Sending prompt to LLM (model: qwen3:8b)...
[LLM] LLM response (no tool calls):
The question about the capital of France cannot be answered using the provided tools, which are limited to echoing messages, retrieving the current time, and performing arithmetic calculations. You may need to consult a general knowledge database or resource for this information.

> /exit
[AGENT] Goodbye!
```

> What is the capital of France?
[AGENT] Sending prompt to LLM (model: qwen3:8b)...
[LLM] LLM response (no tool calls):
The capital of France is Paris.

> /exit
[AGENT] Goodbye!
```

## What Happens Behind the Scenes

When the LLM decides to use a tool, the request to Ollama includes the tool definitions:

```json
POST http://localhost:11434/api/chat
{
  "model": "qwen3:8b",
  "messages": [{"role": "user", "content": "echo Hola"}],
  "tools": [
    {"type": "function", "function": {"name": "echo", "description": "...", "parameters": {...}}},
    {"type": "function", "function": {"name": "get_time", ...}},
    {"type": "function", "function": {"name": "calculator", ...}}
  ],
  "stream": false
}
```

If the LLM decides to call a tool, the agent then:

1. Executes the tool locally (`app.py` → `tools.py`).
2. Uses the tool result directly as the final response.

## What You Learn

1. **Agent Architecture** — The loop: user prompt → LLM decision → tool execution → result back to LLM → final response.
2. **Tool Calling** — How the LLM receives tool definitions and decides which tool to invoke based on the prompt.
3. **Agent Flow Visualization** — `[AGENT]`, `[LLM]`, `[TOOL]` prefixes show the full decision and execution flow in real time.
4. **Session Logging** — JSON Lines logs capture each turn for later security analysis and review.
5. **Three Sample Tools** — `echo`, `get_time`, `calculator` — the building blocks that will be reused in later labs to investigate vulnerabilities and map them to OWASP Top 10 Agentic AI and MITRE ATLAS.

## Next Steps

This lab establishes the basic agent architecture and flow. Later labs will:

- **lab02**: Investigate prompt injection vulnerabilities in agent tools
- **lab03**: Explore tool abuse, unauthorized tool access, and MITRE ATT&CK mapping
- **lab04+**: OWASP Top 10 Agentic AI — tool poisoning, data extraction, malicious tools