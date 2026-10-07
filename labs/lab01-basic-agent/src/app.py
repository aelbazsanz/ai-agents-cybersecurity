#!/usr/bin/env python3
"""
app.py — Interactive Agent for lab01-basic-agent

Interactive agent with real LLM integration (Ollama).

Menu commands:
  - /help    : Show help
  - /tools   : List available tools (echo, get_time, calculator)
  - /exit    : Exit the interactive session
  - User prompts: sent to Ollama, which decides whether to invoke a tool

Agent loop (full flow shown):
  1. Send user prompt + available tools to Ollama
  2. LLM decides: text response OR tool call(s)
  3. If tool call(s): LLM decision → execute tool → result back to LLM → final response
  4. Print final response to user

Session logs are saved to the logs/ folder as JSON Lines files.
Each file is named {session_id}.json and contains:
  timestamp, session_id, model, user_prompt, response, turn

Usage:
    uv run python3 -m app
    # or
    python3 app.py
"""

import json
import os
import re
import sys
import urllib.request
import urllib.error

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import uuid
from datetime import datetime, timezone

from tools import TOOLS, TOOL_HANDLERS, parse_arguments

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
# Determine the project root by going up from the src/ directory.
# __file__ points to src/app.py, so dirname() gives src/, dirname() again gives the project root.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen3:8b")
DEBUG = os.environ.get("DEBUG", "").lower() in ("1", "true", "yes")

# Log directory for session logs (at project root level: labs/lab01-basic-agent/logs/)
LOG_DIR = os.path.join(PROJECT_ROOT, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Session tracking (one file per session)
session_id: str = str(uuid.uuid4())

# Tool definitions in Ollama format
TOOLS_OLLAMA = [
    {
        "type": "function",
        "function": {
            "name": info["name"],
            "description": info.get("description", ""),
            "parameters": info.get("inputSchema", {"type": "object", "properties": {}})
        }
    }
    for info in TOOLS.values()
]


# ---------------------------------------------------------------------------
# Helpers — clean up LLM output
# ---------------------------------------------------------------------------
def _strip_thinking(text: str) -> str:
    """
    Remove qwen3 thinking/reasoning content from the model output.

    qwen3 models can return reasoning content in several formats:
    - <thinking>...</thinking> tags
    - Special tokens like <|begin_of_thinking|> / <|end_of_thinking|>
    - Bare "Thinking..." lines (older/disabled thinking modes)
    We keep only the final answer after the reasoning section.
    """
    if not text:
        return text

    # Strip <thinking>...</thinking> tags and their content
    text = re.sub(r"<thinking>.*?</thinking>", "", text, flags=re.DOTALL)

    # Strip <|begin_of_thinking|>...<|end_of_thinking|> blocks
    text = re.sub(r"<\|begin_of_thinking\|>.*?<\|end_of_thinking\|>", "", text, flags=re.DOTALL)

    # Strip leading "Thinking..." lines (bare reasoning prefix without tags)
    text = re.sub(r"^Thinking\.\.\.\n?", "", text, flags=re.MULTILINE)

    return text.strip()


# ---------------------------------------------------------------------------
# Log helpers — printed to terminal so the agent flow is visible
# ---------------------------------------------------------------------------
def format_json(obj) -> str:
    """Format a JSON object on a single line for readability."""
    return json.dumps(obj, sort_keys=True)


def log_app(text: str) -> None:
    """Print an [AGENT] log line (agent flow / decisions)."""
    print(f"\033[1;36m[AGENT]\033[0m {text}")


def log_llm(text: str) -> None:
    """Print an [LLM] log line (LLM response)."""
    print(f"\033[1;33m[LLM]\033[0m {text}")


def log_tool(text: str) -> None:
    """Print an [TOOL] log line (tool execution result)."""
    print(f"\033[1;35m[TOOL]\033[0m {text}")


# ---------------------------------------------------------------------------
# Menu
# ---------------------------------------------------------------------------
def show_help() -> None:
    """Show the application help menu."""
    print()
    log_app("=== lab01-basic-agent — Agent Help ===")
    print("  Commands:")
    print("    /help    - Show this help menu")
    print("    /tools   - List the available tools")
    print("    /exit    - Exit the interactive session")
    print()
    print("  Then type any user prompt, e.g.:")
    print("    echo Hola")
    print("    get_time")
    print("    calculator add 5 3")
    print()
    print("  The LLM will decide which tool to use based on the prompt.")
    print("  The full agent flow is shown:")
    print("    [AGENT] LLM decision -> [TOOL] execution -> [AGENT] result to LLM")
    print("    -> [LLM] final response")
    print()


def list_tools() -> None:
    """List all registered tools."""
    log_app("Registered tools:")
    for name, info in sorted(TOOLS.items()):
        print(f"  - \033[1m{name}\033[0m: {info['description']}")
    print()


# ---------------------------------------------------------------------------
# LLM
# ---------------------------------------------------------------------------
def ollama_chat(messages, tools) -> dict:
    """Call the Ollama chat API with tool definitions."""
    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "tools": tools,
        "stream": False
    }
    url = f"{OLLAMA_URL}/api/chat"
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode())


