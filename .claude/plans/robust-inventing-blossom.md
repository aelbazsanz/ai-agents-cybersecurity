# Plan: Reorganize lab01 & lab02 into a `src/` layout

## Context

The user's lab02 import error:

```
File ".../lab02-agent-goal-hijack/tools.py", line 25, in <module>
    from tools import TOOLS as LAB01_TOOLS
ImportError: cannot import name 'TOOLS' from 'tools'
(.../lab02-agent-goal-hijack/tools.py...)
```

`lab02/tools.py` tries to import lab01's `tools.py`, but since lab02 also has a local file named `tools.py`, Python's import resolution collides with the current directory's own `tools.py` during import, causing a circular/confused import.

The user proposes: **put all source `.py` files inside a `src/` folder** and execute from there. I agree — this is the better approach:

- Avoids naming collisions (e.g., `tools.py` shadowing an import target)
- Follows the conventional "src layout" (PEP 517 / `src/` package)
- Makes imports explicit: `from tools import ...` vs. `from lab01.tools import ...`
- Matches the `python3 -m app` convention cleanly

## Recommended approach

### 1. lab01-basic-agent restructure

```
labs/lab01-basic-agent/
├── src/                     # NEW: all Python source
│   ├── __init__.py          # empty (or expose app entry point)
│   ├── app.py               # previously app.py
│   └── tools.py             # previously tools.py
├── .gitignore
├── __init__.py              # kept at root for compatibility
├── logs/
├── pyproject.toml
└── README.md
```

Changes in `src/app.py`:
- Add `sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))` so `from tools import ...` resolves to `src/tools.py` (same file package).
- Keep `from tools import TOOLS, TOOL_HANDLERS, parse_arguments` — unchanged from lab01.

Keep root-level files (`app.py` entry is now `src/app.py`).

### 2. lab02-agent-goal-hijack restructure

```
labs/lab02-agent-goal-hijack/
├── src/                     # NEW
│   ├── __init__.py
│   ├── app.py               # previously app.py
│   ├── tools.py             # previously tools.py (keep extending lab01)
│   ├── hijack_detector.py   # previously hijack_detector.py
│   └── scenarios/
│       ├── challenge_01_prompt_injection.py
│       ├── challenge_02_system_prompt_leak.py
│       └── challenge_03_sensitive_file_access.py
├── .gitignore
├── __init__.py
├── logs/
├── pyproject.toml
└── README.md
```

Changes in `src/tools.py`:
- Import lab01's tools via `os.path` relative path + `sys.path.insert` (same pattern as before, now inside `src/`).
- Path to lab01 becomes: `os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'lab01-basic-agent')`.
- Avoid importing from a module named `tools` — instead import with an explicit target: `import lab01_tool_module` using `importlib` or by renaming the sys.path entry, e.g.:

```python
import os, sys
lab01_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'lab01-basic-agent')
sys.path.insert(0, lab01_path)
from tools import TOOLS as LAB01_TOOLS, parse_arguments as lab01_parse_arguments
```

Wait — this still has the same issue: importing `from tools import ...` will resolve to `src/tools.py` because cwd includes `src`? No: when running `uv run python3 -m src.app`, the cwd is the lab02 root, and `sys.path` will include the root dir, not `src`. Actually, `python3 -m` adds the *current directory* and the *package directory* to sys.path. Since we add `lab01_path` at position 0, `from tools import ...` should resolve to lab01's `tools.py` first. But the issue is that the local `src/tools.py` is being imported when `app.py` does `from tools import ...` — because the cwd might not be in sys.path when running with `python3 -m`.

Hmm, let me think about this more carefully.

When running `python3 -m src.app`:
- sys.path[0] = the package directory containing `src` (i.e., the lab02 root if cwd is lab02 root... actually sys.path[0] = cwd)
- `src` is treated as a package, its directory is added to sys.path.

Wait, when you run `python3 -m src.app`, Python adds:
1. sys.path[0] = the current working directory
2. The package path (the directory containing `src/`)

So if cwd is the lab02 root and cwd is in sys.path, then `from tools import ...` would look for `tools.py` in cwd, which doesn't exist (tools is in src/). So it would fall through to sys.path entries. Since lab01_path is inserted at position 0, it would find lab01's `tools.py`.

