"""Backup monitoring: Hyper Backup tasks."""

from __future__ import annotations

from .. import api
from ..app import check, fmt, mcp


@mcp.tool()
async def list_backup_tasks() -> str:
    """List Hyper Backup tasks with their current state and target."""
    data = check(await api.call("SYNO.Backup.Task", "list", version=1))
    tasks = []
    for t in data.get("task_list", []):
        tasks.append({
            "task_id": t.get("task_id"),
            "name": t.get("name"),
            "state": t.get("state"),
            "status": t.get("status"),
            "target": t.get("target_id"),
            "type": t.get("type"),
            "encrypted": t.get("data_enc"),
        })
    return fmt({
        "total": data.get("total", len(tasks)),
        "restoring": data.get("is_restoring"),
        "tasks": tasks,
    })


@mcp.tool()
async def run_backup_task(task_id: int) -> str:
    """
    Start a Hyper Backup task immediately. [control]

    Args:
        task_id: Numeric task id (from list_backup_tasks)
    """
    check(await api.call("SYNO.Backup.Task", "backup", version=1, task_id=task_id))
    return fmt({"task_id": task_id, "started": True})
