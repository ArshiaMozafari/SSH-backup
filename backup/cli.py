"""Command-line entry point."""

import argparse
import getpass
import sys

from .commands import all_categories
from .runner import backup_system_state


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ssh-backup",
        description=(
            "Capture system and network state from a remote "
            "Windows machine over SSH."
        ),
    )
    parser.add_argument("host", help="Target host (e.g. 127.0.0.1)")
    parser.add_argument(
        "-u", "--user", required=True, help="SSH username"
    )
    parser.add_argument(
        "--password",
        help="SSH password. If omitted, you will be prompted.",
    )
    parser.add_argument(
        "-k",
        "--key",
        help="Path to a private key file (use instead of password).",
    )
    parser.add_argument(
        "--key-passphrase",
        help="Passphrase for the private key, if it is encrypted.",
    )
    parser.add_argument(
        "-p", "--port", type=int, default=22, help="SSH port (default: 22)"
    )
    parser.add_argument(
        "-o",
        "--output",
        default="backups",
        help="Directory for backup output (default: backups)",
    )
    parser.add_argument(
        "-c",
        "--categories",
        nargs="+",
        choices=all_categories(),
        help="Only run these categories.",
    )
    parser.add_argument(
        "-t",
        "--timeout",
        type=int,
        default=60,
        help="Per-command timeout in seconds (default: 60)",
    )
    parser.add_argument(
        "-q", "--quiet", action="store_true", help="Suppress progress output."
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    password = args.password
    if not password and not args.key:
        password = getpass.getpass("Password: ")

    try:
        backup_system_state(
            host=args.host,
            username=args.user,
            password=password,
            port=args.port,
            key_filename=args.key,
            key_passphrase=args.key_passphrase,
            out_dir=args.output,
            categories=args.categories,
            command_timeout=args.timeout,
            verbose=not args.quiet,
        )
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        return 130
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())