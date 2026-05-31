# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

[0.2.0]: https://github.com/OWNER/synology-mcp/releases/tag/v0.2.0
