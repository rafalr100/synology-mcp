FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -e .
# stdio MCP server; Glama starts it and introspects (tools/list) over stdio.
CMD ["python", "-m", "synology_mcp"]
