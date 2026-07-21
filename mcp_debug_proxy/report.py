"""
MCP Debug Report Generator
"""
import json
from .core import Session

def generate_report(session: Session, format: str = "text") -> str:
    """Generate a human-readable report from a session."""
    summary = session.summary()
    
    if format == "json":
        return session.export_json()
    
    if format == "mermaid":
        return session.export_mermaid()
    
    # Text format
    lines = []
    lines.append("=" * 60)
    lines.append(f"MCP Debug Proxy Report — {summary['label']}")
    lines.append("=" * 60)
    lines.append(f"Duration: {summary['duration_ms']}ms")
    lines.append(f"Total messages: {summary['total_messages']}")
    lines.append(f"Requests: {summary['requests']}")
    lines.append(f"Responses: {summary['responses']}")
    lines.append(f"Notifications: {summary['notifications']}")
    lines.append("")
    lines.append("Methods called:")
    for method, count in sorted(summary['methods'].items(), key=lambda x: -x[1]):
        lines.append(f"  {method}: {count}x")
    lines.append("")
    lines.append("Message log:")
    for msg in session.messages:
        ts = msg.timestamp
        prefix = ">>>" if msg.direction == "send" else "<<<"
        if msg.is_request:
            latency = session.latency_for(msg.message.get("id"))
            lat = f" [{latency:.0f}ms]" if latency else ""
            lines.append(f"  {prefix} {msg.method} (id={msg.message.get('id')}){lat}")
        elif msg.is_response:
            if "error" in msg.message:
                err = msg.message["error"]
                lines.append(f"  {prefix} ERROR {err.get('message', '')} (id={msg.message.get('id')})")
            elif "result" in msg.message:
                result = msg.message["result"]
                if isinstance(result, dict):
                    keys = list(result.keys())[:3]
                    lines.append(f"  {prefix} result keys={keys} (id={msg.message.get('id')})")
                else:
                    lines.append(f"  {prefix} result={str(result)[:60]} (id={msg.message.get('id')})")
        elif msg.is_notification:
            lines.append(f"  {prefix} NOTIFICATION {msg.method}")
    lines.append("")
    lines.append("=" * 60)
    return "\n".join(lines)
