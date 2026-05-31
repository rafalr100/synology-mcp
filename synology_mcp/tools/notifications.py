"""Notification settings."""

from __future__ import annotations

from .. import api
from ..app import check, fmt, mcp


@mcp.tool()
async def get_notification_settings() -> str:
    """Get e-mail notification settings (enabled state, sender, SMTP)."""
    data = check(await api.call("SYNO.Core.Notification.Mail.Conf", "get", version=2))
    smtp = data.get("smtp_info", {}) or {}
    return fmt({
        "email_enabled": data.get("enable_mail"),
        "sender_name": data.get("sender_name") or None,
        "sender_mail": data.get("sender_mail") or None,
        "smtp_server": smtp.get("smtp_server") if isinstance(smtp, dict) else None,
        "oauth_enabled": data.get("enable_oauth"),
    })
