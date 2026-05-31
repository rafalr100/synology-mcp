# Contributing

Thanks for your interest in improving the Synology MCP Server!

## Getting set up

```bash
git clone https://github.com/OWNER/synology-mcp.git
cd synology-mcp
uv venv --python 3.12 .venv
uv pip install --python .venv -e .
cp .env.example .env   # point at a test NAS
.venv/bin/python smoke_test.py
```

## Adding a tool

1. Pick (or create) a domain module in `synology_mcp/tools/`.
2. Write an `async def` decorated with `@mcp.tool()`. Use the shared helpers from
   `synology_mcp.app` (`check`, `fmt`, `ts`, `fmt_uptime`) and call the DSM API through
   `synology_mcp.api.call(...)`.
3. Keep the docstring concise — it becomes the tool description the model sees. Tag
   state-changing tools with `[control]` (and destructive power tools with `[power]`).
4. If the module is new, add it to `synology_mcp/tools/__init__.py`.
5. Map fields explicitly and convert units (bytes→GB/MB, timestamps→ISO). Return JSON via
   `fmt(...)`.
6. Regenerate the reference: `python scripts/gen_tools_doc.py`.

## Verifying API shapes

Synology field names vary by DSM version. Before relying on a field, confirm it against a
live DSM 7 system. Query available APIs and versions with:

```
GET /webapi/query.cgi?api=SYNO.API.Info&version=1&method=query&query=all
```

## Guidelines

- **No secrets, no personal data** in code, tests, docs or fixtures — use placeholders.
- Prefer read-only tools; gate anything destructive and document the risk.
- Match the existing code style (type hints, small focused functions, English docstrings).
- Test new tools against a real NAS and note any required privileges.

## Pull requests

Describe what changed, which DSM version you tested on, and any new permissions required.
Keep PRs focused.
