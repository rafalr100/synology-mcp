"""Network-facing services: DDNS and QuickConnect (read-only)."""

from __future__ import annotations

from .. import api
from ..app import check, fmt, mcp


@mcp.tool()
async def get_ddns_status() -> str:
    """Get configured DDNS records (hostname, external IP, last update, status)."""
    data = check(await api.call("SYNO.Core.DDNS.Record", "list", version=1))
    records = [
        {
            "hostname": r.get("hostname"),
            "provider": r.get("provider") or r.get("id"),
            "ip": r.get("ip"),
            "status": r.get("status"),
            "enabled": r.get("enable"),
            "last_updated": r.get("lastupdated"),
        }
        for r in data.get("records", [])
    ]
    return fmt({"next_update": data.get("next_update_time"), "records": records})


@mcp.tool()
async def get_quickconnect_status() -> str:
    """Get QuickConnect configuration (enabled state and QuickConnect ID)."""
    data = check(await api.call("SYNO.Core.QuickConnect", "get", version=1))
    return fmt({
        "enabled": data.get("enabled"),
        "quickconnect_id": data.get("server_alias"),
        "server_id": data.get("server_id"),
        "region": data.get("region"),
        "domain": data.get("domain"),
    })
