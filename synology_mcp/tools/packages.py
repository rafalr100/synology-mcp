"""DSM updates and installed-package management."""

from __future__ import annotations

from .. import api
from ..app import check, fmt, mcp


@mcp.tool()
async def check_dsm_update() -> str:
    """Check whether a DSM (operating system) update is available for the NAS."""
    chk = check(await api.call("SYNO.Core.Upgrade.Server", "check", version=2))
    status = await api.call("SYNO.Core.Upgrade", "status", version=1)
    sdata = status.get("data", {}) if status.get("success") else {}
    setting = await api.call("SYNO.Core.Upgrade.Setting", "get", version=1)
    setdata = setting.get("data", {}) if setting.get("success") else {}

    update = chk.get("update", {})
    return fmt({
        "update_available": update.get("available", False),
        "new_version": update.get("version_string") or update.get("version"),
        "current_state": sdata.get("status"),
        "auto_download_enabled": setdata.get("auto_download"),
        "update_channel": setdata.get("upgrade_type"),
    })


@mcp.tool()
async def list_packages(running_only: bool = False) -> str:
    """
    List installed packages (apps) with their version and running status.

    Args:
        running_only: If True, only return packages that are currently running.
    """
    data = check(await api.call("SYNO.Core.Package", "list", version=2, additional='["status"]'))
    packages = []
    for p in data.get("packages", []):
        add = p.get("additional", {})
        status = add.get("status")
        if running_only and status != "running":
            continue
        packages.append({
            "id": p.get("id"),
            "name": p.get("name"),
            "version": p.get("version"),
            "status": status,
            "type": add.get("install_type") or "user",
        })
    packages.sort(key=lambda x: (x["status"] != "running", (x["name"] or "").lower()))
    return fmt({"total": len(packages), "packages": packages})


@mcp.tool()
async def set_package_state(package_id: str, action: str) -> str:
    """
    Start or stop an installed package. [control]

    Args:
        package_id: Package id from list_packages (e.g. "WebStation", "DownloadStation")
        action: "start" or "stop"
    """
    if action not in ("start", "stop"):
        raise ValueError("action must be 'start' or 'stop'")
    check(await api.call("SYNO.Core.Package.Control", action, version=1, id=package_id))
    return fmt({"package_id": package_id, "action": action, "ok": True})
