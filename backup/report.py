"""Writing backup output to disk."""

from pathlib import Path

SEPARATOR = "=" * 70


def write_category_file(
    run_dir: Path,
    category: str,
    results: list[tuple[str, str, str, int, float]],
) -> Path:
    """Write one category's command results to a text file.

    `results` is a list of (command, description, output, exit_status, elapsed).
    """
    path = run_dir / f"{category}.txt"
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# Category: {category}\n\n")
        for cmd, description, output, status, elapsed in results:
            f.write(f"{SEPARATOR}\n")
            f.write(f"# {description}\n")
            f.write(f"$ {cmd}\n")
            f.write(f"[exit={status}, {elapsed:.1f}s]\n")
            f.write(f"{SEPARATOR}\n")
            f.write(output)
            f.write("\n\n")
    return path


def write_summary_file(
    run_dir: Path,
    header: str,
    summary_lines: list[str],
    total_elapsed: float,
) -> Path:
    """Write the top-level summary file for a backup run."""
    path = run_dir / "_summary.txt"
    with open(path, "w", encoding="utf-8") as f:
        f.write(header)
        f.write("\nCommand results:\n")
        f.write("-" * 70 + "\n")
        for line in summary_lines:
            f.write(line + "\n")
        f.write("-" * 70 + "\n")
        f.write(f"Total time: {total_elapsed:.1f}s\n")
        f.write(f"Files written to: {run_dir}\n")
    return path