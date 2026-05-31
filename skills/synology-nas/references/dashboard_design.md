# Dashboard design guide

Guidance for rendering a NAS dashboard as a **single self-contained HTML
artifact** from `get_overview` (and optionally other tool) output.

## Hard rules

- **One file, no network.** Inline all CSS. No `<script src>`, no CDN, no web
  fonts, no external images. Charts are **inline SVG** drawn from the data.
- **Static values.** Bake the tool values directly into the HTML. Do not invent
  numbers — use exactly what the tools returned. If a value is `null`, show "—".
- Keep it **legible and compact**: it should fit a laptop screen without
  horizontal scroll and reflow on mobile.

## Layout

1. **Header** — model + hostname, DSM version, uptime, and a health pill
   (green `system_ok`, amber otherwise). Optionally a temperature chip.
2. **Gauges row** — donut/arc gauges for **CPU total %** and **Memory used %**;
   small stat chips for network rx/tx.
3. **Storage** — one horizontal bar per volume (used vs total), with GB and %.
   Bar turns amber ≥ 75% and red ≥ 90%.
4. **Disks** — compact table: id, temp °C, status, S.M.A.R.T. (red if not
   "normal").
5. **Workloads** — tiles for packages running/total, containers running/total,
   VMs running/total, active downloads.
6. **Footer** — generated timestamp and "Source: Synology MCP".

## Color tokens (dark theme)

```
--bg:#0f1419  --panel:#1a2129  --panel2:#222c37  --text:#e6edf3
--muted:#8b98a5  --accent:#3b82f6  --ok:#22c55e  --warn:#f59e0b --bad:#ef4444
```

A light theme is fine too if the user prefers; keep the same structure.

## Thresholds for highlighting

| Metric | Amber | Red |
|--------|-------|-----|
| Volume used % | ≥ 75 | ≥ 90 |
| CPU total % | ≥ 70 | ≥ 90 |
| Memory used % | ≥ 80 | ≥ 95 |
| Disk temp °C | ≥ 45 | ≥ 55 |
| Disk S.M.A.R.T. / status | — | ≠ "normal" |
| Security scan | — | "outOfDate" / not "safe" |

## SVG gauge recipe

A donut gauge = two stacked circles using `stroke-dasharray`. For a circle of
radius `r`, circumference `C = 2·π·r`; the filled arc is `dasharray = pct/100·C`
then `C`. Rotate `-90deg` so it starts at the top. Color the arc by threshold.

Use `assets/dashboard_template.html` as the starting point and replace the
`{{PLACEHOLDER}}` tokens with real values.
