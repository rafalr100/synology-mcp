"""Aggregated snapshot for building dashboards.

``get_overview`` gathers data from many subsystems in a single call so an LLM
client can render a complete dashboard (as an HTML/React artifact) without many
round-trips. Sub-calls fail soft: a failing section is reported as null instead
of aborting the whole snapshot.
"""

from __future__ import annotations

import asyncio

from .. import api
from ..app import fmt, fmt_uptime, mcp, ttl_cache


async def _safe(api_name, method, version=1, **kw):
    try:
        r = await api.call(api_name, method, version=version, **kw)
        return r.get("data", {}) if r.get("success") else None
    except Exception:
        return None


@mcp.tool()
@ttl_cache(3.0)
async def get_overview() -> str:
    """
    Get a complete NAS snapshot in one call — ideal for building a dashboard.

    Aggregates: system identity, CPU/RAM/network load, per-volume storage,
    per-disk health, overall health, and counts of packages, containers, VMs,
    download tasks and recent log severities. Use this, then render a dashboard
    artifact from the returned JSON.
    """
    (info, util, storage_d, health, net, pkgs, containers, vms,
     downloads, logs, sec) = await asyncio.gather(
        _safe("SYNO.DSM.Info", "getinfo", 2),
        _safe("SYNO.Core.System.Utilization", "get", 1),
        _safe("SYNO.Storage.CGI.Storage", "load_info", 1),
        _safe("SYNO.Core.System.SystemHealth", "get", 1),
        _safe("SYNO.Core.Network", "get", 1),
        _safe("SYNO.Core.Package", "list", 2, additional='["status"]'),
        _safe("SYNO.Docker.Container", "list", 1, limit=-1, offset=0),
        _safe("SYNO.Virtualization.API.Guest", "list", 1),
        _safe("SYNO.DownloadStation2.Task", "list", 2),
        _safe("SYNO.Core.SyslogClient.Log", "list", 1, limit=1),
        _safe("SYNO.Core.SecurityScan.Status", "system_get", 1),
    )

    info = info or {}
    util = util or {}
    cpu = util.get("cpu", {})
    mem = util.get("memory", {})
    nets = util.get("network", [])
    total_net = next((n for n in nets if n.get("device") == "total"), {})
    total_real = mem.get("total_real", 0)
    avail_real = mem.get("avail_real", 0)

    volumes = []
    disks = []
    if storage_d:
        for v in storage_d.get("volumes", []):
            size = v.get("size", {})
            total = int(size.get("total", 0) or 0)
            used = int(size.get("used", 0) or 0)
            volumes.append({
                "id": v.get("id"), "status": v.get("status"),
                "total_gb": round(total / 1024 ** 3, 1),
                "used_gb": round(used / 1024 ** 3, 1),
                "used_pct": round(used / total * 100, 1) if total else None,
            })
        for d in storage_d.get("disks", []):
            disks.append({
                "id": d.get("id"), "temp_c": d.get("temp"),
                "status": d.get("status"), "smart": d.get("smart_status"),
            })

    pkg_list = (pkgs or {}).get("packages", [])
    running_pkgs = sum(1 for p in pkg_list if p.get("additional", {}).get("status") == "running")
    cont_list = (containers or {}).get("containers", [])
    running_cont = sum(1 for c in cont_list if c.get("status") == "running" or (c.get("state") or {}).get("Running"))
    vm_list = (vms or {}).get("guests", [])
    running_vms = sum(1 for g in vm_list if g.get("status") == "running")

    params = (health or {}).get("rule", {}).get("description", {}).get("description_params", [])
    health_status = params[0].replace("widget:", "") if params else "unknown"

    return fmt({
        "system": {
            "model": info.get("model"),
            "dsm_version": info.get("version_string"),
            "hostname": (net or {}).get("server_name"),
            "uptime": fmt_uptime(info.get("uptime", 0)),
            "temperature_c": info.get("temperature"),
            "temperature_warn": info.get("temperature_warn"),
            "ram_mb": info.get("ram"),
        },
        "health": {
            "status": health_status,
            "security_scan": (sec or {}).get("sysStatus"),
        },
        "load": {
            "cpu_user_pct": cpu.get("user_load"),
            "cpu_system_pct": cpu.get("system_load"),
            "cpu_total_pct": (cpu.get("user_load", 0) or 0) + (cpu.get("system_load", 0) or 0),
            "memory_used_pct": mem.get("real_usage"),
            "memory_used_mb": round((total_real - avail_real) / 1024) if total_real else None,
            "memory_total_mb": round(total_real / 1024) if total_real else None,
            "net_rx_kb_s": round(total_net.get("rx", 0) / 1024, 1),
            "net_tx_kb_s": round(total_net.get("tx", 0) / 1024, 1),
        },
        "storage": {"volumes": volumes, "disks": disks},
        "counts": {
            "packages_total": len(pkg_list), "packages_running": running_pkgs,
            "containers_total": len(cont_list), "containers_running": running_cont,
            "vms_total": len(vm_list), "vms_running": running_vms,
            "downloads_active": (downloads or {}).get("total", 0),
        },
    })
