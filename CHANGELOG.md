# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0]

### Added
- Test suite (`tests/`) using `httpx.MockTransport` — runs in CI without a NAS.
- `ruff` linting and `pytest` steps in CI; CI status badge in the README.
- Friendly DSM error messages: common codes (105, 119, 403, …) now explain themselves
  instead of surfacing a bare number.
- Short TTL cache on `get_overview` so dashboard rendering doesn't repeat identical calls.

### Changed
- LICENSE holder set to the GitHub handle (no personal name).
- `scripts/gen_tools_doc.py` no longer hard-depends on FastMCP internals.

## [0.3.0]

### Added
- **Surveillance Station:** `get_surveillance_info`, `list_cameras`.
- **Synology Photos:** `list_photo_albums`.
- **Synology Drive:** `list_drive_connections`.
- **Time & region:** `get_time_settings` (timezone, NTP).
- **Resource history:** `get_resource_history` (Resource Monitor threshold events) for
  plotting trends in dashboards.
- Tool count is now **71 across 21 domains**.

## [0.2.0]

### Added
- **65 tools across 18 domains** (up from an initial monitoring + file set).
- Domains: system monitoring, health & activity, storage (volumes/pools/disks), files,
  packages & DSM updates, Docker (containers/images/projects/logs/stats), Virtual Machine
  Manager, Download Station, Hyper Backup, Task Scheduler, users/groups/shared folders,
  file & terminal services (SMB/AFP/NFS/FTP, SSH, SNMP), hardware (power/UPS/USB),
  security (DSM/auto-block/firewall/certificates), DDNS, QuickConnect, notifications.
- `get_overview` aggregate snapshot for building dashboards in one call.
- Bundled Claude skill (`skills/synology-nas`) with dashboard design guide and HTML template.
- Opt-in power control (`reboot_nas`, `shutdown_nas`, `install_dsm_update`) gated by
  `SYNOLOGY_ENABLE_POWER_CONTROL`.
- Configuration via environment variables / `.env`; 2FA support via a persistent
  trusted-device token (`bootstrap_2fa.py`).
- Enterprise docs: full tool reference, configuration guide, dashboards guide,
  contributing guide, examples, issue/PR templates and CI.

### Changed
- Refactored into a modular, config-driven package (`config.py`, `api.py`, `app.py`,
  `tools/`). No hard-coded credentials.

[0.4.0]: https://github.com/rafalr100/synology-mcp/releases/tag/v0.4.0
[0.3.0]: https://github.com/rafalr100/synology-mcp/releases/tag/v0.3.0
[0.2.0]: https://github.com/rafalr100/synology-mcp/releases/tag/v0.2.0
