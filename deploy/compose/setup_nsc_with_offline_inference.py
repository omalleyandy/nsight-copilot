# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["rich>=13"]
# ///
"""Automated setup for Nsight Copilot Offline on DGX Spark.

Installs Docker, NVIDIA Container Toolkit, configures NGC authentication,
and starts the inference services. Idempotent — safe to re-run.

Usage:
    curl -LsSf https://astral.sh/uv/install.sh | UV_INSTALL_DIR=/usr/local/bin sudo -E sh
    sudo -E $(which uv) run setup_nsc_with_offline_inference.py
"""

import configparser
import grp
import json
import os
import pwd
import re
import signal
import subprocess
import sys
import time
import webbrowser

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
NGC_SETUP_URL = "https://ngc.nvidia.com/setup"
NVCR_REGISTRY = "nvcr.io"
TOTAL_STEPS = 7

COMPOSE_FILES = ["-f", "compose.yaml"]

ARCH_RE = re.compile(r"^[a-z0-9]+$")
CODENAME_RE = re.compile(r"^[a-z]+$")

console = Console()


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------


def print_step(step_num: int, message: str) -> None:
    console.print(f"\n[bold]\\[{step_num}/{TOTAL_STEPS}][/bold] {message}")


def _status_line(badge: str, detail: str = "") -> str:
    suffix = f"  [dim]{detail}[/dim]" if detail != "" else ""
    return f"  {badge}{suffix}"


def print_ok(detail: str = "") -> None:
    console.print(_status_line("[bold green]OK[/bold green]", detail))


def print_skipped(detail: str = "") -> None:
    console.print(_status_line("[bold yellow]SKIPPED[/bold yellow]", detail))


def print_failed(detail: str = "") -> None:
    console.print(_status_line("[bold red]FAILED[/bold red]", detail))


def run(
    cmd: list[str],
    *,
    check: bool = True,
    capture: bool = False,
    env: dict[str, str] | None = None,
    stdin_data: str | bytes | None = None,
    status_msg: str = "",
) -> subprocess.CompletedProcess:
    """Run a command with an optional spinner.

    Shows a rich spinner with status_msg while the command runs.
    Output is captured during spinner display to avoid visual collision,
    then printed on failure. When status_msg is empty, no spinner is shown
    and output streams directly to the terminal.

    Returns:
        CompletedProcess from subprocess.run.

    Raises:
        FileNotFoundError: If the command binary is not found and check=False.
    """
    merged_env = {**os.environ, **(env or {})}
    use_spinner = bool(status_msg)

    kwargs: dict = {
        "check": check,
        "env": merged_env,
    }

    # With spinner: capture everything to keep display clean.
    # Without spinner: capture only stderr for error reporting, let stdout stream.
    if use_spinner or capture:
        kwargs["stdout"] = subprocess.PIPE
        kwargs["stderr"] = subprocess.PIPE
    else:
        kwargs["stderr"] = subprocess.PIPE

    if stdin_data is not None:
        kwargs["input"] = stdin_data.encode() if isinstance(stdin_data, str) else stdin_data

    try:
        if use_spinner:
            with console.status(f"[yellow]{status_msg}[/yellow]", spinner="dots"):
                return subprocess.run(cmd, **kwargs)
        return subprocess.run(cmd, **kwargs)
    except subprocess.CalledProcessError as exc:
        stderr_text = ""
        if exc.stderr:
            stderr_text = exc.stderr.decode(errors="replace") if isinstance(exc.stderr, bytes) else exc.stderr
        console.print(f"  [red]Command failed:[/red] [dim]{' '.join(cmd)}[/dim]")
        if stderr_text != "":
            for line in stderr_text.strip().splitlines()[-10:]:
                console.print(f"  [red dim]{line}[/red dim]")
        sys.exit(1)
    except FileNotFoundError:
        if check:
            console.print(f"  [red]Command not found:[/red] [dim]{cmd[0]}[/dim]")
            sys.exit(1)
        raise


