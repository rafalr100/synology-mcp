"""Synology Drive Server tools."""

from __future__ import annotations

from .. import api
from ..app import check, fmt, mcp


@mcp.tool()
async def list_drive_connections() -> str:
    """List Synology Drive client connections (devices syncing with the NAS)."""
    data = check(await api.call("SYNO.SynologyDrive.Connection", "list", version=1))
    items = []
    for c in data.get("items", []):
        items.append({
            "client_name": c.get("client_name"),
            "ip": c.get("client_ip"),
            "type": c.get("client_type"),
            "version": c.get("client_version"),
            "status": c.get("client_status"),
            "location": c.get("client_location") or None,
            "login_time": c.get("login_time"),
            "last_auth_time": c.get("last_auth_time"),
        })
    return fmt({"total": data.get("total", len(items)), "connections": items})
