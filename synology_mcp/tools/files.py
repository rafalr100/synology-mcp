"""File Station tools: browse, inspect, search and manage files and folders."""

from __future__ import annotations

import asyncio
from typing import Optional

from .. import api
from ..app import check, fmt, mcp, ts

# Fields requested from File Station; must be sent as a JSON-array string.
_FILE_ADDITIONAL = '["real_path","size","time","type","owner","perm"]'


@mcp.tool()
async def list_shares() -> str:
    """List all available shared folders (File Station view)."""
    data = check(await api.call("SYNO.FileStation.List", "list_share", version=2,
                                additional='["real_path","perm"]'))
    shares = []
    for s in data.get("shares", []):
        shares.append({
            "name": s.get("name"),
            "path": s.get("path"),
            "real_path": s.get("additional", {}).get("real_path"),
            "is_readonly": s.get("additional", {}).get("perm", {}).get("is_readonly"),
        })
    return fmt({"shares": shares, "total": data.get("total", len(shares))})


@mcp.tool()
async def list_files(
    path: str,
    limit: int = 100,
    offset: int = 0,
    sort_by: str = "name",
    sort_direction: str = "asc",
    pattern: Optional[str] = None,
) -> str:
    """
    List files and folders at a given path.

    Args:
        path: Full path e.g. /home or /docker/app
        limit: Max items to return (default 100)
        offset: Pagination offset
        sort_by: name | size | user | group | mtime | atime | crtime | posix
        sort_direction: asc | desc
        pattern: Optional filename filter (supports wildcards, e.g. *.pdf)
    """
    data = check(await api.call(
        "SYNO.FileStation.List", "list", version=2,
        folder_path=path, limit=limit, offset=offset,
        sort_by=sort_by, sort_direction=sort_direction,
        pattern=pattern, additional=_FILE_ADDITIONAL,
    ))
    files = []
    for f in data.get("files", []):
        add = f.get("additional", {})
        time = add.get("time", {})
        files.append({
            "name": f.get("name"),
            "path": f.get("path"),
            "is_dir": f.get("isdir"),
            "size_bytes": add.get("size") if not f.get("isdir") else None,
            "modified": ts(time.get("mtime")),
            "created": ts(time.get("crtime")),
        })
    return fmt({"path": path, "total": data.get("total", len(files)), "files": files})


@mcp.tool()
async def get_file_info(paths: str) -> str:
    """
    Get detailed info (size, owner, timestamps) for one or more files/folders.

    Args:
        paths: Comma-separated paths e.g. /home/report.pdf,/photo
    """
    data = check(await api.call(
        "SYNO.FileStation.List", "getinfo", version=2,
        path=paths, additional=_FILE_ADDITIONAL,
    ))
    files = []
    for f in data.get("files", []):
        add = f.get("additional", {})
        time = add.get("time", {})
        owner = add.get("owner", {})
        files.append({
            "name": f.get("name"),
            "path": f.get("path"),
            "is_dir": f.get("isdir"),
            "real_path": add.get("real_path"),
            "size_bytes": add.get("size") if not f.get("isdir") else None,
            "owner": f"{owner.get('user')}:{owner.get('group')}" if owner else None,
            "modified": ts(time.get("mtime")),
            "created": ts(time.get("crtime")),
            "accessed": ts(time.get("atime")),
        })
    return fmt({"files": files})


@mcp.tool()
async def get_directory_size(path: str) -> str:
    """
    Calculate the total size and item count of a folder (recursively).

    Args:
        path: Folder path e.g. /docker
    """
    start = check(await api.call("SYNO.FileStation.DirSize", "start", version=1, path=path))
    taskid = start.get("taskid")
    if not taskid:
        return fmt(start)
    for _ in range(120):
        status = check(await api.call("SYNO.FileStation.DirSize", "status", version=1, taskid=taskid))
        if status.get("finished"):
            total = int(status.get("total_size", 0) or 0)
            return fmt({
                "path": path,
                "total_size_bytes": total,
                "total_size_gb": round(total / 1024 ** 3, 2),
                "num_files": status.get("num_file"),
                "num_dirs": status.get("num_dir"),
            })
        await asyncio.sleep(0.5)
    return fmt({"error": "directory size calculation timed out"})


@mcp.tool()
async def get_file_md5(path: str) -> str:
    """
    Compute the MD5 checksum of a file.

    Args:
        path: Full file path
    """
    start = check(await api.call("SYNO.FileStation.MD5", "start", version=2, file_path=path))
    taskid = start.get("taskid")
    if not taskid:
        return fmt(start)
    for _ in range(120):
        status = check(await api.call("SYNO.FileStation.MD5", "status", version=2, taskid=taskid))
        if status.get("finished"):
            return fmt({"path": path, "md5": status.get("md5")})
        await asyncio.sleep(0.5)
    return fmt({"error": "MD5 calculation timed out"})


