#!/usr/bin/env python3
"""One-time 2FA bootstrap: exchange an OTP code for a persistent device token.

If your Synology account has two-factor authentication enabled, the server
cannot log in with just a password. Run this once with a current 6-digit OTP
code (from your authenticator app) to obtain a trusted-device token, which is
appended to your .env as SYNOLOGY_DEVICE_ID. After that the server logs in
without needing an OTP.

Usage:
    python bootstrap_2fa.py <6-digit-OTP-code>
"""

import asyncio
import sys
from pathlib import Path

from synology_mcp import api, config


async def main(otp: str) -> None:
    config.validate()
    print(f"→ Logging in to {config.URL} as '{config.USER}' with OTP {otp} ...")
    did = await api.bootstrap_device_token(otp)
    print(f"✓ Received device token: {did[:12]}...")

    env_path = Path(__file__).resolve().parent / ".env"
    lines = env_path.read_text().splitlines() if env_path.exists() else []
    lines = [ln for ln in lines if not ln.startswith("SYNOLOGY_DEVICE_ID=")]
    lines.append(f"SYNOLOGY_DEVICE_ID={did}")
    env_path.write_text("\n".join(lines) + "\n")
    print(f"✓ Saved SYNOLOGY_DEVICE_ID to {env_path}")

    await api.close()
    print("\n✓ Done — the server will now log in without an OTP.")


if __name__ == "__main__":
    if len(sys.argv) != 2 or not sys.argv[1].isdigit():
        print("Usage: python bootstrap_2fa.py <6-digit-OTP-code>")
        sys.exit(1)
    asyncio.run(main(sys.argv[1]))
