"""System monitoring tools: info, resource usage, network."""

from __future__ import annotations

from .. import api
from ..app import check, fmt, fmt_uptime, mcp


@mcp.tool()
async def get_system_info() -> str:
    """Get NAS model, DSM version, hostname, uptime, RAM, temperature and serial number."""
    data = check(await api.call("SYNO.DSM.Info", "getinfo", version=2))
    net = await api.call("SYNO.Core.Network", "get", version=1)
    hostname = net.get("data", {}).get("server_name") if net.get("success") else None
    return fmt({
        "model": data.get("model"),
        "dsm_version": data.get("version_string"),
        "hostname": hostname,
        "uptime": fmt_uptime(data.get("uptime", 0)),
        "ram_mb": data.get("ram"),
        "serial": data.get("serial"),
        "temperature_c": data.get("temperature"),
        "temperature_warn": data.get("temperature_warn"),
        "system_time": data.get("time"),
    })


@mcp.tool()
async def get_resource_usage() -> str:
    """Get real-time CPU usage, memory usage and network throughput."""
    data = check(await api.call("SYNO.Core.System.Utilization", "get", version=1))
    cpu = data.get("cpu", {})
    mem = data.get("memory", {})
    nets = data.get("network", [])
    total_net = next((n for n in nets if n.get("device") == "total"), nets[0] if nets else {})

    total_real = mem.get("total_real", 0)  # KB
    avail_real = mem.get("avail_real", 0)   # KB
    return fmt({
        "cpu": {
            "user_load": f"{cpu.get('user_load', '?')}%",
            "system_load": f"{cpu.get('system_load', '?')}%",
            "other_load": f"{cpu.get('other_load', '?')}%",
            "load_1min": cpu.get("1min_load"),
            "load_5min": cpu.get("5min_load"),
            "load_15min": cpu.get("15min_load"),
        },
        "memory": {
            "total_mb": round(total_real / 1024),
            "used_mb": round((total_real - avail_real) / 1024),
            "available_mb": round(avail_real / 1024),
            "usage_pct": f"{mem.get('real_usage', '?')}%",
            "swap_usage_pct": f"{mem.get('swap_usage', '?')}%",
        },
        "network": {
            "rx_kb_s": round(total_net.get("rx", 0) / 1024, 1),
            "tx_kb_s": round(total_net.get("tx", 0) / 1024, 1),
        },
    })


@mcp.tool()
async def get_network_info() -> str:
    """Get network interfaces with IP addresses, link speed and status, plus gateway/DNS."""
    core = check(await api.call("SYNO.Core.Network", "get", version=1))
    iface_data = await api.call("SYNO.Core.Network.Interface", "list", version=1)
    raw_ifaces = iface_data.get("data", []) if iface_data.get("success") else []

    interfaces = []
    for iface in raw_ifaces:
        interfaces.append({
            "name": iface.get("ifname"),
            "ip": iface.get("ip") or None,
            "mask": iface.get("mask") or None,
            "type": iface.get("type"),
            "speed_mbps": iface.get("speed") or None,
            "status": iface.get("status"),
            "dhcp": iface.get("use_dhcp"),
        })
    return fmt({
        "hostname": core.get("server_name"),
        "gateway": core.get("gateway"),
        "dns_primary": core.get("dns_primary"),
        "dns_secondary": core.get("dns_secondary") or None,
        "interfaces": interfaces,
    })
