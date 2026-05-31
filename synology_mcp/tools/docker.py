"""Docker / Container Manager tools."""

from __future__ import annotations

from .. import api
from ..app import check, fmt, mcp, ts


@mcp.tool()
async def list_containers() -> str:
    """List all Docker / Container Manager containers with their state and image."""
    data = check(await api.call("SYNO.Docker.Container", "list", version=1, limit=-1, offset=0))
    containers = []
    for c in data.get("containers", []):
        state = c.get("state") or {}
        running = c.get("status") == "running" or state.get("Running", False)
        containers.append({
            "name": c.get("name"),
            "image": c.get("image"),
            "running": running,
            "state": state.get("Status") or c.get("status"),
            "exit_code": state.get("ExitCode"),
            "started_at": state.get("StartedAt"),
            "finished_at": state.get("FinishedAt"),
            "is_package": c.get("is_package"),
        })
    containers.sort(key=lambda x: (not x["running"], (x["name"] or "").lower()))
    running = sum(1 for c in containers if c["running"])
    return fmt({"total": len(containers), "running": running, "containers": containers})


@mcp.tool()
async def get_container_logs(name: str, lines: int = 50) -> str:
    """
    Get recent log lines for a Docker container.

    Args:
        name: Container name (from list_containers)
        lines: Number of recent log lines (default 50)
    """
    data = check(await api.call(
        "SYNO.Docker.Container.Log", "get", version=1,
        name=name, sort_by="time", sort_dir="DESC", offset=0, limit=lines,
    ))
    entries = [
        {"time": ts(e.get("created")) or e.get("created"), "stream": e.get("stream"), "text": e.get("text")}
        for e in data.get("logs", data.get("items", []))
    ]
    return fmt({"container": name, "lines": len(entries), "logs": entries})


@mcp.tool()
async def set_container_state(name: str, action: str) -> str:
    """
    Start, stop or restart a Docker container. [control]

    Args:
        name: Container name (from list_containers)
        action: "start", "stop" or "restart"
    """
    if action not in ("start", "stop", "restart"):
        raise ValueError("action must be 'start', 'stop' or 'restart'")
    check(await api.call("SYNO.Docker.Container", action, version=1, name=name))
    return fmt({"container": name, "action": action, "ok": True})


@mcp.tool()
async def get_container_stats(name: str) -> str:
    """
    Get live CPU / memory / network / disk usage for a running container.

    Args:
        name: Container name (from list_containers)
    """
    data = check(await api.call("SYNO.Docker.Container.Resource", "get", version=1, name=name))
    res = data.get("resources", data)
    if isinstance(res, list):
        res = res[-1] if res else {}
    return fmt({
        "container": name,
        "cpu_pct": res.get("cpu") or res.get("cpu_percent"),
        "memory_mb": round((res.get("memory") or res.get("mem") or 0) / 1024 ** 2, 1) if res.get("memory") or res.get("mem") else None,
        "raw": res,
    })


@mcp.tool()
async def list_docker_projects() -> str:
    """List Docker Compose / Container Manager projects."""
    data = check(await api.call("SYNO.Docker.Project", "list", version=1))
    projects = []
    items = data.values() if isinstance(data, dict) else data
    for p in items:
        if not isinstance(p, dict):
            continue
        projects.append({
            "id": p.get("id"),
            "name": p.get("name"),
            "status": p.get("status"),
            "path": p.get("share_path") or p.get("path"),
            "containers": len(p.get("containerIds", []) or []),
            "created": ts(p.get("created_at")) or p.get("created_at"),
        })
    return fmt({"total": len(projects), "projects": projects})


@mcp.tool()
async def list_docker_images() -> str:
    """List Docker images stored on the NAS, including whether an update is available."""
    data = check(await api.call("SYNO.Docker.Image", "list", version=1, limit=-1, offset=0))
    images = []
    for img in data.get("images", []):
        size = int(img.get("size", 0) or 0)
        images.append({
            "repository": img.get("repository"),
            "tags": img.get("tags"),
            "size_mb": round(size / 1024 ** 2, 1) if size else None,
            "created": ts(img.get("created")) or img.get("created"),
            "upgradable": img.get("upgradable"),
        })
    return fmt({"total": len(images), "images": images})