But when running `python3 src/app.py` directly:
- sys.path[0] = the directory containing the script = `src/`
- `from tools import ...` → finds `src/tools.py` → the current file → circular import → ERROR (same as user's error!)

So the fix: run with `python3 -m app` or `uv run python3 -m app` from the lab02 root (cwd = root, not src).

Let me verify:
- `cd lab02 && python3 -m app` — no, that requires `src` to be a package and `app` to be runnable... `python3 -m app` when cwd is lab02 root and `app.py` is inside `src/` → Python treats `src` as a package, and `app` as a module within it. This works.

Actually, the cleanest is:
- `uv run python3 -m src.app` or
- `python3 -m src.app`

Or simply `python3 -m app` from the lab02 root (since `src` is a namespace/package and `app` is inside it).

Let me reconsider: with the src layout:

```
lab02/
├── src/
│   ├── __init__.py
│   ├── app.py
│   ├── tools.py
│   └── hijack_detector.py
```

Running `python3 -m app` from lab02 root:
- Python needs to find `app` as a top-level module or package. `src.app` — since `src` is a package (`__init__.py` exists), Python will find `src/app.py`. But `python3 -m app` searches for `app` in sys.path, not `src.app`.

Hmm, actually `python3 -m app` looks for a top-level module `app`, not `src.app`. To run `src.app`, we need `python3 -m src.app`.

Alternatively, to keep the simple `python3 -m app` convenience, we can put a small `app.py` at the root that imports from `src`:

```python
# lab02/app.py (root) — thin shim
from src.app import main
if __name__ == "__main__":
    main()
```

Hmm, but app.py doesn't have a `main()` function — the entry point is `if __name__ == "__main__"`. We could wrap `run_interactive_loop()` in a `main()` function.

Actually, let me keep it simpler. The user said "execute from this folder" — meaning run from the src folder. So:

- `cd src && uv run python3 app.py` — cwd = src, sys.path[0] = src, `from tools import ...` finds src/tools.py (the local file) ✓
- For `hijack_detector.py` imports, `from tools import ...` in `hijack_detector.py` finds src/tools.py ✓

Wait, but `hijack_detector.py` doesn't import tools at all. And `app.py` does `from tools import ...` — with cwd = src, this resolves to src/tools.py ✓.

And for `src/tools.py` importing lab01's tools:
- cwd = src, so Python's default search includes cwd (src) and the current file's directory.
- Adding `lab01_path = ../lab01-basic-agent` to sys.path position 0 ensures `from tools import ...` resolves to lab01's `tools.py` ✓.

So the working command:
```
cd src && python3 app.py
```

This is simple and consistent. Let me go with this.

Actually, wait. Let me reconsider whether to run from `src` or use `python3 -m src.app`. Running `python3 -m src.app` from the root would treat `src` as a package and run `app` inside it. Both work. I'll support:

- `uv run python3 -m app` from the lab root (requires `src` package + app module importable) — hmm, `python3 -m app` won't find `src/app` unless we use `python3 -m src.app`.

Let me just support one clean command: `python3 app.py` from within `src/`. And update README to reflect this.

Actually, let me reconsider. The cleanest approach that preserves the existing convenience (`python3 app.py` from the lab root):

Option A: Keep root `app.py` as a thin shim:
```python
# lab02/app.py
from src.app import run_interactive_loop

if __name__ == "__main__":
    run_interactive_loop()
```
and root `tools.py`? No — if root has `app.py` shim importing from `src.app`, then root-level `python3 app.py` works, and `from tools import ...` in src/app resolves to src/tools.py (because cwd=root is in sys.path, and `tools` isn't in root, so it looks further... no wait, it would look in cwd first, and cwd doesn't have `tools.py`, so it skips to other sys.path entries, including lab01_path). 

Hmm, but there's a subtlety: when cwd is in sys.path (which it is by default), `from tools import X` in src/app.py searches:
1. cwd = lab02 root — no tools.py here ✓
2. other sys.path entries — lab01_path has tools.py ✓

So it works: lab02/app.py imports from src/app, and src/app.py's `from tools import ...` resolves to src/tools.py (since src is also on sys.path when running `python3 app.py`? No — cwd is in sys.path, not src. But `tools` doesn't exist in cwd, so it continues... 

Wait, no. When running `python3 app.py` from lab02 root with cwd in sys.path:
- src/app.py does `from tools import ...`
- Python searches cwd (lab02 root) for `tools` — not found
- Python searches next sys.path entries — including lab01_path — finds lab01's `tools.py`! ✗ WRONG — it should find src/tools.py.

So this doesn't work because cwd isn't on the list before lab01_path... actually the order matters. sys.path insertion with insert(0, lab01_path) puts lab01 at position 0, ahead of cwd. So `from tools import ...` would resolve to lab01 first.

OK so the root-shim approach is tricky. Let me just go with **Option B: run from src/**.

Command:
```
cd labs/lab02-agent-goal-hijack/src
python3 app.py
```

And for lab01:
```
cd labs/lab01-basic-agent/src
python3 app.py
```

This matches the user's request ("execute from this folder") and avoids all import ambiguity. The README for each lab gets updated accordingly.

### 3. Implementation steps

**lab01:**
1. `mkdir src`
2. Move `app.py` → `src/app.py`, `tools.py` → `src/tools.py`
3. Ensure `src/__init__.py` exists (empty)
4. Update `src/app.py`: add `sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))` — actually NOT needed if running from src/ (cwd = src, which is on sys.path). But it doesn't hurt to add it for robustness? No — adding cwd... let me think. If running from src/, cwd = src. `from tools import ...` finds src/tools.py directly. No path change needed. But to be safe if someone runs from elsewhere... The command is `cd src && python3 app.py`, so cwd = src always.

**lab02:**
1. `mkdir src`
2. Move `app.py`, `tools.py`, `hijack_detector.py` → `src/`
3. Move `scenarios/` → `src/scenarios/`
4. `src/__init__.py` (empty)
5. Update `src/tools.py` import of lab01:
   ```python
   lab01_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'lab01-basic-agent')
   sys.path.insert(0, lab01_path)
   from tools import TOOLS as LAB01_TOOLS, parse_arguments as lab01_parse_arguments
   ```
   Since cwd = src (which is on sys.path), `from tools import ...` resolves to src/tools.py first. But we want LAB01_TOOLS from lab01. Because lab01_path is at sys.path[0], it should find lab01's tools.py first... 

   Wait, no! When cwd = src and sys.path[0] = src (because script dir or cwd is added), then `from tools import ...`:
   1. Check src/ for tools.py → found! (the local file, circular) ✗

   So the local `from tools import LAB01_TOOLS as LAB01_TOOLS` — no wait, we're doing `from tools import TOOLS as LAB01_TOOLS`. Python finds the first `tools.py` on sys.path, which is src/tools.py (cwd). That's the circular import that caused the user's error!

   Hmm. So even with the src layout, if cwd is src and the script is src/tools.py, `from tools import ...` will resolve to itself.

   Wait, actually no. The user's error happened when running `uv run app.py` from the lab02 root. Let me check what sys.path looked like then.

   When running `python3 app.py` from lab02 root:
   - sys.path[0] = cwd = lab02 root
   - `app.py` → imports `from tools import TOOLS, TOOL_HANDLERS, parse_arguments` → finds lab02's `tools.py` (cwd) ✓ good, this is the local file
   - `tools.py` line 25: `from tools import TOOLS as LAB01_TOOLS` → Python finds tools.py in cwd (lab02 root) — which is itself → circular import → error!

   So the root cause is the local `from tools import ...` inside src/tools.py (or tools.py at root).

   With the src layout, when running `cd src && python3 app.py`:
   - sys.path[0] = src
   - `app.py` → `from tools import ...` → finds src/tools.py ✓
   - `tools.py` line 25: `from tools import TOOLS as LAB01_TOOLS` → finds src/tools.py (itself) → circular!

   Same problem! So we MUST avoid `from tools import ...` inside tools.py.

   The fix: use `importlib` to dynamically load lab01's tools.py, or use `exec`, or add lab01_path to sys.path BEFORE running, or use a fully-qualified name.

   Actually, the cleanest fix: change sys.path.insert(0, lab01_path) to insert lab01_path at position 0. Then:
   - sys.path = [lab01_path, src, cwd, ...]
   - `from tools import ...` finds lab01's tools.py first (position 0) ✗ — we want src's tools.py for the local tools!

   Hmm, so position matters. The issue is that `from tools import` inside src/tools.py will always find the first `tools.py` on sys.path.

   Options:
   1. Use `importlib.import_module` with a file path.
   2. Rename lab01's tools.py import to a different target name and avoid the name `tools`.
   3. Use `importlib.util.spec_from_file_location` to load the file directly.

   Option 3 is the most robust:
   ```python
   import importlib.util, os, sys
   lab01_tools_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'lab01-basic-agent', 'tools.py')
   spec = importlib.util.spec_from_file_location("lab01_tools", lab01_tools_path)
   lab01_tools = importlib.util.module_from_spec(spec)
   sys.modules["lab01_tools"] = lab01_tools
   spec.loader.exec_module(lab01_tools)
   LAB01_TOOLS = lab01_tools.TOOLS
   lab01_parse_arguments = lab01_tools.parse_arguments
   ```

   This avoids name collisions entirely. 

   Alternatively, use `importlib.util.module_from_spec` without sys.modules, but we need sys.modules for caching.

   Actually, even simpler: since we're already importing from `tools` (local src/tools.py) for the local stuff, we can just load lab01 with a distinct module name via importlib.

   Let me use this approach in `src/tools.py`.

### 4. Verification

After restructuring:
- `cd lab01/src && python3 app.py` → should print the help banner.
- Test: `echo "Hi, Angel!"`, `calculator add 5 3`, `/tools`, `/exit`.
- `cd lab02/src && python3 app.py` → should work with all 6 tools (3 from lab01 + 3 new).
- Test hijack detection: run scenario prompt.

Let me write this plan.
