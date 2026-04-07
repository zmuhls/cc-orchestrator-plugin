# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A Claude Code plugin that routes analysis tasks to either **Codex CLI** (OpenAI, for code review/static analysis) or **AutoAgent** (HKUDS, for multi-step coding/research/file analysis). The headline command is `/dispatch <task>` which picks the optimal tool automatically.

This is a Claude Code plugin — it follows the `.claude-plugin/` manifest structure with markdown-based commands, agents, and skills. There is no build step.

## Plugin Components

- **Commands** (`commands/*.md`) — slash commands with YAML frontmatter (`description`, `allowed-tools`, `argument-hint`). `/auto` wraps AutoAgent, `/dispatch` auto-routes.
- **Agents** (`agents/*.md`) — subagents Claude spawns autonomously. `auto-agent` delegates to AutoAgent, `router-agent` decides which tool to use.
- **Skills** (`skills/orchestrator/SKILL.md`) — contextual guidance loaded when either tool is relevant.
- **Scripts** (`scripts/auto_oneshot.py`) — the only Python in the repo. Bridges AutoAgent's interactive CLI to non-interactive execution.

## auto_oneshot.py

This is the critical bridge script. AutoAgent's `auto main` command is a TUI with `PromptSession` — can't be called from Claude Code's Bash tool. AutoAgent's `auto agent` CLI passes string context variables, but system agents need actual environment objects (`code_env`, `web_env`, `file_env`). This wrapper extracts the initialization from `cli.py:179-215` and runs a single query.

Key dependency: `AUTOAGENT_ROOT` is hardcoded to `~/Control/autoagent`. If AutoAgent moves, update line 23.

The script auto-detects Docker via `docker info`. Falls back to `LocalEnv` with `--local` flag or when Docker is unavailable.

## External Dependencies

| Dependency | Required | Install |
|---|---|---|
| AutoAgent | yes | `cd ~/Control/autoagent && pip install -e .` |
| Codex CLI | yes (for `/codex`, `/dispatch` Codex routing) | `brew install codex && codex login` |
| cc-codex-plugin | yes (provides `codex exec`) | `claude plugin marketplace add thepushkarp/cc-codex-plugin` |
| Docker Desktop | optional (for sandboxed execution) | `brew install --cask docker-desktop` |
| pyparsing >= 3.1 | yes (AutoAgent's browsergym needs it) | `pip install 'pyparsing>=3.1.0'` |

## Conventions

- Commits: lowercase, imperative, under 100 characters
- Plugin markdown: YAML frontmatter must be valid YAML — no XML-like tags (`<example>`) inside the `---` delimiters
- Agent descriptions use YAML `>` folded scalar for multi-line text
- Commands mirror the pattern in cc-codex-plugin's `commands/codex.md`

## Validation and Testing

```bash
claude plugin validate .                    # validate plugin structure
claude plugin marketplace add zmuhls/cc-orchestrator-plugin  # register
claude plugin install cc-orchestrator-plugin@cc-orchestrator-plugin  # install
# then /reload-plugins in a Claude Code session

# smoke test the wrapper directly
python scripts/auto_oneshot.py --query "what is 2+2" --agent-func get_system_triage_agent --local
```
