---
description: Automatically route a task to the best tool — Codex for code review/analysis, AutoAgent for multi-step coding/research, or Claude directly for simple tasks
allowed-tools: Bash
argument-hint: "<task description>"
---

# Dispatch Command

Intelligent task router that picks the optimal tool for the job.

## Arguments

$ARGUMENTS

## Step 1: Validate Task

If $ARGUMENTS is empty, respond with:

```
No task specified.

Usage:
  /dispatch <task description>

Examples:
  /dispatch review auth.py for SQL injection vulnerabilities
  /dispatch research the latest papers on RAG architectures
  /dispatch write a Python script that converts CSV to JSON
  /dispatch find bugs in the sorting implementation

The router automatically picks the best tool:
  - Codex: code review, security audits, bug hunting, planning
  - AutoAgent: multi-step coding, web research, file analysis
  - Claude: simple questions, trivial changes
```

## Step 2: Analyze and Route

Classify the task from $ARGUMENTS:

**Route to Codex** if the task involves:
- Code review, code analysis, code quality
- Security audit, vulnerability scanning
- Bug hunting, finding issues in existing code
- Implementation planning (analysis only, no execution)
- Edge case enumeration

**Route to AutoAgent** if the task involves:
- Writing and executing code (needs a sandbox)
- Web research, browsing, data gathering
- Analyzing files (PDF, DOCX, spreadsheets)
- Multi-step tasks requiring iteration
- Tasks that need to run code to verify results

**Handle directly** if the task is:
- A simple question
- A trivial code change
- Conversational or informational

## Step 3: Execute

### If Codex:

Announce: "Routing to **Codex** — this is a [review/analysis/planning] task."

```bash
codex exec \
  --model gpt-5.4 \
  --sandbox read-only \
  "<TASK_WITH_CONSTRAINTS>" \
  2>&1
```

Add appropriate constraints based on task type (see router-agent for constraint templates).
Always append: `Format findings as: \`file:line\` - description. Skip preambles. Lead with findings.`

### If AutoAgent:

Announce: "Routing to **AutoAgent** — this needs [execution/research/file analysis]."

Select agent function:
- Code tasks → `get_coding_agent`
- Web research → `get_websurfer_agent`
- File analysis → `get_filesurfer_agent`
- Complex/unclear → `get_system_triage_agent`

```bash
python ~/.claude/plugins/local/cc-orchestrator-plugin/scripts/auto_oneshot.py \
  --query "<TASK>" \
  --agent-func <AGENT> \
  --local \
  --timeout 240 \
  2>&1
```

Set Bash tool timeout to 300000ms.

### If Claude:

Just answer the task directly — no external tool needed.

## Step 4: Present Results

1. Show which tool was chosen and why (one line)
2. Present the tool's output
3. Add your own synthesis or commentary if useful
