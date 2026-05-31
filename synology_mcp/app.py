"""Shared FastMCP instance and small formatting helpers used by all tools."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Optional

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Synology NAS")


def fmt(data) -> str:
    """Serialise a tool result to a pretty JSON string."""
    return json.dumps(data, ensure_ascii=False, indent=2)


def check(result: dict) -> dict:
    """Return ``result['data']`` or raise with the DSM error code on failure."""
    if not result.get("success"):
        code = result.get("error", {}).get("code", "?")
        raise RuntimeError(f"Synology API error (code {code}): {result.get('error')}")
    return result.get("data", {})


def ts(value) -> Optional[str]:
    """Convert a Unix timestamp (seconds) to an ISO-like UTC string."""
    if not value:
        return None
    try:
        return datetime.fromtimestamp(int(value), tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, OSError, TypeError):
        return None


def fmt_uptime(seconds) -> str:
    """Render a number of seconds as ``Nd Nh Nm``."""
    try:
        seconds = int(seconds)
    except (ValueError, TypeError):
        return "?"
    d, rem = divmod(seconds, 86400)
    h, rem = divmod(rem, 3600)
    m, _ = divmod(rem, 60)
    return f"{d}d {h}h {m}m"
