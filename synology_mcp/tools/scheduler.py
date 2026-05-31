"""Task Scheduler tools: list and run scheduled tasks."""

from __future__ import annotations

from .. import api
from ..app import check, fmt, mcp


@mcp.tool()
async def list_scheduled_tasks() -> str:
    """List scheduled tasks (cron jobs, scripts, scheduled backups, etc.)."""
    data = check(await api.call("SYNO.Core.TaskScheduler", "list", version=1))
    tasks = []
    for t in data.get("tasks", []):
        tasks.append({
            "id": t.get("id"),
            "name": t.get("name"),
            "type": t.get("type"),
            "enabled": t.get("enable"),
            "owner": t.get("owner"),
            "next_run": t.get("next_trigger_time"),
            "can_run_now": t.get("can_run"),
        })
    return fmt({"total": data.get("total", len(tasks)), "tasks": tasks})


@mcp.tool()
async def run_scheduled_task(task_id: int) -> str:
    """
    Trigger a scheduled task to run immediately. [control]

    Args:
        task_id: Numeric task id (from list_scheduled_tasks)
    """
    check(await api.call("SYNO.Core.TaskScheduler", "run", version=1, taskId=task_id))
    return fmt({"task_id": task_id, "triggered": True})
