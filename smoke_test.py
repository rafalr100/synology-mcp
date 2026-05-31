#!/usr/bin/env python3
"""Quick connectivity test — verifies login and a few read-only calls.

Usage:
    python smoke_test.py
"""

import asyncio

from synology_mcp import api, config


async def main() -> None:
    config.validate()
    print(f"→ Connecting to {config.URL} as '{config.USER}' ...")
    sid = await api._ensure_session()
    print(f"✓ Logged in (sid: {sid[:8]}...)\n")

    info = await api.call("SYNO.DSM.Info", "getinfo", version=2)
    d = info.get("data", {})
    print(f"  Model:       {d.get('model')}")
    print(f"  DSM version: {d.get('version_string')}")
    print(f"  Temperature: {d.get('temperature')}°C\n")

    shares = await api.call("SYNO.FileStation.List", "list_share", version=2)
    names = [s["name"] for s in shares.get("data", {}).get("shares", [])]
    print(f"  Shares: {', '.join(names) if names else '(none / no permission)'}")

    await api.close()
    print("\n✓ Smoke test passed.")


if __name__ == "__main__":
    asyncio.run(main())
