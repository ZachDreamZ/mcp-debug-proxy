# MCP Debug Proxy Documentation

## Installation

```bash
pip install mcp-debug-proxy
```

## Quick Start

Record a session with any stdio-based MCP server:

```bash
mcp-debug --out session.json -- python my_mcp_server.py
```

Generate a report:

```bash
mcp-debug --report session.json
```

## Commands

### Proxy Mode
Wrap any MCP server and record all traffic:

```bash
mcp-debug --out session.json -- <server-command>
```

### Text Report
```bash
mcp-debug --report session.json
```

### JSON Export
```bash
mcp-debug --report session.json --format json
```

### Mermaid Diagram (Paid)
```bash
mcp-debug --mermaid session.json
```

### Session Replay (Paid)
```bash
mcp-debug --replay session.json --rate 2.0
```

## Troubleshooting

If the proxy doesn't work, check:
1. The server command runs without the proxy
2. Python 3.10+ is installed
3. The server uses stdio transport (not HTTP/SSE)

## Pricing

| Feature | Free | Paid ($9) |
|---------|:----:|:---------:|
| Session recording | ✅ | ✅ |
| Text report | ✅ | ✅ |
| Latency analysis | ✅ | ✅ |
| JSON export | ✅ | ✅ |
| Mermaid diagrams | ❌ | ✅ |
| Session replay | ❌ | ✅ |
| Session comparison | ❌ | ✅ |

[Get Paid Version →](https://shadowcraft41.gumroad.com/l/ypnsof)
