"""Administrative read tools: users, groups, shares, logs, security scan."""

from __future__ import annotations

from .. import api
from ..app import check, fmt, mcp, ts


@mcp.tool()
async def list_users() -> str:
    """List local user accounts with description, email, 2FA and status."""
    data = check(await api.call(
        "SYNO.Core.User", "list", version=1,
        additional='["description","email","expired","2fa_status"]',
    ))
    users = [
        {
            "name": u.get("name"),
            "description": u.get("description") or None,
            "email": u.get("email") or None,
            "expired": u.get("expired"),
            "2fa": u.get("2fa_status"),
        }
        for u in data.get("users", [])
    ]
    return fmt({"total": data.get("total", len(users)), "users": users})


@mcp.tool()
async def list_groups() -> str:
    """List local user groups."""
    data = check(await api.call("SYNO.Core.Group", "list", version=1))
    groups = [{"name": g.get("name"), "description": g.get("description") or None}
              for g in data.get("groups", [])]
    return fmt({"total": data.get("total", len(groups)), "groups": groups})


@mcp.tool()
async def list_shared_folders() -> str:
    """List shared folders with their volume location and description (admin view)."""
    data = check(await api.call(
        "SYNO.Core.Share", "list", version=1,
        additional='["hidden","encryption","is_aclmode"]',
    ))
    shares = [
        {
            "name": s.get("name"),
            "volume": s.get("vol_path"),
            "description": s.get("desc") or None,
            "encrypted": bool(s.get("encryption")),
            "usb_share": s.get("is_usb_share"),
        }
        for s in data.get("shares", [])
    ]
    return fmt({"total": data.get("total", len(shares)), "shares": shares})


@mcp.tool()
async def create_shared_folder(name: str, volume: str = "/volume1", description: str = "") -> str:
    """
    Create a new shared folder. [control]

    Args:
        name: Name of the shared folder
        volume: Volume path to create it on (default /volume1)
        description: Optional description
    """
    import json as _json
    check(await api.call(
        "SYNO.Core.Share", "create", version=1,
        name=name,
        shareinfo=_json.dumps({"name": name, "vol_path": volume, "desc": description}),
    ))
    return fmt({"created": name, "volume": volume})


@mcp.tool()
async def delete_shared_folder(name: str) -> str:
    """
    Delete a shared folder (and its contents). [control]

    Args:
        name: Name of the shared folder to delete
    """
    check(await api.call("SYNO.Core.Share", "delete", version=1, name=name))
    return fmt({"deleted": name})


@mcp.tool()
async def get_system_logs(limit: int = 30, level: str | None = None) -> str:
    """
    Get recent system log entries.

    Args:
        limit: Max entries to return (default 30)
        level: Optional filter — "info", "warning" or "error"
    """
    data = check(await api.call("SYNO.Core.SyslogClient.Log", "list", version=1, limit=limit))
    items = data.get("items", [])
    if level:
        items = [i for i in items if i.get("level") == level]
    logs = [
        {"time": i.get("time"), "level": i.get("level"), "type": i.get("logtype"),
         "who": i.get("who"), "message": i.get("descr")}
        for i in items
    ]
    return fmt({
        "counts": {"info": data.get("infoCount"), "warning": data.get("warnCount"),
                   "error": data.get("errorCount")},
        "total": data.get("total"),
        "logs": logs,
    })


@mcp.tool()
async def get_security_scan_status() -> str:
    """Get the result of the Security Advisor scan (malware, network, system, updates)."""
    data = check(await api.call("SYNO.Core.SecurityScan.Status", "system_get", version=1))
    categories = {}
    for cat, info in data.get("items", {}).items():
        categories[cat] = {
            "severity": info.get("failSeverity"),
            "progress": info.get("progress"),
            "issues": {k: v for k, v in (info.get("fail") or {}).items() if v},
        }
    return fmt({
        "overall_status": data.get("sysStatus"),
        "last_scan": ts(data.get("lastScanTime")) or data.get("lastScanTime"),
        "categories": categories,
    })
