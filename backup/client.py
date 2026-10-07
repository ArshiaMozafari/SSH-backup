"""SSH connection handling."""

import paramiko


def connect(
    host: str,
    username: str,
    password: str | None = None,
    port: int = 22,
    key_filename: str | None = None,
    key_passphrase: str | None = None,
    timeout: int = 30,
) -> paramiko.SSHClient:
    """Open an SSH connection to a remote host.

    Uses password auth if `password` is provided, otherwise key auth
    if `key_filename` is provided.
    """
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    client.connect(
        hostname=host,
        port=port,
        username=username,
        password=password,
        key_filename=key_filename,
        passphrase=key_passphrase,
        timeout=timeout,
        banner_timeout=timeout,
        auth_timeout=timeout,
    )
    return client