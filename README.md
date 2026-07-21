# MCP Debug Proxy

Intercept, log, analyze, and replay **MCP (Model Context Protocol)** server traffic.

## Why?

Debugging MCP servers means staring at raw stdio output or adding print
statements. `mcp-debug` wraps any MCP server process and gives you:

- **Full session recording** — every JSON-RPC message with timing
- **Latency analysis** — per-method response times
- **Replay engine** — replay recorded sessions at any speed
- **Export formats** — JSON, text reports, Mermaid sequence diagrams
- **Zero code changes** — works with any stdio-based MCP server

## Quick Start

```bash
# Install
pip install mcp-debug-proxy

# Proxy an MCP server
mcp-debug -- npx @modelcontextprotocol/server-filesystem /tmp

# Record to file
mcp-debug --out session.json -- npx @modelcontextprotocol/server-filesystem /tmp

# Analyze a recording
mcp-debug --report session.json

# Generate a diagram
mcp-debug --mermaid session.json

# Replay at 2x speed
mcp-debug --replay session.json --rate 2.0
```

## Features

### Proxy Mode
Sits between your AI client and any stdio-based MCP server. Every message
is recorded with microsecond timing.

### Analysis
- Latency breakdown by method
- Error rate tracking
- Message volume statistics
- Full message log with timing

### Replay
Test client behavior by replaying recorded server responses at any speed.
Useful for regression testing and load testing.

## Output Formats

- **Text reports** — human-readable session summary
- **JSON export** — machine-readable for CI pipelines
- **Mermaid diagrams** — visual sequence diagrams for documentation

## Requirements

- Python 3.10+
- Works with any stdio-based MCP server

## License

MIT
