# cc-orchestrator-plugin

Claude Code plugin that unifies [OpenAI Codex CLI](https://github.com/openai/codex) and [AutoAgent](https://github.com/HKUDS/AutoAgent) into a single routing layer. Describe your task and the plugin picks the optimal tool.

## What it does

- **`/dispatch <task>`** — analyzes the task and routes to the best tool automatically
- **`/auto <task>`** — runs AutoAgent's system agents (coding, web research, file analysis)
- **`/codex <task>`** — runs Codex CLI for code review and static analysis (via [cc-codex-plugin](https://github.com/thepushkarp/cc-codex-plugin))

The plugin also provides subagents (`auto-agent`, `router-agent`) that Claude can spawn autonomously when it detects a task would benefit from external analysis.

## Routing logic

| Task type | Routed to | Why |
|---|---|---|
| Code review, security audit, bug hunting | Codex | focused single-pass static analysis |
| Implementation planning, edge cases | Codex | structured analytical output |
| Multi-step coding with execution | AutoAgent | Docker-sandboxed iterative coding |
| Web research, data gathering | AutoAgent | Web Surfer agent browses the web |
| File analysis (PDF, DOCX, etc.) | AutoAgent | File Surfer agent |
| Simple/trivial | Claude | no external tool needed |

## Prerequisites

- [Codex CLI](https://github.com/openai/codex) installed and authenticated (`brew install codex && codex login`)
- [cc-codex-plugin](https://github.com/thepushkarp/cc-codex-plugin) installed as a Claude Code plugin
- [AutoAgent](https://github.com/HKUDS/AutoAgent) cloned and installed (`pip install -e .`)
- Docker Desktop (optional — use `--local` flag without it)

## Installation

```bash
# add as a marketplace source
claude plugin marketplace add zmuhls/cc-orchestrator-plugin

# install
claude plugin install cc-orchestrator-plugin@cc-orchestrator-plugin
```

## Usage

```bash
# auto-routed — plugin picks the tool
/dispatch review auth.py for SQL injection vulnerabilities
/dispatch research the latest papers on RAG architectures
/dispatch write a CSV parser in Python

# explicit Codex
/codex find bugs in sort.py

# explicit AutoAgent
/auto --local analyze the files in the current directory
/auto --agent get_coding_agent write a web scraper for product prices
```

### /auto flags

| Flag | Values | Default |
|---|---|---|
| `--model` | any model name | COMPLETION_MODEL from env |
| `--agent` | get_system_triage_agent, get_coding_agent, get_websurfer_agent, get_filesurfer_agent | get_system_triage_agent |
| `--local` | (flag) | false (auto-detects Docker) |

## Architecture

```
cc-orchestrator-plugin/
  .claude-plugin/
    plugin.json            # plugin manifest
    marketplace.json       # marketplace registration
  scripts/
    auto_oneshot.py        # non-interactive AutoAgent wrapper
  commands/
    auto.md                # /auto slash command
    dispatch.md            # /dispatch auto-routing command
  agents/
    auto-agent.md          # subagent for AutoAgent delegation
    router-agent.md        # routing agent (Codex vs AutoAgent)
  skills/
    orchestrator/
      SKILL.md             # unified guidance for both tools
```

The `auto_oneshot.py` wrapper exists because AutoAgent's CLI (`auto main`) is interactive. The wrapper extracts the environment initialization logic and runs a single query non-interactively, making it compatible with Claude Code's Bash tool.

## License

MIT
