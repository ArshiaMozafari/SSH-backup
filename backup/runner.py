"""Command execution and backup orchestration."""

import sys
from datetime import datetime
from pathlib import Path

from .client import connect
from .commands import get_groups
from .report import write_category_file, write_summary_file


def run_command(
    client,
    cmd: str,
    timeout: int = 60,
) -> tuple[str, int, float]:
    """Run a single command over SSH.

    Returns (output, exit_status, elapsed_seconds).
    Never raises on command failure — returns a diagnostic string instead.
    """
    start = datetime.now()
    try:
        stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
        out = stdout.read().decode(errors="replace")
        err = stderr.read().decode(errors="replace")
        status = stdout.channel.recv_exit_status()

        parts: list[str] = []
        if out.strip():
            parts.append(out)
        if err.strip():
            parts.append("--- stderr ---\n" + err)
        combined = "\n".join(parts) if parts else "(no output)"

        elapsed = (datetime.now() - start).total_seconds()
        return combined, status, elapsed
    except Exception as exc:
        elapsed = (datetime.now() - start).total_seconds()
        return f"[ERROR running command: {exc}]", -1, elapsed


def backup_system_state(
    host: str,
    username: str,
    password: str | None = None,
    port: int = 22,
    key_filename: str | None = None,
    key_passphrase: str | None = None,
    out_dir: str = "backups",
    categories: list[str] | None = None,
    command_timeout: int = 60,
    verbose: bool = True,
) -> Path:
    """Connect to a host and save categorized state to files.

    Returns the directory containing the backup.
    """
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if verbose:
        print(f"Connecting to {host}:{port} as {username}...")

    client = connect(
        host=host,
        username=username,
        password=password,
        port=port,
        key_filename=key_filename,
        key_passphrase=key_passphrase,
    )

    if verbose:
        print("Connected.")

    groups = get_groups(categories)
    run_dir = Path(out_dir) / f"{host}_{stamp}"
    run_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Header info
        hostname, _, _ = run_command(client, "hostname", timeout=15)
        hostname = hostname.strip() or host
        header = (
            "System state backup\n"
            "===================\n"
            f"Host:     {host} ({hostname})\n"
            f"User:     {username}\n"
            f"Started:  {stamp}\n"
            f"Python:   {sys.version.split()[0]}\n"
        )

        summary_lines: list[str] = []
        total_start = datetime.now()

        for category, commands in groups.items():
            if verbose:
                print(f"\n[{category}]")

            results = []
            for cmd, description in commands:
                if verbose:
                    print(f"  {description} ...", end=" ", flush=True)

                output, status, elapsed = run_command(
                    client, cmd, timeout=command_timeout
                )
                results.append((cmd, description, output, status, elapsed))

                if verbose:
                    marker = "ok" if status == 0 else f"exit={status}"
                    print(f"{marker} ({elapsed:.1f}s)")

                summary_lines.append(
                    f"{category:26s} {description:42s} "
                    f"exit={status:<4} {elapsed:6.1f}s"
                )

            write_category_file(run_dir, category, results)

        total_elapsed = (datetime.now() - total_start).total_seconds()
        write_summary_file(
            run_dir, header, summary_lines, total_elapsed
        )

        if verbose:
            print(f"\nBackup complete in {total_elapsed:.1f}s")
            print(f"Saved to: {run_dir}")

        return run_dir

    finally:
        client.close()