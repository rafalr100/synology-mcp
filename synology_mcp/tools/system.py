"""System health, active connections and processes."""

from __future__ import annotations

from .. import api
from ..app import check, fmt, mcp


@mcp.tool()
async def get_system_health() -> str:
    """Get overall system health: status, uptime, reboot-required flag and fan status."""
    health = check(await api.call("SYNO.Core.System.SystemHealth", "get", version=1))
    reboot = await api.call("SYNO.Core.Hardware.NeedReboot", "get", version=1)
    fan = await api.call("SYNO.Core.Hardware.FanSpeed", "get", version=1)
    fdata = fan.get("data", {}) if fan.get("success") else {}

    params = health.get("rule", {}).get("description", {}).get("description_params", [])
    status = params[0].replace("widget:", "") if params else "unknown"
    return fmt({
        "status": status,
        "uptime": health.get("uptime"),
        "reboot_required": reboot.get("data", {}).get("needReboot") if reboot.get("success") else None,
        "fan_status": fdata.get("cool_fan"),
        "disk_temp_alarm": fdata.get("all_disk_temp_fail"),
    })


@mcp.tool()
async def get_active_connections() -> str:
    """List currently active connections to the NAS (who, from where, which protocol)."""
    data = check(await api.call("SYNO.Core.CurrentConnection", "list", version=1))
    conns = []
    for c in data.get("items", []):
        conns.append({
            "user": c.get("who") or c.get("descr"),
            "from": c.get("from"),
            "protocol": c.get("protocol") or c.get("type"),
            "time": c.get("time"),
            "current_session": c.get("is_current_connected"),
        })
    return fmt({"total": data.get("total", len(conns)), "connections": conns})


@mcp.tool()
async def list_processes(top: int = 15, sort_by: str = "cpu") -> str:
    """
    List top running processes by CPU or memory usage.

    Args:
        top: Number of processes to return (default 15)
        sort_by: "cpu" or "mem" (default cpu)
    """
    data = check(await api.call("SYNO.Core.System.Process", "list", version=1))
    procs = data.get("process", data.get("items", []))
    key = "cpu" if sort_by == "cpu" else "mem"
    procs.sort(key=lambda p: p.get(key) or 0, reverse=True)
    out = [
        {
            "pid": p.get("pid"),
            "command": p.get("command") or p.get("name"),
            "cpu_pct": p.get("cpu"),
            "mem_mb": round((p.get("mem") or 0) / 1024, 1),  # 'mem' is RSS in KB
        }
        for p in procs[:top]
    ]
    return fmt({"sorted_by": sort_by, "processes": out})
