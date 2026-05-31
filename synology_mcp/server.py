"""Entry point for the Synology MCP server.

Importing :mod:`synology_mcp.tools` registers all tools on the shared FastMCP
instance; :func:`main` then runs it over stdio.
"""

from __future__ import annotations

from . import tools  # noqa: F401  (import registers all tools)
from .app import mcp


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
