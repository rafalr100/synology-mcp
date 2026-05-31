"""Storage tools: volumes and physical disks."""

from __future__ import annotations

from .. import api
from ..app import check, fmt, mcp


@mcp.tool()
async def get_storage_info() -> str:
    """Get storage volumes: RAID type, filesystem, used/free space and health status."""
    data = check(await api.call("SYNO.Storage.CGI.Storage", "load_info", version=1))
    volumes = []
    for v in data.get("volumes", []):
        size = v.get("size", {})
        total = int(size.get("total", 0) or 0)
        used = int(size.get("used", 0) or 0)
        volumes.append({
            "id": v.get("id"),
            "status": v.get("status"),
            "raid_type": v.get("raidType"),
            "fs_type": v.get("fs_type"),
            "total_gb": round(total / 1024 ** 3, 1),
            "used_gb": round(used / 1024 ** 3, 1),
            "free_gb": round((total - used) / 1024 ** 3, 1),
            "used_pct": f"{round(used / total * 100, 1)}%" if total else "?",
        })
    return fmt({"volumes": volumes})


@mcp.tool()
async def get_storage_pools() -> str:
    """Get storage pools with RAID type, status and data-scrubbing state."""
    data = check(await api.call("SYNO.Storage.CGI.Storage", "load_info", version=1))
    pools = []
    for p in data.get("storagePools", []):
        scrub = p.get("data_scrubbing", {})
        pools.append({
            "id": p.get("id"),
            "raid_type": p.get("raidType"),
            "status": p.get("status"),
            "drive_type": p.get("drive_type"),
            "num_disks": len(p.get("disks", []) or []),
            "scrubbing_status": scrub.get("data_scrubbing_status") if isinstance(scrub, dict) else None,
            "last_scrub": scrub.get("data_scrubbing_finish_time") if isinstance(scrub, dict) else None,
        })
    return fmt({"total": len(pools), "pools": pools})


@mcp.tool()
async def get_disk_info() -> str:
    """Get individual disk details: model, temperature, health (S.M.A.R.T.) and status."""
    data = check(await api.call("SYNO.Storage.CGI.Storage", "load_info", version=1))
    disks = []
    for d in data.get("disks", []):
        size = int(d.get("size_total", 0) or 0)
        life = d.get("remain_life")
        life_val = life.get("value") if isinstance(life, dict) else life
        remaining_life = life_val if isinstance(life_val, int) and life_val >= 0 else None
        disks.append({
            "id": d.get("id"),
            "model": (d.get("model") or "").strip(),
            "vendor": (d.get("vendor") or "").strip(),
            "size_gb": round(size / 1024 ** 3, 1) if size else None,
            "status": d.get("status"),
            "temp_c": d.get("temp"),
            "smart_status": d.get("smart_status"),
            "type": d.get("diskType"),
            "is_ssd": d.get("isSsd"),
            "remaining_life_pct": remaining_life,
            "used_by": d.get("used_by"),
        })
    return fmt({"disks": disks})
