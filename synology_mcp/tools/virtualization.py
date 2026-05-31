"""Virtual Machine Manager tools."""

from __future__ import annotations

from .. import api
from ..app import check, fmt, mcp

_GUEST_API = "SYNO.Virtualization.API.Guest"


@mcp.tool()
async def list_virtual_machines() -> str:
    """List Virtual Machine Manager guests with their state and resource allocation."""
    data = check(await api.call(_GUEST_API, "list", version=1))
    guests = []
    for g in data.get("guests", []):
        guests.append({
            "name": g.get("guest_name"),
            "status": g.get("status"),
            "vcpus": g.get("vcpu_num"),
            "ram_mb": g.get("vram_size"),
            "storage": g.get("storage_name"),
            "autorun": g.get("autorun"),
            "description": g.get("description") or None,
        })
    guests.sort(key=lambda x: (x["status"] != "running", (x["name"] or "").lower()))
    return fmt({"total": len(guests), "guests": guests})


@mcp.tool()
async def set_vm_state(name: str, action: str) -> str:
    """
    Power a virtual machine on or off. [control]

    Args:
        name: VM name (from list_virtual_machines)
        action: "poweron", "poweroff" (force off), "shutdown" (graceful) or "restart"
    """
    methods = {"poweron": "poweron", "poweroff": "poweroff",
               "shutdown": "shutdown", "restart": "restart"}
    if action not in methods:
        raise ValueError("action must be 'poweron', 'poweroff', 'shutdown' or 'restart'")
    check(await api.call(_GUEST_API + ".Action", methods[action], version=1, guest_name=name))
    return fmt({"vm": name, "action": action, "ok": True})
