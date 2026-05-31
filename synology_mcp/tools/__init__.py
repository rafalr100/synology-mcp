"""Importing this package registers every tool on the shared FastMCP instance.

Each submodule defines ``@mcp.tool()`` functions; importing them runs the
decorators, which attach the tools to ``synology_mcp.app.mcp``.
"""

from . import (  # noqa: F401
    admin,
    backup,
    dashboard,
    docker,
    downloads,
    files,
    hardware,
    monitoring,
    network_services,
    notifications,
    packages,
    power,
    scheduler,
    security,
    services,
    storage,
    system,
    virtualization,
)
