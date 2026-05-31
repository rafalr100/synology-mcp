"""Security: DSM account protection, auto-block, firewall and certificates."""

from __future__ import annotations

from .. import api
from ..app import check, fmt, mcp


@mcp.tool()
async def get_security_settings() -> str:
    """Get DSM security settings (session timeout, CSRF protection, IP checking)."""
    data = check(await api.call("SYNO.Core.Security.DSM", "get", version=6))
    return fmt({
        "session_timeout_minutes": data.get("timeout"),
        "csrf_protection": data.get("enable_csrf_protection"),
        "skip_ip_checking": data.get("skip_ip_checking"),
        "allow_stay_signed_in": data.get("allow_stay_signed_in_option"),
    })


@mcp.tool()
async def get_autoblock_settings() -> str:
    """Get the auto-block policy (block IPs after failed login attempts)."""
    data = check(await api.call("SYNO.Core.Security.AutoBlock", "get", version=1))
    return fmt({
        "enabled": data.get("enable"),
        "attempts": data.get("attempts"),
        "within_minutes": data.get("within_mins"),
        "block_expires_days": data.get("expire_day"),
    })


@mcp.tool()
async def get_firewall_status() -> str:
    """Get firewall profile information."""
    profiles = await api.call("SYNO.Core.Security.Firewall.Profile", "list", version=1)
    pdata = profiles.get("data", {}) if profiles.get("success") else {}
    return fmt({"profiles": pdata.get("profile_names", [])})


@mcp.tool()
async def list_certificates() -> str:
    """List installed TLS/SSL certificates with validity dates and assigned services."""
    data = check(await api.call("SYNO.Core.Certificate.CRT", "list", version=1))
    certs = []
    for c in data.get("certificates", []):
        certs.append({
            "id": c.get("id"),
            "description": c.get("desc") or None,
            "subject": (c.get("subject") or {}).get("common_name") if isinstance(c.get("subject"), dict) else c.get("subject"),
            "issuer": (c.get("issuer") or {}).get("common_name") if isinstance(c.get("issuer"), dict) else c.get("issuer"),
            "valid_from": c.get("valid_from"),
            "valid_till": c.get("valid_till"),
            "is_default": c.get("is_default"),
            "is_broken": c.get("is_broken"),
            "renewable": c.get("renewable"),
            "services": len(c.get("services", []) or []),
        })
    return fmt({"total": len(certs), "certificates": certs})