def run_streaming(
    cmd: list[str],
    *,
    check: bool = True,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess:
    """Run a command with stdout/stderr connected to the terminal."""
    merged_env = {**os.environ, **(env or {})}
    try:
        result = subprocess.run(cmd, env=merged_env, check=False)
    except FileNotFoundError:
        if check:
            console.print(f"  [red]Command not found:[/red] [dim]{cmd[0]}[/dim]")
            sys.exit(1)
        raise

    if check and result.returncode != 0:
        console.print(f"  [red]Command failed:[/red] [dim]{' '.join(cmd)}[/dim]")
        sys.exit(1)

    return result


def run_silent(cmd: list[str]) -> bool:
    """Run a command silently.

    Returns:
        True if exit code 0, False otherwise.
    """
    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def get_invoking_user() -> tuple[str, int, int, str]:
    """Return (username, uid, gid, home) of the real user (handles sudo)."""
    sudo_user = os.environ.get("SUDO_USER")
    if sudo_user is not None:
        if sudo_user == "root":
            console.print("[red]SUDO_USER is 'root'; cannot determine the real invoking user.[/red]")
            console.print("[red]Run as a regular user with: sudo uv run setup_nsc_with_offline_inference.py[/red]")
            sys.exit(1)
        pw = pwd.getpwnam(sudo_user)
        return sudo_user, pw.pw_uid, pw.pw_gid, pw.pw_dir
    uid = os.getuid()
    pw = pwd.getpwuid(uid)
    return pw.pw_name, pw.pw_uid, pw.pw_gid, pw.pw_dir


def ensure_root() -> None:
    if os.geteuid() != 0:
        console.print(f"[red]This script must be run as root. Re-run with: sudo uv run {sys.argv[0]}[/red]")
        sys.exit(1)


def prompt_input(message: str) -> str:
    """Read a line from stdin.

    Returns:
        The stripped input, or empty string if non-interactive.
    """
    if not sys.stdin.isatty():
        return ""
    try:
        return console.input(message).strip()
    except (EOFError, KeyboardInterrupt):
        console.print()
        return ""


def _read_os_release() -> dict[str, str]:
    """Parse /etc/os-release into a dict.

    Returns:
        Dict mapping keys to values from /etc/os-release.
    """
    result: dict[str, str] = {}
    with open("/etc/os-release") as f:
        for line in f:
            if "=" in line:
                k, _, v = line.strip().partition("=")
                result[k] = v.strip('"')
    return result


# ---------------------------------------------------------------------------
# Step 1: Install Docker Engine
# ---------------------------------------------------------------------------


def step_install_docker() -> None:
    print_step(1, "Install Docker Engine")

    if run_silent(["docker", "--version"]):
        print_skipped("already installed")
        return

    run(["apt-get", "update", "-qq"], status_msg="Updating apt cache...")
    run(
        ["apt-get", "install", "-y", "-qq", "ca-certificates", "curl"],
        status_msg="Installing prerequisites...",
    )

    # Add Docker GPG key
    keyring_dir = "/etc/apt/keyrings"
    gpg_path = os.path.join(keyring_dir, "docker.asc")
    if not os.path.isfile(gpg_path):
        os.makedirs(keyring_dir, mode=0o755, exist_ok=True)
        run(
            ["curl", "-fsSL", "https://download.docker.com/linux/ubuntu/gpg", "-o", gpg_path],
            status_msg="Downloading Docker GPG key...",
        )
        os.chmod(gpg_path, 0o644)

    # Add Docker apt repository
    sources_path = "/etc/apt/sources.list.d/docker.list"
    if not os.path.isfile(sources_path):
        result = run(["dpkg", "--print-architecture"], capture=True)
        arch = result.stdout.decode().strip()
        if not ARCH_RE.match(arch):
            console.print(f"  [red]Unexpected architecture value:[/red] {arch}")
            sys.exit(1)

        os_release = _read_os_release()
        codename = os_release.get("VERSION_CODENAME", "")
        if not CODENAME_RE.match(codename):
            console.print(f"  [red]Unexpected VERSION_CODENAME value:[/red] {codename}")
            sys.exit(1)

        repo_line = f"deb [arch={arch} signed-by={gpg_path}] https://download.docker.com/linux/ubuntu {codename} stable"
        with open(sources_path, "w") as f:
            f.write(repo_line + "\n")

    run(["apt-get", "update", "-qq"], status_msg="Updating apt cache...")
    run(
        [
            "apt-get",
            "install",
            "-y",
            "-qq",
            "docker-ce",
            "docker-ce-cli",
            "containerd.io",
            "docker-buildx-plugin",
            "docker-compose-plugin",
        ],
        status_msg="Installing Docker packages...",
    )

    print_ok()


# ---------------------------------------------------------------------------
# Step 2: Configure Docker without sudo
# ---------------------------------------------------------------------------


def step_configure_docker_no_sudo(username: str) -> None:
    print_step(2, "Configure Docker for non-root usage")

    try:
        docker_group = grp.getgrnam("docker")
        if username in docker_group.gr_mem:
            print_skipped(f"user '{username}' already in docker group")
            return
    except KeyError:
        pass  # group doesn't exist yet

    run(["groupadd", "-f", "docker"], status_msg="Creating docker group...")
    run(["usermod", "-aG", "docker", username], status_msg=f"Adding {username} to docker group...")

    print_ok()
    console.print("  [yellow]Note: You may need to log out and back in, or run 'newgrp docker',[/yellow]")
    console.print("  [yellow]for group changes to take effect on manual docker commands.[/yellow]")


# ---------------------------------------------------------------------------
# Step 3: Install NVIDIA Container Toolkit
# ---------------------------------------------------------------------------


def step_install_nvidia_ctk() -> None:
    print_step(3, "Install NVIDIA Container Toolkit")

    if run_silent(["nvidia-ctk", "--version"]):
        print_skipped("already installed")
        return

    # GPG key — download and dearmor without shell pipeline
    keyring_path = "/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg"
    if not os.path.isfile(keyring_path):
        gpg_result = run(
            ["curl", "-fsSL", "https://nvidia.github.io/libnvidia-container/gpgkey"],
            capture=True,
            status_msg="Downloading NVIDIA CTK GPG key...",
        )
        dearmor_result = run(["gpg", "--dearmor"], stdin_data=gpg_result.stdout, capture=True)
        with open(keyring_path, "wb") as f:
            f.write(dearmor_result.stdout)

    # Apt repo — download and substitute without shell pipeline
    sources_path = "/etc/apt/sources.list.d/nvidia-container-toolkit.list"
    if not os.path.isfile(sources_path):
        list_result = run(
            [
                "curl",
                "-fsSL",
                "https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list",
            ],
            capture=True,
            status_msg="Downloading NVIDIA CTK apt source list...",
        )
        content = list_result.stdout.decode().replace(
            "deb https://",
            f"deb [signed-by={keyring_path}] https://",
        )
        with open(sources_path, "w") as f:
            f.write(content)

    run(["apt-get", "update", "-qq"], status_msg="Updating apt cache...")
    run(
        ["apt-get", "install", "-y", "-qq", "nvidia-container-toolkit"],
        status_msg="Installing NVIDIA Container Toolkit...",
    )

    print_ok()


# ---------------------------------------------------------------------------
# Step 4: Configure NVIDIA CTK for Docker
# ---------------------------------------------------------------------------


def step_configure_nvidia_ctk() -> None:
    print_step(4, "Configure NVIDIA Container Toolkit for Docker")

    daemon_json_path = "/etc/docker/daemon.json"
    try:
        with open(daemon_json_path) as f:
            config = json.load(f)
        if "nvidia" in config.get("runtimes", {}):
            print_skipped("NVIDIA runtime already configured")
            return
    except (FileNotFoundError, json.JSONDecodeError):
        pass  # not configured yet

    run(
        ["nvidia-ctk", "runtime", "configure", "--runtime=docker"],
        status_msg="Configuring NVIDIA runtime...",
    )
    run(["systemctl", "restart", "docker"], status_msg="Restarting Docker daemon...")

    print_ok()


# ---------------------------------------------------------------------------
# Step 5: Resolve environment variables
# ---------------------------------------------------------------------------


def _resolve_ngc_api_key(home_dir: str) -> str:
    """NGC_API_KEY resolution waterfall: env -> ~/.ngc/config -> interactive prompt.

    Returns:
        The resolved NGC API key string.
    """
    # 1. Environment variable
    key = os.environ.get("NGC_API_KEY", "")
    if key.startswith("nvapi-"):
        console.print("  [dim]NGC_API_KEY found in environment.[/dim]")
        return key

    # 2. NGC CLI config
    ngc_config_path = os.path.join(home_dir, ".ngc", "config")
    try:
        config = configparser.ConfigParser()
        config.read(ngc_config_path)
        key = config.get("CURRENT", "apikey", fallback="")
        if key.startswith("nvapi-"):
            console.print(f"  [dim]NGC_API_KEY found in {ngc_config_path}.[/dim]")
            return key
    except (configparser.Error, OSError):
        pass

    # 3. Interactive prompt — try to open browser first
    console.print("  [yellow]NGC_API_KEY not found. Opening NGC setup page...[/yellow]")
    try:
        webbrowser.open(NGC_SETUP_URL)
        console.print("  Browser opened. Generate an API key and paste it below.")
    except OSError:
        console.print(f"  Could not open browser. Go to: [link]{NGC_SETUP_URL}[/link]")
        console.print("  Generate an API key (starts with 'nvapi-') and paste it below.")

    for _ in range(3):
        key = prompt_input("  NGC API Key: ")
        if key.startswith("nvapi-"):
            return key
        if key != "":
            console.print("  [yellow]Invalid key (must start with 'nvapi-'). Try again.[/yellow]")
        else:
            console.print("  [yellow]No input received.[/yellow]")

    console.print("  [red]Failed to obtain NGC_API_KEY after 3 attempts.[/red]")
    sys.exit(1)


def step_setup_env_vars(uid: int, gid: int, home: str) -> dict[str, str]:
    print_step(5, "Resolve environment variables")

    ngc_api_key = _resolve_ngc_api_key(home)

    offline_dir = os.environ.get("OFFLINE_INFERENCE_DIR", "")
    if offline_dir == "":
        offline_dir = os.path.join(home, ".cache", "offline_inference")
        console.print(f"  [dim]OFFLINE_INFERENCE_DIR not set, using default: {offline_dir}[/dim]")

    os.makedirs(offline_dir, exist_ok=True)
    os.chown(offline_dir, uid, gid)

    user_id = str(uid)

    env_vars = {
        "NGC_API_KEY": ngc_api_key,
        "OFFLINE_INFERENCE_DIR": offline_dir,
        "USER_ID": user_id,
    }

    console.print(f"  OFFLINE_INFERENCE_DIR = [cyan]{offline_dir}[/cyan]")
    console.print(f"  USER_ID = [cyan]{user_id}[/cyan]")
    print_ok()
    return env_vars


# ---------------------------------------------------------------------------
# Step 6: Docker login to nvcr.io
# ---------------------------------------------------------------------------


def step_docker_login(ngc_api_key: str, home: str) -> None:
    print_step(6, "Authenticate Docker with NGC registry")

    # Check if already logged in — inspect docker config files for nvcr.io auth entry.
    # Note: if Docker uses a credential helper (credStore), the auths dict may be empty
    # and this check will fall through to a redundant but harmless docker login.
    for config_path in [
        os.path.join(home, ".docker", "config.json"),
        os.path.expanduser("~/.docker/config.json"),  # root's config (running as sudo)
    ]:
        try:
            with open(config_path) as f:
                docker_config = json.load(f)
            if NVCR_REGISTRY in docker_config.get("auths", {}):
                print_skipped(f"already logged in to {NVCR_REGISTRY}")
                return
        except (FileNotFoundError, json.JSONDecodeError):
            continue

    run(
        ["docker", "login", NVCR_REGISTRY, "-u", "$oauthtoken", "--password-stdin"],
        stdin_data=ngc_api_key,
        status_msg=f"Logging in to {NVCR_REGISTRY}...",
    )

    print_ok()


# ---------------------------------------------------------------------------
# Step 7: Start services
# ---------------------------------------------------------------------------


KEY_SERVICES = {"gpt-oss-nim", "autocomplete-nim", "vllm-bge", "rerank-nim", "litellm"}
HEALTH_POLL_INTERVAL_SECONDS = 15


def _as_compose_ps_entries(value: object) -> list[dict[str, object]]:
    if isinstance(value, dict):
        return [value]
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    return []


def _parse_compose_ps_entries(output: bytes | str) -> list[dict[str, object]]:
    text = output.decode(errors="replace") if isinstance(output, bytes) else output
    text = text.strip()
    if text == "":
        return []

    try:
        return _as_compose_ps_entries(json.loads(text))
    except json.JSONDecodeError:
        pass

    entries: list[dict[str, object]] = []
    for line in text.splitlines():
        try:
            entries.extend(_as_compose_ps_entries(json.loads(line)))
        except json.JSONDecodeError:
            continue
    return entries


def _get_compose_services(
    compose_cmd: list[str],
    env: dict[str, str],
    *,
    all_services: bool = False,
) -> list[dict[str, object]]:
    args = ["ps"]
    if all_services:
        args.append("-a")
    args.extend(["--format", "json"])

    result = run(compose_cmd + args, check=False, capture=True, env=env)
    if result.returncode != 0 or result.stdout is None:
        return []
    return _parse_compose_ps_entries(result.stdout)


def _get_running_services(compose_cmd: list[str], env: dict[str, str]) -> set[str]:
    """Query docker compose for currently running services.

    Returns:
        Set of service names that are in "running" state.
    """
    running: set[str] = set()
    for svc in _get_compose_services(compose_cmd, env):
        service = svc.get("Service")
        if svc.get("State") == "running" and isinstance(service, str) and service != "":
            running.add(service)
    return running


def _all_compose_services_stopped(services: list[dict[str, object]]) -> bool:
    if not services:
        return False
    active_states = {"created", "running", "restarting"}
    return all(svc.get("State") not in active_states for svc in services)


def _start_compose_logs(compose_cmd: list[str], env: dict[str, str]) -> subprocess.Popen:
    return subprocess.Popen(
        compose_cmd + ["logs", "-f"],
        env=env,
    )


def _start_and_stream_logs(compose_cmd: list[str], env: dict[str, str]) -> bool:
    """Start services detached, then stream all logs until healthy or failed.

    Returns:
        True if all key services are running, False otherwise.
    """
    merged_env = {**os.environ, **env}

    # Start detached in background — `up -d` blocks on depends_on conditions
    # (model-prep, healthchecks) so we can't wait for it. Run it as a background
    # process and stream logs in parallel.
    up_proc = subprocess.Popen(
        compose_cmd + ["up", "-d", "--remove-orphans"],
        env=merged_env,
        stdout=subprocess.DEVNULL,
    )

    # Give compose a moment to create containers before tailing logs.
    # `docker compose logs -f` can exit immediately when no containers exist yet.
    time.sleep(2)

    logs_proc: subprocess.Popen | None = None
    if _get_compose_services(compose_cmd, env, all_services=True):
        logs_proc = _start_compose_logs(compose_cmd, merged_env)
    else:
        console.print("  [dim]Waiting for compose to create containers before streaming logs...[/dim]")

    healthy = False
    try:
        while True:
            time.sleep(HEALTH_POLL_INTERVAL_SECONDS)
            services = _get_compose_services(compose_cmd, env, all_services=True)

            if logs_proc is None and services:
                logs_proc = _start_compose_logs(compose_cmd, merged_env)
            elif logs_proc is not None and logs_proc.poll() is not None and up_proc.poll() is None:
                logs_proc = _start_compose_logs(compose_cmd, merged_env)

            running = {
                svc.get("Service")
                for svc in services
                if svc.get("State") == "running" and isinstance(svc.get("Service"), str)
            }
            if KEY_SERVICES.issubset(running):
                healthy = True
                break

            up_returncode = up_proc.poll()
            if up_returncode is not None and up_returncode != 0:
                break
            if up_returncode is not None and not services:
                break
            if up_returncode is not None and _all_compose_services_stopped(services):
                break
    except KeyboardInterrupt:
        console.print("\n  [yellow]Interrupted — services stay running in background.[/yellow]")
    finally:
        procs = [proc for proc in (logs_proc, up_proc) if proc is not None]
        for proc in procs:
            if proc.poll() is None:
                proc.send_signal(signal.SIGINT)
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()

    return healthy


def step_start_services(env_vars: dict[str, str]) -> None:
    print_step(7, "Start inference services")

    compose_cmd = ["docker", "compose"] + COMPOSE_FILES

    # Check if services are already running
    if KEY_SERVICES.issubset(_get_running_services(compose_cmd, env_vars)):
        print_skipped("all key services already running")
        return

    # Clean up stale containers from prior interrupted runs
    run(
        compose_cmd + ["down", "--remove-orphans"],
        env=env_vars,
        status_msg="Cleaning up previous containers...",
    )

    console.print("  [dim]Pulling container images...[/dim]\n")
    pull_result = run_streaming(compose_cmd + ["pull"], check=False, env=env_vars)
    if pull_result.returncode != 0:
        print_failed("could not pull all container images")
        console.print(
            "  [yellow]Docker keeps completed image layers. "
            "Re-run setup after fixing network or registry access.[/yellow]"
        )
        sys.exit(1)

    console.print("  [dim]Streaming all service logs (Ctrl+C to stop early)...[/dim]\n")

    healthy = _start_and_stream_logs(compose_cmd, env_vars)

    if healthy:
        print_ok("all key services running")
    else:
        print_failed("not all services came up healthy")

        # Show container status so the user can see which services failed
        merged_env = {**os.environ, **env_vars}
        console.print("\n  [bold]Container status:[/bold]")
        subprocess.run(
            compose_cmd + ["ps", "-a"],
            env=merged_env,
            stderr=subprocess.DEVNULL,
            check=False,
        )

        # Show recent logs from non-running services to surface the actual errors
        result = subprocess.run(
            compose_cmd + ["ps", "-a", "--format", "json"],
            env=merged_env,
            capture_output=True,
            check=False,
        )
        if result.returncode == 0 and result.stdout:
            failed_services: list[str] = []
            for svc in _parse_compose_ps_entries(result.stdout):
                if svc.get("State") not in ("running",):
                    name = svc.get("Service", "")
                    if isinstance(name, str) and name:
                        failed_services.append(name)
            if failed_services:
                console.print(f"\n  [bold]Recent logs from failed services ({', '.join(failed_services)}):[/bold]")
                subprocess.run(
                    compose_cmd + ["logs", "--tail=30"] + failed_services,
                    env=merged_env,
                    stderr=subprocess.DEVNULL,
                    check=False,
                )

        sys.exit(1)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    ensure_root()

    username, uid, gid, home = get_invoking_user()

    os.chdir(SCRIPT_DIR)

    # Verify required files exist
    required_files = ["compose.yaml", "litellm-config.yaml", "model-prep.sh"]
    for f in required_files:
        if not os.path.isfile(f):
            console.print(f"[red]Error: Required file '{f}' not found in {SCRIPT_DIR}[/red]")
            sys.exit(1)

    console.print(
        Panel(
            Text.assemble(
                ("Nsight Copilot Offline Setup\n", "bold"),
                (f"Target user: {username} (uid={uid})\n", ""),
                (f"Working directory: {SCRIPT_DIR}", "dim"),
            ),
            border_style="blue",
        )
    )

    step_install_docker()
    step_configure_docker_no_sudo(username)
    step_install_nvidia_ctk()
    step_configure_nvidia_ctk()
    env_vars = step_setup_env_vars(uid, gid, home)
    step_docker_login(env_vars["NGC_API_KEY"], home)
    step_start_services(env_vars)

    console.print()
    console.print(
        Panel(
            "[bold green]Setup complete![/bold green]\n"
            "The Nsight Copilot API will be available at [link]http://localhost:8080[/link] "
            "once all services are healthy.",
            border_style="green",
        )
    )


if __name__ == "__main__":
    main()
