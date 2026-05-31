"""Shared FastMCP instance and small formatting helpers used by all tools."""

from __future__ import annotations

import functools
import json
import time
from datetime import UTC, datetime

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Synology NAS")


def ttl_cache(seconds: float):
    """Cache an async function's result for a few seconds (keyed by arguments).

    Useful for hot, read-only aggregates (e.g. dashboards) so rendering doesn't
    hammer the NAS with identical calls.
    """
    def decorator(func):
        store: dict = {}

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            key = (args, tuple(sorted(kwargs.items())))
            now = time.monotonic()
            hit = store.get(key)
            if hit and now - hit[0] < seconds:
                return hit[1]
            value = await func(*args, **kwargs)
            store[key] = (now, value)
            return value

        return wrapper
    return decorator


def fmt(data) -> str:
    """Serialise a tool result to a pretty JSON string."""
    return json.dumps(data, ensure_ascii=False, indent=2)


# Friendly explanations for common DSM error codes (general + FileStation range).
_ERROR_HINTS = {
    100: "unknown error",
    101: "invalid parameter",
    102: "the requested API does not exist (feature/package may not be installed)",
    103: "the requested method does not exist",
    105: "the logged-in account does not have permission for this action (try an admin account)",
    106: "session timed out",
    107: "session interrupted by a duplicate login",
    119: "invalid session (SID) — re-authentication needed",
    120: "invalid parameter",
    403: "permission denied or 2FA required",
    406: "two-factor authentication is enforced",
    407: "operation not permitted / blocked",
    408: "no such file or directory",
    414: "operation failed",
    599: "no such task / operation not permitted for this path",
}


def check(result: dict) -> dict:
    """Return ``result['data']`` or raise a readable error on failure."""
    if not result.get("success"):
        err = result.get("error", {}) or {}
        code = err.get("code", "?")
        hint = _ERROR_HINTS.get(code)
        msg = f"Synology API error (code {code})"
        if hint:
            msg += f": {hint}"
        if err.get("errors"):
            msg += f" — {err['errors']}"
        raise RuntimeError(msg)
    return result.get("data", {})


def ts(value) -> str | None:
    """Convert a Unix timestamp (seconds) to an ISO-like UTC string."""
    if not value:
        return None
    try:
        return datetime.fromtimestamp(int(value), tz=UTC).strftime("%Y-%m-%d %H:%M:%S")
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
