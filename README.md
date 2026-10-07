# SSH State Backup

Capture system and network state from a remote Windows host over SSH,
into a timestamped folder of readable, diffable text files.

## What it does

Connects to a Windows machine over SSH and runs a curated list of
diagnostic commands, grouped by category:

- **system** — hostname, OS, hardware, drivers
- **network** — IP config, routes, ARP, netstat, `netsh dump`, DNS
- **storage** — disks, drive letters, shadow copies
- **users_and_security** — local users, admins, sessions, password policy
- **services_and_processes** — services, processes, startup items

Each category is written to its own `.txt` file, plus a `_summary.txt`
with timing and exit codes for every command.

## Requirements

- Python 3.10+
- OpenSSH Server running on the target Windows machine
- An account with administrator rights for full output
  (some commands return partial data for non-admin users)

### Enabling OpenSSH Server on Windows

In an elevated PowerShell:

    Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
    Start-Service sshd
    Set-Service -Name sshd -StartupType Automatic

## Install

    pip install -r requirements.txt

Or, to install it as a command:

    pip install -e .

## Usage

Run as a module:

    python -m backup.cli 127.0.0.1 -u YourSystemName

Run only specific categories:

    python -m backup.cli 127.0.0.1 -u YourSystemName -c network users_and_security

If installed with `pip install -e .`:

    ssh-backup 127.0.0.1 -u YourSystemName

Use a key instead of a password:

    ssh-backup 127.0.0.1 -u YourSystemName -k ~/.ssh/id_rsa

If the key is passphrase-protected:

    ssh-backup 127.0.0.1 -u YourSystemName -k ~/.ssh/id_rsa --key-passphrase

Note: `-p` is the SSH **port** (matching `ssh(1)`). The password is
passed with `--password` or prompted for interactively.

## Output

    backups/
    └── 127.0.0.1_20250115_143022/
        ├── _summary.txt
        ├── system.txt
        ├── network.txt
        ├── storage.txt
        ├── users_and_security.txt
        └── services_and_processes.txt

## Security notes

- If `--password` is passed on the command line, it may appear in your
  shell history and process list. Prefer SSH keys, or let the tool
  prompt for the password.
- The tool uses `AutoAddPolicy`, meaning it accepts any host key.
  This is convenient but does not protect against man-in-the-middle
  attacks. For production use, manage `known_hosts` explicitly.
- Backup output contains system information. Do not commit `backups/`
  to version control. This is already in `.gitignore`.
