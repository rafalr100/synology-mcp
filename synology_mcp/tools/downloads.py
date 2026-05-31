"""Download Station tools (DSM 7 uses the DownloadStation2 API)."""

from __future__ import annotations

import json

from .. import api
from ..app import check, fmt, mcp

_TASK_API = "SYNO.DownloadStation2.Task"


@mcp.tool()
async def list_downloads() -> str:
    """List Download Station tasks with progress, size and transfer speed."""
    data = check(await api.call(
        _TASK_API, "list", version=2,
        additional='["detail","transfer"]',
    ))
    tasks = []
    for t in data.get("task", []):
        add = t.get("additional", {})
        transfer = add.get("transfer", {})
        size = int(t.get("size", 0) or 0)
        done = int(transfer.get("size_downloaded", 0) or 0)
        tasks.append({
            "id": t.get("id"),
            "title": t.get("title"),
            "type": t.get("type"),
            "status": t.get("status"),
            "size_mb": round(size / 1024 ** 2, 1) if size else None,
            "progress_pct": round(done / size * 100, 1) if size else None,
            "download_kb_s": round(int(transfer.get("speed_download", 0) or 0) / 1024, 1),
            "upload_kb_s": round(int(transfer.get("speed_upload", 0) or 0) / 1024, 1),
        })
    return fmt({"total": data.get("total", len(tasks)), "tasks": tasks})


@mcp.tool()
async def add_download(url: str, destination: str) -> str:
    """
    Add a new download task from a URL or magnet link. [control]

    Args:
        url: HTTP/FTP URL or magnet link to download
        destination: Shared-folder path (without leading slash), e.g. "video/movies".
                     Required by Download Station.
    """
    check(await api.call(
        _TASK_API, "create", version=2,
        type='"url"', url=json.dumps([url]),
        destination=json.dumps(destination), create_list="false",
    ))
    return fmt({"added": url, "destination": destination})


@mcp.tool()
async def manage_download(task_ids: str, action: str) -> str:
    """
    Pause, resume or delete download tasks. [control]

    Args:
        task_ids: Comma-separated task ids (from list_downloads)
        action: "pause", "resume" or "delete"
    """
    if action not in ("pause", "resume", "delete"):
        raise ValueError("action must be 'pause', 'resume' or 'delete'")
    ids = json.dumps([i.strip() for i in task_ids.split(",") if i.strip()])
    kwargs = {"id": ids}
    if action == "delete":
        kwargs["force_complete"] = "false"
    check(await api.call(_TASK_API, action, version=2, **kwargs))
    return fmt({"action": action, "task_ids": task_ids, "ok": True})
