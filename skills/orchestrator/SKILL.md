---
name: orchestrator
description: Unified guidance for using Codex CLI and AutoAgent together. Use when the user mentions codex, autoagent, dispatch, asks which tool to use for analysis, or when Claude detects a task matching either tool's strengths — code review, security audits, multi-step coding, web research, or file analysis.
allowed-tools: Bash
---

# Orchestrator — Codex + AutoAgent Integration

You have two complementary external analysis tools available. Each has distinct strengths. This skill guides when and how to use them.

## Tool Comparison

| Dimension | Codex CLI | AutoAgent |
|---|---|---|
| **Invocation** | `codex exec` or `/codex` | `auto_oneshot.py` or `/auto` |
| **Model** | gpt-5.4 (default) | COMPLETION_MODEL (default: claude-3-5-sonnet) |
| **Execution** | Single-pass, non-interactive | Multi-turn, agent orchestration |
| **Environment** | Read-only sandbox (default) | Docker sandbox or local |
| **Best for** | Static analysis, code review | Dynamic tasks, research, coding |
| **Speed** | Fast (single LLM call) | Slower (multi-agent, imports) |
| **Risk** | Low (read-only default) | Moderate (can execute code) |

## When to Use Codex

Codex excels at focused, single-pass analytical tasks:

- **Code review** — security audits, bug hunting, quality checks
- **Planning** — implementation plans, edge case analysis
- **Static analysis** — finding patterns, reviewing logic

**Invoke via:**
- `/codex <task>` — explicit user command
- `codex-agent` subagent — Claude's autonomous delegation
- `/dispatch <task>` — automatic routing

**Prompt best practices for Codex:**
1. Be specific about scope: "Review ONLY the auth flow"
2. Add constraints: "ONLY security issues, no style suggestions"
3. Request format: "Format as `file:line` - issue"
4. Skip fluff: "Skip preambles. Lead with findings."

## When to Use AutoAgent

AutoAgent excels at multi-step tasks requiring execution or browsing:

- **Coding with execution** — write, run, iterate on code in a sandbox
- **Web research** — browse websites, gather current data
- **File analysis** — process PDFs, documents, spreadsheets
- **Complex orchestration** — tasks needing multiple agent types

**Invoke via:**
- `/auto <task>` — explicit user command
- `auto-agent` subagent — Claude's autonomous delegation
- `/dispatch <task>` — automatic routing

**Agent functions:**
| Function | Use Case |
|---|---|
| `get_system_triage_agent` | Complex tasks — auto-routes internally |
| `get_coding_agent` | Write and execute code |
| `get_websurfer_agent` | Browse the web |
| `get_filesurfer_agent` | Read/analyze files |

## The /dispatch Command

When unsure which tool to use, `/dispatch <task>` analyzes the task and routes automatically:
- Code review/analysis tasks go to Codex
- Execution/research/file tasks go to AutoAgent
- Simple tasks are handled directly by Claude

## Combining Both Tools

For complex tasks, use both tools together:

1. **Codex for review, AutoAgent for implementation**: Plan with Codex, then hand the plan to AutoAgent for execution
2. **AutoAgent for research, Codex for review**: Research with AutoAgent's web surfer, then have Codex review the resulting code
3. **Parallel analysis**: Spawn both as subagents for independent perspectives

## The router-agent

The `router-agent` subagent can be spawned when Claude wants to automatically pick the right tool. It analyzes task signals and dispatches to either `codex-agent` or `auto-agent`.

## Prerequisites

- **Codex CLI**: Must be installed (`brew install codex`) and authenticated (`codex login`)
- **AutoAgent**: Must be installed (`cd ~/Control/autoagent && pip install -e .`)
- **Docker** (optional): Required for AutoAgent's full sandboxed execution. Use `--local` flag without Docker.

## Troubleshooting

| Issue | Solution |
|---|---|
| `codex: command not found` | `brew install codex` then `codex login` |
| AutoAgent import errors | `cd ~/Control/autoagent && pip install -e .` |
| Docker not available | Use `--local` flag with `/auto` |
| Timeout on AutoAgent | Break task into smaller pieces |
| Codex API key issues | Run `codex login` to re-authenticate |