@mcp.tool()
async def create_folder(parent_path: str, name: str) -> str:
    """
    Create a new folder.

    Args:
        parent_path: Where to create the folder e.g. /home
        name: New folder name
    """
    data = check(await api.call(
        "SYNO.FileStation.CreateFolder", "create", version=2,
        folder_path=parent_path, name=name, force_parent=True,
    ))
    return fmt(data)


@mcp.tool()
async def rename_item(path: str, new_name: str) -> str:
    """
    Rename a file or folder.

    Args:
        path: Full path of the item to rename
        new_name: New name only (not a full path)
    """
    data = check(await api.call(
        "SYNO.FileStation.Rename", "rename", version=2,
        path=path, name=new_name, additional="real_path",
    ))
    return fmt(data)


@mcp.tool()
async def copy_move_item(
    paths: str,
    dest_folder: str,
    move: bool = False,
    overwrite: bool = False,
) -> str:
    """
    Copy or move files/folders into an existing destination folder. [control]

    Args:
        paths: Comma-separated source paths
        dest_folder: Existing destination folder path
        move: True to move, False to copy (default)
        overwrite: Overwrite existing files (default False)
    """
    start = check(await api.call(
        "SYNO.FileStation.CopyMove", "start", version=3,
        path=paths, dest_folder_path=dest_folder,
        overwrite=overwrite, remove_src=move,
    ))
    taskid = start.get("taskid")
    if not taskid:
        return fmt(start)
    result = await api.wait_for_task("SYNO.FileStation.CopyMove", taskid)
    return fmt({"action": "move" if move else "copy", "done": result.get("success"),
                "detail": result.get("data")})


@mcp.tool()
async def delete_item(paths: str, recursive: bool = True) -> str:
    """
    Delete files or folders. [control]

    Args:
        paths: Comma-separated paths to delete
        recursive: Delete folder contents recursively (default True)
    """
    # The blocking 'delete' method is reliable; the async start/status variant
    # has been observed to report success without removing the items.
    check(await api.call(
        "SYNO.FileStation.Delete", "delete", version=2,
        path=paths, recursive=recursive,
    ))
    return fmt({"deleted": True, "paths": paths.split(",")})


@mcp.tool()
async def search_files(
    folder_path: str,
    pattern: str,
    recursive: bool = True,
    limit: int = 50,
) -> str:
    """
    Search for files by name pattern within a folder.

    Args:
        folder_path: Root folder to search e.g. /home
        pattern: Filename pattern e.g. *.pdf or report*
        recursive: Search subdirectories (default True)
        limit: Max results (default 50)
    """
    start = check(await api.call(
        "SYNO.FileStation.Search", "start", version=2,
        folder_path=folder_path, recursive=recursive, pattern=pattern,
    ))
    taskid = start.get("taskid")
    if not taskid:
        return fmt(start)
    try:
        for _ in range(20):
            status = await api.call(
                "SYNO.FileStation.Search", "list", version=2,
                taskid=taskid, limit=limit,
                additional='["real_path","size","time"]',
            )
            if status.get("success"):
                data = status["data"]
                if data.get("finished") or data.get("files"):
                    files = [
                        {
                            "name": f.get("name"),
                            "path": f.get("path"),
                            "is_dir": f.get("isdir"),
                            "size_bytes": f.get("additional", {}).get("size") if not f.get("isdir") else None,
                            "modified": ts(f.get("additional", {}).get("time", {}).get("mtime")),
                        }
                        for f in data.get("files", [])
                    ]
                    return fmt({"found": len(files), "finished": data.get("finished"), "files": files})
            await asyncio.sleep(0.5)
        return fmt({"error": "search timed out"})
    finally:
        await api.call("SYNO.FileStation.Search", "stop", version=2, taskid=taskid)


@mcp.tool()
async def extract_archive(archive_path: str, dest_folder: str) -> str:
    """
    Extract an archive (ZIP, etc.) into a destination folder. [control]

    Args:
        archive_path: Full path to the archive file
        dest_folder: Destination folder path
    """
    start = check(await api.call(
        "SYNO.FileStation.Extract", "start", version=2,
        file_path=archive_path, dest_folder_path=dest_folder,
    ))
    taskid = start.get("taskid")
    if not taskid:
        return fmt(start)
    result = await api.wait_for_task("SYNO.FileStation.Extract", taskid, max_wait=300)
    return fmt({"extracted_to": dest_folder, "done": result.get("success")})


@mcp.tool()
async def create_share_link(path: str, password: Optional[str] = None) -> str:
    """
    Create a public sharing link for a file or folder. [control]

    Args:
        path: Full path to share
        password: Optional password to protect the link
    """
    data = check(await api.call(
        "SYNO.FileStation.Sharing", "create", version=3,
        path=path, password=password,
    ))
    links = data.get("links", [])
    return fmt({"links": [{"path": l.get("path"), "url": l.get("url"),
                           "link_id": l.get("id"), "error": l.get("error")} for l in links]})
