# Tool Reference

The Synology MCP server exposes **71 tools**. Tools tagged `control` change NAS state; tools tagged `power` are destructive and disabled unless `SYNOLOGY_ENABLE_POWER_CONTROL=true`.

## Contents

- [Dashboard](#dashboard) (1)
- [System Monitoring](#system-monitoring) (4)
- [System Health & Activity](#system-health-activity) (4)
- [Storage](#storage) (3)
- [Files](#files) (12)
- [Packages & DSM Updates](#packages-dsm-updates) (3)
- [Docker / Container Manager](#docker-container-manager) (6)
- [Virtual Machine Manager](#virtual-machine-manager) (2)
- [Surveillance Station](#surveillance-station) (2)
- [Synology Photos](#synology-photos) (1)
- [Synology Drive](#synology-drive) (1)
- [Download Station](#download-station) (3)
- [Backup](#backup) (2)
- [Task Scheduler](#task-scheduler) (2)
- [Users, Groups & Shared Folders](#users-groups-shared-folders) (7)
- [File & Terminal Services](#file-terminal-services) (4)
- [Hardware](#hardware) (4)
- [Security & Certificates](#security-certificates) (4)
- [Network Services](#network-services) (2)
- [Notifications](#notifications) (1)
- [Power Control (opt-in)](#power-control-opt-in) (3)

## Dashboard

One-call aggregate snapshot for building visual dashboards.

### `get_overview`

Get a complete NAS snapshot in one call — ideal for building a dashboard.

**Parameters:** none

**Returns:** A complete snapshot: `system`, `health`, `load`, `storage` (volumes+disks) and `counts` (packages/containers/VMs/downloads). Ideal input for a dashboard.

## System Monitoring

Identity, live load and network information.

### `get_network_info`

Get network interfaces with IP addresses, link speed and status, plus gateway/DNS.

**Parameters:** none

**Returns:** Hostname, gateway, primary/secondary DNS, and a list of interfaces with IP, mask, type, link speed and status.

### `get_resource_history`

Get recent Resource Monitor threshold events (CPU/RAM/IO spikes over time).

**Parameters**

| Name | Type | Required | Default |
|------|------|----------|---------|
| `limit` | integer | no | `25` |

**Returns:** Recent Resource Monitor threshold events (time, level, description) for plotting trends.

### `get_resource_usage`

Get real-time CPU usage, memory usage and network throughput.

**Parameters:** none

**Returns:** CPU load breakdown and 1/5/15-min averages, memory used/available/percent, swap usage, and network rx/tx (KB/s).

### `get_system_info`

Get NAS model, DSM version, hostname, uptime, RAM, temperature and serial number.

**Parameters:** none

**Returns:** Model, DSM version, hostname, uptime, RAM (MB), serial, temperature (°C) and system time.

## System Health & Activity

Overall health, active connections and processes.

### `get_active_connections`

List currently active connections to the NAS (who, from where, which protocol).

**Parameters:** none

**Returns:** List of current connections: user, source IP, protocol, time and whether it is the current session.

### `get_system_health`

Get overall system health: status, uptime, reboot-required flag and fan status.

**Parameters:** none

**Returns:** Overall status (e.g. `system_ok`), uptime, reboot-required flag, fan status and disk-temperature alarm.

### `get_time_settings`

Get the NAS time, timezone and NTP synchronization settings.

**Parameters:** none

**Returns:** Current NAS time, timezone, and whether NTP sync is enabled plus the NTP server.

### `list_processes`

List top running processes by CPU or memory usage.

**Parameters**

| Name | Type | Required | Default |
|------|------|----------|---------|
| `top` | integer | no | `15` |
| `sort_by` | string | no | `cpu` |

**Returns:** Top processes sorted by CPU or memory, each with pid, command, CPU % and memory (MB).

## Storage

Volumes, storage pools and physical disks.

### `get_disk_info`

Get individual disk details: model, temperature, health (S.M.A.R.T.) and status.

**Parameters:** none

**Returns:** Per-disk model, vendor, size (GB), status, temperature (°C), S.M.A.R.T. status, type, SSD life and pool membership.

### `get_storage_info`

Get storage volumes: RAID type, filesystem, used/free space and health status.

**Parameters:** none

**Returns:** Per-volume RAID type, filesystem, total/used/free (GB), used % and status.

### `get_storage_pools`

Get storage pools with RAID type, status and data-scrubbing state.

**Parameters:** none

**Returns:** Per-pool RAID type, status, drive type, disk count and data-scrubbing status/last run.

## Files

Browse, inspect, search and manage files via File Station.

### `copy_move_item`  —  `control`

Copy or move files/folders into an existing destination folder.

**Parameters**

| Name | Type | Required | Default |
|------|------|----------|---------|
| `paths` | string | yes |  |
| `dest_folder` | string | yes |  |
| `move` | boolean | no | `False` |
| `overwrite` | boolean | no | `False` |

**Returns:** Action (copy/move) and completion status.

### `create_folder`

Create a new folder.

**Parameters**

| Name | Type | Required | Default |
|------|------|----------|---------|
| `parent_path` | string | yes |  |
| `name` | string | yes |  |

**Returns:** Confirmation with the created folder path.

### `create_share_link`  —  `control`

Create a public sharing link for a file or folder.

**Parameters**

| Name | Type | Required | Default |
|------|------|----------|---------|
| `path` | string | yes |  |
| `password` | any | no |  |

**Returns:** The created public link(s): URL and link id.

### `delete_item`  —  `control`

Delete files or folders.

**Parameters**

| Name | Type | Required | Default |
|------|------|----------|---------|
| `paths` | string | yes |  |
| `recursive` | boolean | no | `True` |

**Returns:** Confirmation and the list of deleted paths.

### `extract_archive`  —  `control`

Extract an archive (ZIP, etc.) into a destination folder.

**Parameters**

| Name | Type | Required | Default |
|------|------|----------|---------|
| `archive_path` | string | yes |  |
| `dest_folder` | string | yes |  |

**Returns:** Destination folder and completion status.

### `get_directory_size`

Calculate the total size and item count of a folder (recursively).

**Parameters**

| Name | Type | Required | Default |
|------|------|----------|---------|
| `path` | string | yes |  |

**Returns:** Recursive total size (bytes and GB) plus file and directory counts for a folder.

### `get_file_info`

Get detailed info (size, owner, timestamps) for one or more files/folders.

**Parameters**

| Name | Type | Required | Default |
|------|------|----------|---------|
| `paths` | string | yes |  |

**Returns:** Detailed metadata for one or more paths: real path, size, owner, modified/created/accessed times.

### `get_file_md5`

Compute the MD5 checksum of a file.

**Parameters**

| Name | Type | Required | Default |
|------|------|----------|---------|
| `path` | string | yes |  |

**Returns:** The MD5 checksum of a file.

### `list_files`

List files and folders at a given path.

**Parameters**

| Name | Type | Required | Default |
|------|------|----------|---------|
| `path` | string | yes |  |
| `limit` | integer | no | `100` |
| `offset` | integer | no | `0` |
| `sort_by` | string | no | `name` |
| `sort_direction` | string | no | `asc` |
| `pattern` | any | no |  |

**Returns:** Directory listing: name, path, is_dir, size (bytes), modified and created timestamps. Supports sorting, paging and a wildcard filter.

### `list_shares`

List all available shared folders (File Station view).

**Parameters:** none

**Returns:** Shared folders visible in File Station: name, path, real path and read-only flag.

### `rename_item`

Rename a file or folder.

**Parameters**

| Name | Type | Required | Default |
|------|------|----------|---------|
| `path` | string | yes |  |
| `new_name` | string | yes |  |

**Returns:** Confirmation with the renamed item.

### `search_files`

Search for files by name pattern within a folder.

**Parameters**

| Name | Type | Required | Default |
|------|------|----------|---------|
| `folder_path` | string | yes |  |
| `pattern` | string | yes |  |
| `recursive` | boolean | no | `True` |
| `limit` | integer | no | `50` |

**Returns:** Files matching a name pattern under a folder (recursive optional): name, path, is_dir, size, modified.

## Packages & DSM Updates

Installed packages and DSM operating-system updates.

### `check_dsm_update`

Check whether a DSM (operating system) update is available for the NAS.

**Parameters:** none

**Returns:** Whether a DSM update is available, the new version (if any), current state, auto-download flag and update channel.

### `list_packages`

List installed packages (apps) with their version and running status.

**Parameters**

| Name | Type | Required | Default |
|------|------|----------|---------|
| `running_only` | boolean | no | `False` |

**Returns:** Installed packages with id, name, version, running status and type. Optionally only running ones.

### `set_package_state`  —  `control`

Start or stop an installed package.

**Parameters**

| Name | Type | Required | Default |
|------|------|----------|---------|
| `package_id` | string | yes |  |
| `action` | string | yes |  |

**Returns:** Confirmation of the start/stop action on a package.

## Docker / Container Manager

Containers, images, projects and live stats.

### `get_container_logs`

Get recent log lines for a Docker container.

**Parameters**

| Name | Type | Required | Default |
|------|------|----------|---------|
| `name` | string | yes |  |
| `lines` | integer | no | `50` |

**Returns:** Recent log lines for a container (time, stream, text).

### `get_container_stats`

Get live CPU / memory / network / disk usage for a running container.

**Parameters**

| Name | Type | Required | Default |
|------|------|----------|---------|
| `name` | string | yes |  |

**Returns:** Live CPU %, memory (MB) and raw resource counters for a running container.

### `list_containers`

List all Docker / Container Manager containers with their state and image.

**Parameters:** none

**Returns:** All containers with name, image, running flag, state, exit code, start/finish times.

### `list_docker_images`

List Docker images stored on the NAS, including whether an update is available.

**Parameters:** none

**Returns:** Stored images: repository, tags, size (MB), creation time and whether an update is available.

### `list_docker_projects`

List Docker Compose / Container Manager projects.

**Parameters:** none

**Returns:** Container Manager / Compose projects: id, name, status, path, container count and creation time.

### `set_container_state`  —  `control`

Start, stop or restart a Docker container.

**Parameters**

| Name | Type | Required | Default |
|------|------|----------|---------|
| `name` | string | yes |  |
| `action` | string | yes |  |

**Returns:** Confirmation of start/stop/restart on a container.

## Virtual Machine Manager

Virtual machine guests.

### `list_virtual_machines`

List Virtual Machine Manager guests with their state and resource allocation.

**Parameters:** none

**Returns:** VMM guests with name, status, vCPUs, RAM (MB), storage, autorun and description.

### `set_vm_state`  —  `control`

Power a virtual machine on or off.

**Parameters**

| Name | Type | Required | Default |
|------|------|----------|---------|
| `name` | string | yes |  |
| `action` | string | yes |  |

**Returns:** Confirmation of poweron/poweroff/shutdown/restart on a VM.

## Surveillance Station

Cameras and Surveillance Station info.

### `get_surveillance_info`

Get Surveillance Station info: version, camera count and licence usage.

**Parameters:** none

**Returns:** Surveillance Station version, cameras in use, licences and max camera support.

### `list_cameras`

List Surveillance Station cameras with model, IP and status.

**Parameters:** none

**Returns:** Cameras with id, name, vendor, model, IP, MAC, status code and online flag.

## Synology Photos

Photo albums (personal space).

### `list_photo_albums`

List albums in Synology Photos (personal space).

**Parameters**

| Name | Type | Required | Default |
|------|------|----------|---------|
| `limit` | integer | no | `50` |
| `offset` | integer | no | `0` |

**Returns:** Albums in Synology Photos (personal space): id, name, item count, shared flag and type.

## Synology Drive

Drive client connections.

### `list_drive_connections`

List Synology Drive client connections (devices syncing with the NAS).

**Parameters:** none

**Returns:** Synology Drive client connections: client name, IP, type, version, status, location, login and last-auth times.

## Download Station

Download tasks (HTTP/FTP/magnet/torrent).

### `add_download`  —  `control`

Add a new download task from a URL or magnet link.

**Parameters**

| Name | Type | Required | Default |
|------|------|----------|---------|
| `url` | string | yes |  |
| `destination` | string | yes |  |

**Returns:** Confirmation of the added URL and its destination.

### `list_downloads`

List Download Station tasks with progress, size and transfer speed.

**Parameters:** none

**Returns:** Download tasks with id, title, type, status, size (MB), progress % and up/down speed (KB/s).

### `manage_download`  —  `control`

Pause, resume or delete download tasks.

**Parameters**

| Name | Type | Required | Default |
|------|------|----------|---------|
| `task_ids` | string | yes |  |
| `action` | string | yes |  |

**Returns:** Confirmation of pause/resume/delete on the given task ids.

## Backup

Hyper Backup tasks.

### `list_backup_tasks`

List Hyper Backup tasks with their current state and target.

**Parameters:** none

**Returns:** Hyper Backup tasks with id, name, state, status, target, type and encryption flag.

### `run_backup_task`  —  `control`

Start a Hyper Backup task immediately.

**Parameters**

| Name | Type | Required | Default |
|------|------|----------|---------|
| `task_id` | integer | yes |  |

**Returns:** Confirmation that the backup task was started.

## Task Scheduler

Scheduled tasks (cron jobs, scripts, scheduled backups).

### `list_scheduled_tasks`

List scheduled tasks (cron jobs, scripts, scheduled backups, etc.).

**Parameters:** none

**Returns:** Scheduled tasks with id, name, type, enabled flag, owner, next run and can-run-now flag.

### `run_scheduled_task`  —  `control`

Trigger a scheduled task to run immediately.

**Parameters**

| Name | Type | Required | Default |
|------|------|----------|---------|
| `task_id` | integer | yes |  |

**Returns:** Confirmation that the task was triggered.

## Users, Groups & Shared Folders

Accounts, groups, shared folders, logs and security scan.

### `create_shared_folder`  —  `control`

Create a new shared folder.

**Parameters**

| Name | Type | Required | Default |
|------|------|----------|---------|
| `name` | string | yes |  |
| `volume` | string | no | `/volume1` |
| `description` | string | no | `` |

**Returns:** Confirmation with the created folder name and volume.

### `delete_shared_folder`  —  `control`

Delete a shared folder (and its contents).

**Parameters**

| Name | Type | Required | Default |
|------|------|----------|---------|
| `name` | string | yes |  |

**Returns:** Confirmation of the deleted folder.

### `get_security_scan_status`

Get the result of the Security Advisor scan (malware, network, system, updates).

**Parameters:** none

**Returns:** Security Advisor result per category (malware, network, system, update) with severity and issue counts.

### `get_system_logs`

Get recent system log entries.

**Parameters**

| Name | Type | Required | Default |
|------|------|----------|---------|
| `limit` | integer | no | `30` |
| `level` | any | no |  |

**Returns:** Recent log entries (time, level, type, who, message) plus info/warning/error counts.

### `list_groups`

List local user groups.

**Parameters:** none

**Returns:** Local groups with name and description.

### `list_shared_folders`

List shared folders with their volume location and description (admin view).

**Parameters:** none

**Returns:** Shared folders (admin view): name, volume, description, encryption and USB-share flags.

### `list_users`

List local user accounts with description, email, 2FA and status.

**Parameters:** none

**Returns:** Local accounts with name, description, email, expiry and 2FA status.

## File & Terminal Services

SMB/AFP/NFS/FTP, SSH/Telnet and SNMP.

### `get_file_services`

Get the enabled state and key settings of SMB, AFP, NFS and FTP file services.

**Parameters:** none

**Returns:** Enabled state and key settings of SMB, AFP, NFS and FTP.

### `get_snmp_settings`

Get SNMP service settings.

**Parameters:** none

**Returns:** SNMP enabled state, versions, location and contact.

### `get_terminal_settings`

Get SSH / Telnet terminal access settings.

**Parameters:** none

**Returns:** SSH and Telnet enabled state and SSH port.

### `set_file_service`  —  `control`

Enable or disable a file-sharing protocol.

**Parameters**

| Name | Type | Required | Default |
|------|------|----------|---------|
| `service` | string | yes |  |
| `enabled` | boolean | yes |  |

**Returns:** Confirmation of enabling/disabling a file-sharing protocol.

## Hardware

Power, hibernation, UPS and USB devices.

### `get_hibernation_settings`

Get disk hibernation (power-saving) settings.

**Parameters:** none

**Returns:** Disk idle time before hibernation and auto-power-off settings.

### `get_power_settings`

Get power-related hardware settings: power recovery, LED brightness, beep and power schedule.

**Parameters:** none

**Returns:** Power-recovery, Wake-on-LAN, LED brightness, beep and scheduled power task counts.

### `get_ups_status`

Get UPS (uninterruptible power supply) status and configuration.

**Parameters:** none

**Returns:** UPS enabled state, mode, model, battery charge %, runtime and connection status.

### `list_usb_devices`

List USB devices connected to the NAS.

**Parameters:** none

**Returns:** Connected USB devices (id and title).

## Security & Certificates

DSM security, auto-block, firewall and TLS certificates.

### `get_autoblock_settings`

Get the auto-block policy (block IPs after failed login attempts).

**Parameters:** none

**Returns:** Auto-block policy: enabled, attempts, window (minutes) and block expiry (days).

### `get_firewall_status`

Get firewall profile information.

**Parameters:** none

**Returns:** Firewall profile names.

### `get_security_settings`

Get DSM security settings (session timeout, CSRF protection, IP checking).

**Parameters:** none

**Returns:** DSM session timeout, CSRF protection, IP-checking and stay-signed-in options.

### `list_certificates`

List installed TLS/SSL certificates with validity dates and assigned services.

**Parameters:** none

**Returns:** Installed TLS certificates: description, subject, issuer, validity dates, default/broken/renewable flags and assigned-service count.

## Network Services

DDNS and QuickConnect.

### `get_ddns_status`

Get configured DDNS records (hostname, external IP, last update, status).

**Parameters:** none

**Returns:** DDNS records: hostname, provider, external IP, status, enabled flag and last update.

### `get_quickconnect_status`

Get QuickConnect configuration (enabled state and QuickConnect ID).

**Parameters:** none

**Returns:** QuickConnect enabled state, ID, server id, region and domain.

## Notifications

E-mail notification settings.

### `get_notification_settings`

Get e-mail notification settings (enabled state, sender, SMTP).

**Parameters:** none

**Returns:** E-mail notification enabled state, sender, SMTP server and OAuth flag.

## Power Control (opt-in)

Reboot, shutdown and DSM update — disabled unless enabled.

### `install_dsm_update`  —  `control` `power`

Download and install an available DSM update, then reboot.

**Parameters:** none

**Returns:** Confirmation that a DSM update install was started (requires power control enabled).

### `reboot_nas`  —  `control` `power`

Reboot the NAS.  Requires SYNOLOGY_ENABLE_POWER_CONTROL=true.

**Parameters:** none

**Returns:** Confirmation that a reboot was issued (requires power control enabled).

### `shutdown_nas`  —  `control` `power`

Shut down (power off) the NAS.  Requires SYNOLOGY_ENABLE_POWER_CONTROL=true.

**Parameters:** none

**Returns:** Confirmation that a shutdown was issued (requires power control enabled).

