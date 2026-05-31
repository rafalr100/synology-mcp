---
name: synology-nas
description: >-
  Monitor and manage a Synology DSM 7 NAS through the Synology MCP server, and
  build rich visual dashboards from its data. Use when the user asks about their
  Synology NAS, DiskStation, or DS-series device — system health, CPU/RAM,
  storage and disk health, Docker containers, virtual machines, packages, DSM
  updates, Download Station, Hyper Backup, shared folders, users, logs,
  certificates, network services — or asks to "show a dashboard", "visualize",
  "give me an overview", or "check the status" of the NAS. Requires the
  `synology` MCP server to be connected.
---

# Synology NAS

This skill helps you operate the **Synology MCP server** (server name: `synology`)
and turn its data into clean, useful answers and dashboards.

## When to use this skill

Trigger whenever the user refers to their **Synology NAS / DiskStation / DSM**
and wants to inspect or manage it, or asks for a **dashboard / overview /
visualization** of NAS data.

## Tool map

The MCP server exposes tools grouped by domain. Prefer the **aggregate** tool for
overviews; use specific tools for detail or actions.

| Goal | Tool(s) |
|------|---------|
| One-shot snapshot for a dashboard | `get_overview` |
| System identity / uptime / temp | `get_system_info` |
| Live CPU / RAM / network | `get_resource_usage` |
| Overall health, fans, reboot flag | `get_system_health` |
| Volumes / pools / disks (S.M.A.R.T.) | `get_storage_info`, `get_storage_pools`, `get_disk_info` |
| Network / DDNS / QuickConnect | `get_network_info`, `get_ddns_status`, `get_quickconnect_status` |
| Files | `list_shares`, `list_files`, `get_file_info`, `get_directory_size`, `search_files`, `get_file_md5` |
| File actions | `create_folder`, `rename_item`, `copy_move_item`, `delete_item`, `extract_archive`, `create_share_link` |
| Packages & DSM updates | `list_packages`, `check_dsm_update`, `set_package_state` |
| Docker | `list_containers`, `get_container_logs`, `get_container_stats`, `list_docker_images`, `list_docker_projects`, `set_container_state` |
| Virtual machines | `list_virtual_machines`, `set_vm_state` |
| Download Station | `list_downloads`, `add_download`, `manage_download` |
| Backup | `list_backup_tasks`, `run_backup_task` |
| Scheduled tasks | `list_scheduled_tasks`, `run_scheduled_task` |
| Users / groups / shares | `list_users`, `list_groups`, `list_shared_folders`, `create_shared_folder`, `delete_shared_folder` |
| Services | `get_file_services`, `set_file_service`, `get_terminal_settings`, `get_snmp_settings` |
| Hardware | `get_power_settings`, `get_hibernation_settings`, `get_ups_status`, `list_usb_devices` |
| Security | `get_security_settings`, `get_autoblock_settings`, `get_firewall_status`, `list_certificates` |
| Logs / notifications | `get_system_logs`, `get_active_connections`, `get_security_scan_status`, `get_notification_settings` |
| Power (opt-in) | `reboot_nas`, `shutdown_nas`, `install_dsm_update` |

## Operating principles

1. **For overviews and dashboards, call `get_overview` first.** It returns
   system, load, storage, disks and counts in a single round-trip. Only call
   specific tools afterwards if the user wants more detail.
2. **Confirm before destructive actions.** Tools whose descriptions contain
   `[control]` change NAS state (start/stop containers, delete files, manage
   downloads, toggle services). Briefly confirm intent before calling them.
   `[power]` tools (reboot/shutdown/update) are extra-sensitive and may be
   disabled server-side.
3. **Summarize, don't dump.** The tools return JSON. Translate it into a concise,
   human answer; surface anything abnormal (high temp, >85% volume usage,
   failing S.M.A.R.T., stopped expected services, security scan "outOfDate",
   external-IP logins).
4. **Respect units.** Memory/process figures are already converted in tool
   output; timestamps are UTC strings.

## Building dashboards

When the user asks for a dashboard, status board, or visualization:

1. Call `get_overview` (plus any specific tools the request implies, e.g.
   `get_system_logs` for a "recent activity" panel).
2. Render a **single self-contained HTML artifact** — no external scripts or
   network calls; inline CSS and inline SVG for any charts/gauges.
3. Follow the design guidance in **`references/dashboard_design.md`** and use
   **`assets/dashboard_template.html`** as a starting point. Replace the
   placeholder values with real data from the tool results.
4. Highlight problem states in amber/red (e.g. volume >85%, temp warning,
   failing disk, security "outOfDate").

Keep dashboards readable: a header with model/hostname/uptime, status tiles,
gauges for CPU/RAM, a storage bar per volume, a disk-health table, and tiles for
container/VM/package counts.

## Notes

- Some tools require an administrator account; non-admins receive a permission
  error — report it plainly.
- A few capabilities depend on the NAS configuration (e.g. UPS, DDNS, VMM, Docker
  must be installed/enabled). If a tool reports the feature is unavailable, say so.
