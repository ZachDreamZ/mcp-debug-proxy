# MCP Debug Proxy

Intercept, log, analyze, and replay **MCP (Model Context Protocol)** server traffic.

## Free vs Paid

| Feature | Free (GitHub) | Paid ($9) |
|---------|:---:|:---:|
| Session recording (JSON-RPC log) | ✅ | ✅ |
| Text report | ✅ | ✅ |
| Latency breakdown by method | ✅ | ✅ |
| JSON export | ✅ | ✅ |
| Mermaid sequence diagrams | ❌ | ✅ |
| Session replay engine | ❌ | ✅ |
| Session comparison (diff two runs) | ❌ | ✅ |
| Filter by method/error/timing | ❌ | ✅ |
| Priority support | ❌ | ✅ |

## Quick Start

```bash
pip install mcp-debug-proxy

# Record a session (free - text report only)
mcp-debug --out session.json -- python my_server.py
mcp-debug --report session.json
```

[Get the full version →](https://shadowcraft41.gumroad.com/l/ypnsof)

## Why Pay?

The paid version adds **Mermaid diagrams**, **session replay**, **session comparison**, and **smart filtering** — everything you need for serious debugging, documentation, and CI pipelines.

## Install

```bash
pip install mcp-debug-proxy
```

## MIT License

The core proxy engine is MIT licensed. The premium features (Mermaid export, replay, comparison, filtering) require a license key from the paid version.
