# Dashboards

The server is designed to make **in-chat dashboards** easy. It does not render HTML
itself — instead it provides the data, and the LLM client renders a dashboard as an
artifact, guided by the bundled skill.

## How it works

1. **One-call data:** `get_overview` aggregates many subsystems (system identity, CPU/RAM
   load, network throughput, per-volume storage, per-disk health, and counts of packages,
   containers, VMs and downloads) into a single JSON payload. Sub-calls fail soft, so a
   single unavailable subsystem won't break the snapshot.
2. **Rendering:** the [`synology-nas` skill](../skills/synology-nas/SKILL.md) instructs
   the client to render a **self-contained HTML artifact** — inline CSS, inline SVG charts,
   no network calls — using the values from `get_overview`.
3. **Design:** see [dashboard_design.md](../skills/synology-nas/references/dashboard_design.md)
   for layout, color tokens and the highlight thresholds (e.g. volume ≥ 90% turns red),
   and [dashboard_template.html](../skills/synology-nas/assets/dashboard_template.html)
   for a ready starting point.

## Installing the skill

Copy the `skills/synology-nas` folder into your client's skills directory (for Claude
this is typically `~/.claude/skills/`), or point your skill configuration at it. The skill
triggers automatically when you mention your Synology NAS or ask for a dashboard.

## Building a focused dashboard

You can ask for specific panels, e.g. *“a storage-focused dashboard”* or *“a dashboard of
Docker and VMs”*. The client will combine `get_overview` with targeted tools
(`get_disk_info`, `list_containers`, `list_virtual_machines`, `get_system_logs`, …) and
lay out only the panels you asked for.
