---
description: Run AutoAgent for multi-step coding, web research, or file analysis in a sandboxed environment
allowed-tools: Bash
argument-hint: "[--model name] [--agent func] [--local] <task>"
---

# AutoAgent Command

Run AutoAgent's system agents for multi-step coding, web research, and file analysis tasks.

## Arguments

$ARGUMENTS

## Step 1: Parse Arguments

Extract optional flags from $ARGUMENTS:

| Flag | Valid Values | Default |
|------|-------------|---------|
| `--model` | any model name | (from COMPLETION_MODEL env) |
| `--agent` | get_system_triage_agent, get_coding_agent, get_websurfer_agent, get_filesurfer_agent | get_system_triage_agent |
| `--local` | (flag, no value) | false |

**Parsing rules:**
1. Scan for `--model <value>` - accept any string
2. Scan for `--agent <value>` - validate it's one of the valid agent functions
3. Scan for `--local` flag (no value)
4. Everything remaining after extracting flags is the TASK

**Validation errors:**
- If `--agent` has invalid value: "Invalid agent: '<value>'. Valid: get_system_triage_agent, get_coding_agent, get_websurfer_agent, get_filesurfer_agent"

## Step 2: Validate Task

If no task remains after parsing flags, respond with:

```
No task specified.

Usage:
  /auto [options] <task>

Examples:
  /auto research the latest papers on RAG architectures
  /auto --agent get_coding_agent write a Python script that parses CSV files
  /auto --local analyze the files in the current directory
  /auto --model gpt-4o plan a microservices architecture for an e-commerce app

Options:
  --model <name>     Model to use (default: COMPLETION_MODEL from environment)
  --agent <func>     Agent function (default: get_system_triage_agent)
  --local            Force local execution (no Docker)
```

## Step 3: Execute AutoAgent

Build and execute the command with parsed values (or defaults):

```bash
python ~/.claude/plugins/local/cc-orchestrator-plugin/scripts/auto_oneshot.py \
  --query "<TASK>" \
  --agent-func <AGENT> \
  <MODEL_FLAG> \
  <LOCAL_FLAG> \
  --timeout 240 \
  2>&1
```

Where:
- `<TASK>` = the task text from arguments
- `<AGENT>` = parsed --agent or "get_system_triage_agent"
- `<MODEL_FLAG>` = `--model <value>` if specified, omitted otherwise
- `<LOCAL_FLAG>` = `--local` if specified or Docker is unavailable
- Timeout set to 240 seconds for the wrapper's internal timeout
- Bash tool timeout should be 300000ms (5 minutes) to allow for imports + execution

## Step 4: Return Output

Return AutoAgent's output to the user. If the command fails, show the error message and suggest troubleshooting:
- If "ModuleNotFoundError": AutoAgent may not be installed. Run `cd ~/Control/autoagent && pip install -e .`
- If "Docker" error: Try adding `--local` flag
- If timeout: Try a simpler query or increase timeout

## Agent Selection Guide

| Agent | Best For |
|-------|----------|
| `get_system_triage_agent` | Complex tasks - auto-routes to the right specialist |
| `get_coding_agent` | Writing, executing, and iterating on code |
| `get_websurfer_agent` | Web browsing, online research, data gathering |
| `get_filesurfer_agent` | Reading and analyzing files (PDF, DOCX, etc.) |
