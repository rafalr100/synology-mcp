"""Unit tests that exercise the client and tools against a mocked DSM API.

No real NAS is required — httpx.MockTransport answers the entry.cgi calls.
"""

import json
from urllib.parse import parse_qs, urlparse

import httpx
import pytest

from synology_mcp import api
from synology_mcp.app import check, ttl_cache


def _params(request: httpx.Request) -> dict:
    q = parse_qs(urlparse(str(request.url)).query)
    return {k: v[0] for k, v in q.items()}


def _ok(data: dict) -> httpx.Response:
    return httpx.Response(200, json={"success": True, "data": data})


def _err(code: int) -> httpx.Response:
    return httpx.Response(200, json={"success": False, "error": {"code": code}})


@pytest.fixture(autouse=True)
def reset_session():
    api._session_id = None
    api._client = None
    yield
    api._session_id = None
    api._client = None


def install_handler(handler):
    api._client = httpx.AsyncClient(
        base_url="http://nas:5000", transport=httpx.MockTransport(handler)
    )


# ── check() ──────────────────────────────────────────────────────────────────

def test_check_returns_data():
    assert check({"success": True, "data": {"x": 1}}) == {"x": 1}


def test_check_friendly_permission_error():
    with pytest.raises(RuntimeError, match="permission"):
        check({"success": False, "error": {"code": 105}})


def test_check_unknown_code_still_raises():
    with pytest.raises(RuntimeError, match="code 4242"):
        check({"success": False, "error": {"code": 4242}})


# ── login / call / re-auth ─────────────────────────────────────────────────────

async def test_login_and_call():
    def handler(request):
        p = _params(request)
        if p["api"] == "SYNO.API.Auth" and p["method"] == "login":
            return _ok({"sid": "SID123"})
        if p["api"] == "SYNO.DSM.Info":
            assert p["_sid"] == "SID123"
            return _ok({"model": "DS999", "version_string": "DSM 7.x"})
        return _err(102)

    install_handler(handler)
    r = await api.call("SYNO.DSM.Info", "getinfo", version=2)
    assert r["success"] and r["data"]["model"] == "DS999"


async def test_reauth_on_expired_session():
    state = {"logins": 0, "first": True}

    def handler(request):
        p = _params(request)
        if p["api"] == "SYNO.API.Auth" and p["method"] == "login":
            state["logins"] += 1
            return _ok({"sid": f"SID{state['logins']}"})
        if state["first"]:
            state["first"] = False
            return _err(119)  # expired session → triggers one re-auth + retry
        return _ok({"ok": True})

    install_handler(handler)
    r = await api.call("SYNO.Core.System", "info", version=1)
    assert r["success"] is True
    assert state["logins"] == 2  # initial login + re-auth


# ── ttl_cache ───────────────────────────────────────────────────────────────────

async def test_ttl_cache_caches_within_window():
    calls = {"n": 0}

    @ttl_cache(60)
    async def f():
        calls["n"] += 1
        return calls["n"]

    assert await f() == 1
    assert await f() == 1  # served from cache
    assert calls["n"] == 1


# ── a tool end-to-end (formatting) ─────────────────────────────────────────────

async def test_get_system_info_formats_fields():
    from synology_mcp.tools import monitoring

    def handler(request):
        p = _params(request)
        if p["api"] == "SYNO.API.Auth":
            return _ok({"sid": "S"})
        if p["api"] == "SYNO.DSM.Info":
            return _ok({"model": "DS423+", "version_string": "DSM 7.3.2",
                        "uptime": 90061, "ram": 10240, "temperature": 47})
        if p["api"] == "SYNO.Core.Network":
            return _ok({"server_name": "nas-test"})
        return _err(102)

    install_handler(handler)
    out = json.loads(await monitoring.get_system_info())
    assert out["model"] == "DS423+"
    assert out["hostname"] == "nas-test"
    assert out["uptime"] == "1d 1h 1m"
    assert out["temperature_c"] == 47
