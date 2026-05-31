"""Synology Photos tools (personal space)."""

from __future__ import annotations

from .. import api
from ..app import check, fmt, mcp


@mcp.tool()
async def list_photo_albums(limit: int = 50, offset: int = 0) -> str:
    """
    List albums in Synology Photos (personal space).

    Args:
        limit: Max albums to return (default 50)
        offset: Pagination offset
    """
    data = check(await api.call("SYNO.Foto.Browse.Album", "list", version=1,
                                offset=offset, limit=limit))
    albums = []
    for a in data.get("list", []):
        albums.append({
            "id": a.get("id"),
            "name": a.get("name"),
            "item_count": a.get("item_count"),
            "shared": a.get("shared"),
            "type": a.get("type"),
        })
    return fmt({"total": len(albums), "albums": albums})
