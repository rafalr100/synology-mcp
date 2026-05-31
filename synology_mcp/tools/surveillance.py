"""Surveillance Station tools."""

from __future__ import annotations

from .. import api
from ..app import check, fmt, mcp


@mcp.tool()
async def get_surveillance_info() -> str:
    """Get Surveillance Station info: version, camera count and licence usage."""
    data = check(await api.call("SYNO.SurveillanceStation.Info", "GetInfo", version=1))
    v = data.get("version", {})
    version = f"{v.get('major')}.{v.get('minor')}.{v.get('small')}-{v.get('build')}" if isinstance(v, dict) else v
    return fmt({
        "version": version,
        "cameras_used": data.get("cameraNumber"),
        "licences": data.get("liscenseNumber"),
        "max_cameras": data.get("maxCameraSupport"),
    })


@mcp.tool()
async def list_cameras() -> str:
    """List Surveillance Station cameras with model, IP and status."""
    data = check(await api.call("SYNO.SurveillanceStation.Camera", "List", version=9))
    cameras = []
    for cam in data.get("cameras", []):
        status = cam.get("status")
        cameras.append({
            "id": cam.get("id"),
            "name": cam.get("newName") or cam.get("name"),
            "vendor": cam.get("vendor"),
            "model": cam.get("model"),
            "ip": cam.get("ip"),
            "mac": cam.get("mac") or None,
            "status_code": status,
            "online": status == 1,
        })
    return fmt({"total": len(cameras), "cameras": cameras})
