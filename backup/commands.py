"""Command definitions, grouped by category.

Each entry is a tuple of (command, human-readable description).
Commands are run in the order listed.
"""

COMMAND_GROUPS: dict[str, list[tuple[str, str]]] = {
    "system": [
        ("hostname", "Hostname"),
        ("whoami", "Current user"),
        ("ver", "Windows version"),
        (
            "wmic os get caption,version,buildnumber /format:list",
            "OS details",
        ),
        (
            "wmic computersystem get manufacturer,model /format:list",
            "Hardware",
        ),
        ("systeminfo", "Full system info"),
        ("driverquery", "Installed drivers"),
    ],
    "network": [
        ("ipconfig /all", "IP configuration"),
        ("route print", "Routing table"),
        ("arp -a", "ARP cache"),
        ("netstat -anob", "Connections + owning process"),
        ("netsh dump", "Full network config (restorable)"),
        ("nslookup microsoft.com", "DNS resolution test"),
        ("ipconfig /displaydns", "DNS cache"),
        ("netsh wlan show profiles", "Saved WiFi profiles"),
    ],
    "storage": [
        (
            "wmic logicaldisk get name,size,freespace,description /format:list",
            "Disks",
        ),
        ("fsutil fsinfo drives", "Drive letters"),
        ("vssadmin list shadows", "Shadow copies / restore points"),
    ],
    "users_and_security": [
        ("net user", "Local users"),
        ("net localgroup administrators", "Admin group members"),
        ("query user", "Logged-in users"),
        ("net accounts", "Password policy"),
    ],
    "services_and_processes": [
        ("sc query state= all", "All services and states"),
        ("tasklist /v", "Processes with details"),
        (
            "wmic startup get caption,command /format:list",
            "Startup items",
        ),
    ],
}


def all_categories() -> list[str]:
    """Return the list of available category names."""
    return list(COMMAND_GROUPS.keys())


def get_groups(categories: list[str] | None = None):
    """Return command groups, optionally filtered to a subset of categories."""
    if not categories:
        return COMMAND_GROUPS

    unknown = set(categories) - set(COMMAND_GROUPS)
    if unknown:
        raise ValueError(f"Unknown categories: {', '.join(sorted(unknown))}")

    return {name: COMMAND_GROUPS[name] for name in categories}