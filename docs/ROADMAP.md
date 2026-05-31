# Roadmap

Current coverage: **65 tools / 61 DSM APIs**. DSM exposes ~1200 API endpoints, but most
are internal or niche (clustering, LDAP/AD internals, C2 cloud, AI Console, low-level
certificate plumbing). The list below is the *practical* management surface still worth
wrapping, with the live-probe status against DSM 7.3.2.

Legend: ✅ available & ready to implement · ⚠️ available but needs method/field work ·
🔒 blocked by account privilege or NAS configuration.

## v0.3 — high-value, verified available

These returned data on a live DSM 7.3.2 and are the best next additions.

### Surveillance Station ✅
`SYNO.SurveillanceStation.Info` / `.Camera` work (camera count, camera list).
- `list_cameras` — name, model, status, recording state, IP
- `get_surveillance_info` — version, camera/licence counts
- `get_camera_snapshot` — return/save a still image
- `list_recordings`, `get_recent_events`

### Synology Photos ✅
`SYNO.Foto.Browse.Album` works (personal space).
- `list_photo_albums` — albums with item counts
- `get_photo_stats` — totals, storage used
- `search_photos` — by keyword/person/place

### Synology Drive ✅
`SYNO.SynologyDrive.Connection` works.
- `list_drive_connections` — connected clients/sessions
- `get_drive_stats` — sync activity overview

### Richer logs (Log Center) ✅
`SYNO.LogCenter.Log` works alongside the existing syslog tool.
- `get_connection_logs`, `get_file_transfer_logs`
- `query_logs` — filter by type/level/keyword/date range

### Time & region ✅
`SYNO.Core.Region.NTP` works.
- `get_time_settings` — timezone, NTP server, current time
- `set_ntp` *(control)* — enable/disable NTP, set server

### Resource history for dashboards ✅
`SYNO.ResourceMonitor.Log` returns threshold events over time.
- `get_resource_history` — recent CPU/RAM/IO threshold events to plot trends

## v0.4 — available, needs method/field discovery ⚠️

The APIs exist and the packages are installed, but the exact methods/parameters need
probing before they're reliable.

- **VPN Server** (`SYNO.VPNServer.*`) — connected accounts, protocol status (you have it
  installed; `Management.Account.list` returned “no such method”, so the method name needs
  confirming).
- **Cloud Sync** (`SYNO.CloudSync`) — task list and sync status (method names differ from
  the obvious guesses; needs probing).
- **Firewall rules** (`SYNO.Core.Security.Firewall.Rules`) — read/manage individual rules
  (the `get`/`list` methods need the right parameters/version).
- **Port forwarding / router** (`SYNO.Core.PortForwarding.*`) — only meaningful when a
  UPnP-capable router is paired.
- **Bandwidth control** (`SYNO.Core.BandwidthControl`) — per-protocol limits.
- **S.M.A.R.T. test logs & scrubbing control** (`SYNO.Storage.CGI.Smart` /
  `…Scrubbing`) — detailed attributes, run a test, start a scrub.
- **Send test notification** (`SYNO.Core.Notification.*`) — trigger a test mail/push.

## v0.5 — write/management, needs elevated privilege 🔒

Valuable but gated. They return permission errors with a normal admin session and may
require an account with specific privileges (or 2FA-elevated session).

- **User & group management** — create/modify/delete users, reset passwords, group
  membership (`SYNO.Core.User` create returned code 105 here).
- **Btrfs snapshots & replication** — list/create/delete share snapshots
  (`SYNO.Core.Share.Snapshot` returned 403).
- **Shared-folder permissions / ACL** — read and set per-user/group access.
- **Storage management** — create/expand volumes & pools, SSD cache (high-risk; behind a
  flag like power control).

## Cross-cutting improvements

- **MCP resources & prompts** — expose read-only data as MCP *resources* and ship ready
  *prompts* (e.g. “weekly health report”).
- **Caching** — short TTL cache for hot read calls to cut latency on dashboards.
- **Pagination helpers** — consistent paging across list tools.
- **Structured errors** — map common DSM error codes to friendly messages in-tool.
- **Unit tests** — record/replay DSM responses so CI can run without a NAS.
- **Optional power-control granularity** — separate flags per destructive action.

## Notes on scope

The goal is breadth of *useful management*, not 1:1 wrapping of all ~1200 endpoints. Niche
or internal APIs (clustering/HA, directory-service internals, C2 cloud, AI Console,
low-level KMIP/certificate plumbing) are intentionally out of scope unless requested.
