"""Power and DSM-update control.

These operations are destructive and are DISABLED by default. Set
``SYNOLOGY_ENABLE_POWER_CONTROL=true`` to enable them.
"""

from __future__ import annotations

from .. import api, config
from ..app import check, fmt, mcp


def _require_power_control() -> None:
    if not config.ENABLE_POWER_CONTROL:
        raise RuntimeError(
            "Power control is disabled. Set SYNOLOGY_ENABLE_POWER_CONTROL=true "
            "in the environment to enable reboot / shutdown / DSM update."
        )


@mcp.tool()
async def reboot_nas() -> str:
    """Reboot the NAS. [control][power] Requires SYNOLOGY_ENABLE_POWER_CONTROL=true."""
    _require_power_control()
    check(await api.call("SYNO.Core.System", "reboot", version=1))
    return fmt({"action": "reboot", "ok": True})


@mcp.tool()
async def shutdown_nas() -> str:
    """Shut down (power off) the NAS. [control][power] Requires SYNOLOGY_ENABLE_POWER_CONTROL=true."""
    _require_power_control()
    check(await api.call("SYNO.Core.System", "shutdown", version=1))
    return fmt({"action": "shutdown", "ok": True})


@mcp.tool()
async def install_dsm_update() -> str:
    """
    Download and install an available DSM update, then reboot. [control][power]
    Requires SYNOLOGY_ENABLE_POWER_CONTROL=true. Check availability first with check_dsm_update.
    """
    _require_power_control()
    check(await api.call("SYNO.Core.Upgrade", "start", version=1))
    return fmt({"action": "install_dsm_update", "started": True})
