"""Hardware settings: power, LED/beep, hibernation, UPS and external USB devices."""

from __future__ import annotations

from .. import api
from ..app import check, fmt, mcp


@mcp.tool()
async def get_power_settings() -> str:
    """Get power-related hardware settings: power recovery, LED brightness, beep and power schedule."""
    recovery = check(await api.call("SYNO.Core.Hardware.PowerRecovery", "get", version=1))
    led = await api.call("SYNO.Core.Hardware.Led.Brightness", "get", version=1)
    beep = await api.call("SYNO.Core.Hardware.BeepControl", "get", version=1)
    sched = await api.call("SYNO.Core.Hardware.PowerSchedule", "load", version=1)
    sdata = sched.get("data", {}) if sched.get("success") else {}
    return fmt({
        "power_recovery": recovery.get("rc_power_config"),
        "wake_on_lan": recovery.get("wol"),
        "led_brightness": led.get("data", {}).get("led_brightness") if led.get("success") else None,
        "beep_on_poweron": beep.get("data", {}).get("poweron_beep") if beep.get("success") else None,
        "scheduled_poweron_tasks": len(sdata.get("poweron_tasks", [])),
        "scheduled_poweroff_tasks": len(sdata.get("poweroff_tasks", [])),
    })


@mcp.tool()
async def get_hibernation_settings() -> str:
    """Get disk hibernation (power-saving) settings."""
    data = check(await api.call("SYNO.Core.Hardware.Hibernation", "get", version=1))
    return fmt({
        "internal_disk_idle_minutes": data.get("internal_hd_idletime"),
        "auto_poweroff_enabled": data.get("auto_poweroff_enable"),
        "log_enabled": data.get("enable_log"),
    })


@mcp.tool()
async def get_ups_status() -> str:
    """Get UPS (uninterruptible power supply) status and configuration."""
    data = check(await api.call("SYNO.Core.ExternalDevice.UPS", "get", version=1))
    return fmt({
        "enabled": data.get("enable"),
        "mode": data.get("mode"),
        "model": data.get("model") or None,
        "manufacturer": data.get("manufacture") or None,
        "battery_charge_pct": data.get("charge"),
        "runtime_seconds": data.get("runtime"),
        "status": data.get("status"),
        "connected": data.get("usb_ups_connect"),
    })


@mcp.tool()
async def list_usb_devices() -> str:
    """List USB devices connected to the NAS."""
    data = check(await api.call("SYNO.Core.ExternalDevice.Storage.USB", "list", version=1))
    devices = [{"id": d.get("dev_id"), "title": d.get("dev_title")} for d in data.get("devices", [])]
    return fmt({"total": len(devices), "devices": devices})