def run_tool(tool_name: str, arguments: dict) -> str:
    """Run a built-in tool with the given arguments."""
    handler = TOOL_HANDLERS.get(tool_name)
    if handler is None:
        raise ValueError(f"Tool '{tool_name}' is not available.")
    return handler(arguments)


def process_prompt(prompt: str, turn: int = 0) -> None:
    """Send user prompt to Ollama and run the full agent loop."""
    messages = [{"role": "user", "content": prompt}]

    try:
        # ---- Step 1: LLM decides what to do ----
        log_app(f"Sending prompt to LLM (model: {OLLAMA_MODEL})...")
        response = ollama_chat(messages, TOOLS_OLLAMA)
        message = response.get("message", {})

        tool_calls = message.get("tool_calls", [])
        content = message.get("content", "")

        if tool_calls:
            # ---- Step 2: show LLM decision and prepare for execution ----
            log_llm("LLM decided to invoke tool(s):")
            tool_results = []
            for tc in tool_calls:
                func = tc.get("function", {})
                tool_name = func.get("name")
                raw_arguments = func.get("arguments")
                arguments = parse_arguments(raw_arguments)
                log_llm(f"  -> tool: \033[1m{tool_name}\033[0m, arguments: {format_json(arguments)}")

                # ---- Step 3: execute tool and collect result ----
                log_tool(f"Executing {tool_name}...")
                try:
                    result = run_tool(tool_name, arguments)
                    log_tool(f"Result: {result}")
                except ValueError as e:
                    result = f"Error: {e}"
                    log_tool(f"Error: {result}")
                tool_results.append(result)

            # For tool queries, use the combined tool results as the final response
            # This matches the MCP lab style where tool execution result is shown directly
            if len(tool_results) == 1:
                complete_content = tool_results[0]
            else:
                # Multiple tools - combine results
                complete_content = "\n".join(tool_results)

            log_llm(f"Final response: {complete_content}")
            print(f"\033[1;33m{complete_content}\033[0m")
            log_interaction(turn, prompt, complete_content)

        elif content:
            log_llm("LLM response (no tool calls):")
            if DEBUG:
                print(f"\033[1;34m[DEBUG] Raw response: {format_json(response)}\033[0m")
            print(f"\033[1;33m{content}\033[0m")
            log_interaction(turn, prompt, content)
        else:
            log_llm("LLM returned empty response.")
            if DEBUG:
                print(f"\033[1;34m[DEBUG] Raw response: {format_json(response)}\033[0m")
            log_interaction(turn, prompt, "")

    except urllib.error.URLError as e:
        print(f"[ERROR] Failed to connect to Ollama at {OLLAMA_URL}: {e}")
        print("[AGENT] Make sure Ollama is running and accessible.")
        log_interaction(turn, prompt, f"[ERROR] Failed to connect to Ollama: {e}", error=f"URLError: {e}")
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        log_interaction(turn, prompt, f"[ERROR] Unexpected error: {e}", error=f"Exception: {e}")


# ---------------------------------------------------------------------------
# Session logging
# ---------------------------------------------------------------------------
def log_interaction(turn: int, user_prompt: str, response: str, error: str = None) -> None:
    """Save interaction to JSON Lines file named {session_id}.json in logs/."""
    log_entry: dict = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
        "model": OLLAMA_MODEL,
        "user_prompt": user_prompt,
        "response": response,
        "turn": turn,
    }
    if error is not None:
        log_entry["error"] = error

    log_path = os.path.join(LOG_DIR, f"{session_id}.json")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")


# ---------------------------------------------------------------------------
# Interactive loop
# ---------------------------------------------------------------------------
def run_interactive_loop() -> None:
    log_app("=== lab01-basic-agent — Basic Agent ===")
    print("  Commands: /help, /tools, /exit")
    print("  Or type a user prompt, e.g.: echo Hola")
    print("  Press Ctrl+C to quit")
    print()

    turn = 0

    while True:
        try:
            prompt = input("> ").strip()
        except EOFError:
            break

        if not prompt:
            continue

        if prompt == "/help":
            show_help()
        elif prompt == "/tools":
            list_tools()
        elif prompt == "/exit":
            log_app("Goodbye!")
            break
        else:
            turn += 1
            process_prompt(prompt, turn)
        print()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    try:
        run_interactive_loop()
    except KeyboardInterrupt:
        print("\n[AGENT] Goodbye!")
        sys.exit(0)
