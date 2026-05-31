#!/usr/bin/env python3
"""Generate docs/TOOLS.md from the server's registered tool metadata.

Run from the repo root after changing tools:
    python scripts/gen_tools_doc.py

It introspects the FastMCP instance directly (no NAS connection needed) so the
tool reference stays accurate and complete.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from synology_mcp import tools  # noqa: E402,F401  (registers tools)
from synology_mcp.app import mcp  # noqa: E402

CATEGORIES = [
    ("dashboard", "Dashboard", "One-call aggregate snapshot for building visual dashboards."),
    ("monitoring", "System Monitoring", "Identity, live load and network information."),
    ("system", "System Health & Activity", "Overall health, active connections and processes."),
    ("storage", "Storage", "Volumes, storage pools and physical disks."),
    ("files", "Files", "Browse, inspect, search and manage files via File Station."),
    ("packages", "Packages & DSM Updates", "Installed packages and DSM operating-system updates."),
    ("docker", "Docker / Container Manager", "Containers, images, projects and live stats."),
    ("virtualization", "Virtual Machine Manager", "Virtual machine guests."),
    ("surveillance", "Surveillance Station", "Cameras and Surveillance Station info."),
    ("photos", "Synology Photos", "Photo albums (personal space)."),
    ("drive", "Synology Drive", "Drive client connections."),
    ("downloads", "Download Station", "Download tasks (HTTP/FTP/magnet/torrent)."),
    ("backup", "Backup", "Hyper Backup tasks."),
    ("scheduler", "Task Scheduler", "Scheduled tasks (cron jobs, scripts, scheduled backups)."),
    ("admin", "Users, Groups & Shared Folders", "Accounts, groups, shared folders, logs and security scan."),
    ("services", "File & Terminal Services", "SMB/AFP/NFS/FTP, SSH/Telnet and SNMP."),
    ("hardware", "Hardware", "Power, hibernation, UPS and USB devices."),
    ("security", "Security & Certificates", "DSM security, auto-block, firewall and TLS certificates."),
    ("network_services", "Network Services", "DDNS and QuickConnect."),
    ("notifications", "Notifications", "E-mail notification settings."),
    ("power", "Power Control (opt-in)", "Reboot, shutdown and DSM update — disabled unless enabled."),
]

RETURNS = {
    "get_overview": "A complete snapshot: `system`, `health`, `load`, `storage` (volumes+disks) and `counts` (packages/containers/VMs/downloads). Ideal input for a dashboard.",
    "get_system_info": "Model, DSM version, hostname, uptime, RAM (MB), serial, temperature (°C) and system time.",
    "get_resource_usage": "CPU load breakdown and 1/5/15-min averages, memory used/available/percent, swap usage, and network rx/tx (KB/s).",
    "get_network_info": "Hostname, gateway, primary/secondary DNS, and a list of interfaces with IP, mask, type, link speed and status.",
    "get_system_health": "Overall status (e.g. `system_ok`), uptime, reboot-required flag, fan status and disk-temperature alarm.",
    "get_time_settings": "Current NAS time, timezone, and whether NTP sync is enabled plus the NTP server.",
    "get_resource_history": "Recent Resource Monitor threshold events (time, level, description) for plotting trends.",
    "get_surveillance_info": "Surveillance Station version, cameras in use, licences and max camera support.",
    "list_cameras": "Cameras with id, name, vendor, model, IP, MAC, status code and online flag.",
    "list_photo_albums": "Albums in Synology Photos (personal space): id, name, item count, shared flag and type.",
    "list_drive_connections": "Synology Drive client connections: client name, IP, type, version, status, location, login and last-auth times.",
    "get_active_connections": "List of current connections: user, source IP, protocol, time and whether it is the current session.",
    "list_processes": "Top processes sorted by CPU or memory, each with pid, command, CPU % and memory (MB).",
    "get_storage_info": "Per-volume RAID type, filesystem, total/used/free (GB), used % and status.",
    "get_storage_pools": "Per-pool RAID type, status, drive type, disk count and data-scrubbing status/last run.",
    "get_disk_info": "Per-disk model, vendor, size (GB), status, temperature (°C), S.M.A.R.T. status, type, SSD life and pool membership.",
    "list_shares": "Shared folders visible in File Station: name, path, real path and read-only flag.",
    "list_files": "Directory listing: name, path, is_dir, size (bytes), modified and created timestamps. Supports sorting, paging and a wildcard filter.",
    "get_file_info": "Detailed metadata for one or more paths: real path, size, owner, modified/created/accessed times.",
    "get_directory_size": "Recursive total size (bytes and GB) plus file and directory counts for a folder.",
    "get_file_md5": "The MD5 checksum of a file.",
    "search_files": "Files matching a name pattern under a folder (recursive optional): name, path, is_dir, size, modified.",
    "create_folder": "Confirmation with the created folder path.",
    "rename_item": "Confirmation with the renamed item.",
    "copy_move_item": "Action (copy/move) and completion status.",
    "delete_item": "Confirmation and the list of deleted paths.",
    "extract_archive": "Destination folder and completion status.",
    "create_share_link": "The created public link(s): URL and link id.",
    "check_dsm_update": "Whether a DSM update is available, the new version (if any), current state, auto-download flag and update channel.",
    "list_packages": "Installed packages with id, name, version, running status and type. Optionally only running ones.",
    "set_package_state": "Confirmation of the start/stop action on a package.",
    "list_containers": "All containers with name, image, running flag, state, exit code, start/finish times.",
    "get_container_logs": "Recent log lines for a container (time, stream, text).",
    "set_container_state": "Confirmation of start/stop/restart on a container.",
    "get_container_stats": "Live CPU %, memory (MB) and raw resource counters for a running container.",
    "list_docker_projects": "Container Manager / Compose projects: id, name, status, path, container count and creation time.",
    "list_docker_images": "Stored images: repository, tags, size (MB), creation time and whether an update is available.",
    "list_virtual_machines": "VMM guests with name, status, vCPUs, RAM (MB), storage, autorun and description.",
    "set_vm_state": "Confirmation of poweron/poweroff/shutdown/restart on a VM.",
    "list_downloads": "Download tasks with id, title, type, status, size (MB), progress % and up/down speed (KB/s).",
    "add_download": "Confirmation of the added URL and its destination.",
    "manage_download": "Confirmation of pause/resume/delete on the given task ids.",
    "list_backup_tasks": "Hyper Backup tasks with id, name, state, status, target, type and encryption flag.",
    "run_backup_task": "Confirmation that the backup task was started.",
    "list_scheduled_tasks": "Scheduled tasks with id, name, type, enabled flag, owner, next run and can-run-now flag.",
    "run_scheduled_task": "Confirmation that the task was triggered.",
    "list_users": "Local accounts with name, description, email, expiry and 2FA status.",
    "list_groups": "Local groups with name and description.",
    "list_shared_folders": "Shared folders (admin view): name, volume, description, encryption and USB-share flags.",
    "create_shared_folder": "Confirmation with the created folder name and volume.",
    "delete_shared_folder": "Confirmation of the deleted folder.",
    "get_system_logs": "Recent log entries (time, level, type, who, message) plus info/warning/error counts.",
    "get_security_scan_status": "Security Advisor result per category (malware, network, system, update) with severity and issue counts.",
    "get_file_services": "Enabled state and key settings of SMB, AFP, NFS and FTP.",
    "set_file_service": "Confirmation of enabling/disabling a file-sharing protocol.",
    "get_terminal_settings": "SSH and Telnet enabled state and SSH port.",
    "get_snmp_settings": "SNMP enabled state, versions, location and contact.",
    "get_power_settings": "Power-recovery, Wake-on-LAN, LED brightness, beep and scheduled power task counts.",
    "get_hibernation_settings": "Disk idle time before hibernation and auto-power-off settings.",
    "get_ups_status": "UPS enabled state, mode, model, battery charge %, runtime and connection status.",
    "list_usb_devices": "Connected USB devices (id and title).",
    "get_security_settings": "DSM session timeout, CSRF protection, IP-checking and stay-signed-in options.",
    "get_autoblock_settings": "Auto-block policy: enabled, attempts, window (minutes) and block expiry (days).",
    "get_firewall_status": "Firewall profile names.",
    "list_certificates": "Installed TLS certificates: description, subject, issuer, validity dates, default/broken/renewable flags and assigned-service count.",
    "get_ddns_status": "DDNS records: hostname, provider, external IP, status, enabled flag and last update.",
    "get_quickconnect_status": "QuickConnect enabled state, ID, server id, region and domain.",
    "get_notification_settings": "E-mail notification enabled state, sender, SMTP server and OAuth flag.",
    "reboot_nas": "Confirmation that a reboot was issued (requires power control enabled).",
    "shutdown_nas": "Confirmation that a shutdown was issued (requires power control enabled).",
    "install_dsm_update": "Confirmation that a DSM update install was started (requires power control enabled).",
}


def tag(desc: str) -> str:
    t = []
    if "[control]" in desc:
        t.append("`control`")
    if "[power]" in desc:
        t.append("`power`")
    return " ".join(t)


def short_desc(desc: str) -> str:
    # first sentence / line, stripped of tags
    line = desc.split("\n")[0].replace("[control]", "").replace("[power]", "").strip()
    return line


async def _collect() -> list[dict]:
    listed = await mcp.list_tools()
    fnmap = {}
    for name, tool in mcp._tool_manager._tools.items():
        fn = getattr(tool, "fn", None)
        fnmap[name] = getattr(fn, "__module__", "").split(".")[-1] if fn else ""
    out = []
    for t in listed:
        props = (t.inputSchema or {}).get("properties", {})
        req = set((t.inputSchema or {}).get("required", []))
        params = [
            {"name": pn, "type": pp.get("type", "any"),
             "required": pn in req, "default": pp.get("default")}
            for pn, pp in props.items()
        ]
        out.append({"name": t.name, "desc": (t.description or "").strip(),
                    "params": params, "module": fnmap.get(t.name, "")})
    return out


def main() -> None:
    tools_meta = asyncio.run(_collect())
    by_mod = {}
    for t in tools_meta:
        by_mod.setdefault(t["module"], []).append(t)

    out = ["# Tool Reference\n",
           f"The Synology MCP server exposes **{len(tools_meta)} tools**. "
           "Tools tagged `control` change NAS state; tools tagged `power` are "
           "destructive and disabled unless `SYNOLOGY_ENABLE_POWER_CONTROL=true`.\n",
           "## Contents\n"]
    for mod, title, _ in CATEGORIES:
        if mod in by_mod:
            slug = "".join(c for c in title.lower() if c.isalnum() or c in " -")
            anchor = "-".join(slug.split())
            out.append(f"- [{title}](#{anchor}) ({len(by_mod[mod])})")
    out.append("")

    for mod, title, intro in CATEGORIES:
        items = by_mod.get(mod)
        if not items:
            continue
        out.append(f"## {title}\n")
        out.append(f"{intro}\n")
        for t in sorted(items, key=lambda x: x["name"]):
            tg = tag(t["desc"])
            head = f"### `{t['name']}`"
            if tg:
                head += f"  —  {tg}"
            out.append(head + "\n")
            out.append(short_desc(t["desc"]) + "\n")
            if t["params"]:
                out.append("**Parameters**\n")
                out.append("| Name | Type | Required | Default |")
                out.append("|------|------|----------|---------|")
                for p in t["params"]:
                    d = "" if p["default"] is None else f"`{p['default']}`"
                    out.append(f"| `{p['name']}` | {p['type']} | {'yes' if p['required'] else 'no'} | {d} |")
                out.append("")
            else:
                out.append("**Parameters:** none\n")
            out.append(f"**Returns:** {RETURNS.get(t['name'], 'See description.')}\n")

    Path("docs").mkdir(exist_ok=True)
    Path("docs/TOOLS.md").write_text("\n".join(out) + "\n")
    print(f"Wrote docs/TOOLS.md ({len(tools_meta)} tools)")


if __name__ == "__main__":
    main()
