#!/usr/bin/env python3
"""
Non-interactive wrapper for AutoAgent's system agents.

Initializes environments (local or Docker) and runs a single query
through an AutoAgent agent function, printing the result to stdout.

This exists because `auto agent` CLI passes string context variables,
but system agents (triage, coding, web surfer, file surfer) require
actual environment objects (code_env, web_env, file_env).
"""

import argparse
import importlib
import os
import re
import signal
import subprocess
import sys

# AutoAgent's constant.py expects to be importable from cwd or sys.path.
# Ensure the autoagent repo root is on the path.
AUTOAGENT_ROOT = os.path.expanduser("~/Control/autoagent")
if AUTOAGENT_ROOT not in sys.path:
    sys.path.insert(0, AUTOAGENT_ROOT)


def timeout_handler(signum, frame):
    print("ERROR: AutoAgent execution timed out", file=sys.stderr)
    sys.exit(124)


def docker_available():
    try:
        result = subprocess.run(
            ["docker", "info"], capture_output=True, timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def parse_solution(raw_output):
    """Extract content from <solution> tags if present."""
    if raw_output and raw_output.startswith("Case resolved"):
        matches = re.findall(r"<solution>(.*?)</solution>", raw_output, re.DOTALL)
        if matches:
            return matches[0].strip()
    return raw_output


def run(query, agent_func_name, model, use_local, timeout_secs):
    if timeout_secs > 0:
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout_secs)

    # Suppress rich/progress output from AutoAgent internals
    os.environ.setdefault("MC_MODE", "")

    from autoagent import MetaChain
    from autoagent.environment.docker_env import DockerConfig, check_container_ports
    from autoagent.environment.local_env import LocalEnv
    from autoagent.environment.browser_env import BrowserEnv
    from autoagent.environment.markdown_browser import RequestsMarkdownBrowser
    from autoagent.logger import LoggerManager, MetaChainLogger
    from constant import DOCKER_WORKPLACE_NAME

    LoggerManager.set_logger(MetaChainLogger(log_path=None))

    container_name = "orchestrator_oneshot"
    port = 12350

    # Check port availability
    port_info = check_container_ports(container_name)
    if port_info:
        port = port_info[0]

    local_root = os.path.join(
        os.getcwd(), "workspace_meta_showcase", f"showcase_{container_name}"
    )
    os.makedirs(local_root, exist_ok=True)

    docker_config = DockerConfig(
        workplace_name=DOCKER_WORKPLACE_NAME,
        container_name=container_name,
        communication_port=port,
        conda_path="/root/miniconda3",
        local_root=local_root,
        test_pull_name="main",
        git_clone=False,
    )

    # Initialize environments
    should_use_local = use_local or not docker_available()
    if should_use_local:
        code_env = LocalEnv(docker_config)
    else:
        from autoagent.environment.docker_env import DockerEnv

        code_env = DockerEnv(docker_config)
        code_env.init_container()

    web_env = BrowserEnv(
        browsergym_eval_env=None,
        local_root=docker_config.local_root,
        workplace_name=docker_config.workplace_name,
    )
    file_env = RequestsMarkdownBrowser(
        viewport_size=1024 * 5,
        local_root=docker_config.local_root,
        workplace_name=docker_config.workplace_name,
        downloads_folder=os.path.join(
            docker_config.local_root, docker_config.workplace_name, "downloads"
        ),
    )

    context_variables = {
        "working_dir": docker_config.workplace_name,
        "code_env": code_env,
        "web_env": web_env,
        "file_env": file_env,
    }

    # Load agent function
    agent_module = importlib.import_module("autoagent.agents")
    try:
        agent_fn = getattr(agent_module, agent_func_name)
    except AttributeError:
        print(f"ERROR: Agent function '{agent_func_name}' not found", file=sys.stderr)
        sys.exit(1)

    agent = agent_fn(model)
    client = MetaChain()
    messages = [{"role": "user", "content": query}]

    response = client.run(agent, messages, context_variables, debug=False)

    raw_output = response.messages[-1]["content"]
    result = parse_solution(raw_output)
    print(result)


def main():
    parser = argparse.ArgumentParser(description="Run AutoAgent non-interactively")
    parser.add_argument("--query", required=True, help="The task/query to execute")
    parser.add_argument(
        "--agent-func",
        default="get_system_triage_agent",
        help="Agent function name (default: get_system_triage_agent)",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="LLM model override (default: uses COMPLETION_MODEL from .env)",
    )
    parser.add_argument(
        "--local",
        action="store_true",
        help="Force local environment (no Docker)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=240,
        help="Timeout in seconds (default: 240, 0=no timeout)",
    )

    args = parser.parse_args()

    model = args.model
    if model is None:
        from constant import COMPLETION_MODEL

        model = COMPLETION_MODEL

    run(args.query, args.agent_func, model, args.local, args.timeout)


if __name__ == "__main__":
    main()
