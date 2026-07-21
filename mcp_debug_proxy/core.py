"""
MCP Debug Proxy Core
"""
import asyncio
import json
import logging
import os
import sys
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Optional
import subprocess

log = logging.getLogger("mcp-debug")

class MessageRecord:
    """A recorded JSON-RPC message with timing."""
    def __init__(self, direction: str, message: dict, timestamp: float, id: str = None):
        self.direction = direction  # "send" or "recv"
        self.message = message
        self.timestamp = timestamp
        self.id = id or str(uuid.uuid4())[:8]
        self.method = message.get("method", "(response)")
        self.is_request = "method" in message and "id" in message
        self.is_response = "id" in message and "result" in message or "error" in message
        self.is_notification = "method" in message and "id" not in message

    def to_dict(self):
        return {
            "id": self.id,
            "direction": self.direction,
            "timestamp": datetime.fromtimestamp(self.timestamp, tz=timezone.utc).isoformat(),
            "method": self.method,
            "is_request": self.is_request,
            "is_response": self.is_response,
            "is_notification": self.is_notification,
            "body": self.message,
        }

class Session:
    """A recorded MCP session with all messages."""
    def __init__(self, label: str = None):
        self.label = label or f"session-{uuid.uuid4().hex[:6]}"
        self.messages: list[MessageRecord] = []
        self.start_time = time.time()
        self.end_time: Optional[float] = None
        self._pending: dict[str, float] = {}

    def record_send(self, message: dict):
        rec = MessageRecord("send", message, time.time())
        self.messages.append(rec)
        if message.get("id") is not None:
            self._pending[str(message["id"])] = rec.timestamp
        return rec

    def record_recv(self, message: dict):
        rec = MessageRecord("recv", message, time.time())
        self.messages.append(rec)
        return rec

    def close(self):
        self.end_time = time.time()

    def duration_ms(self) -> float:
        if not self.end_time:
            return 0.0
        return (self.end_time - self.start_time) * 1000

    def latency_for(self, req_id) -> Optional[float]:
        """Return latency in ms for a request/response pair."""
        send_t = self._pending.get(str(req_id))
        if not send_t:
            return None
        for m in reversed(self.messages):
            if m.direction == "recv" and m.message.get("id") == req_id:
                return (m.timestamp - send_t) * 1000
        return None

    def summary(self) -> dict:
        reqs = [m for m in self.messages if m.is_request]
        resps = [m for m in self.messages if m.is_response]
        notifications = [m for m in self.messages if m.is_notification]
        methods = {}
        for m in reqs:
            methods[m.method] = methods.get(m.method, 0) + 1
        return {
            "label": self.label,
            "duration_ms": round(self.duration_ms(), 1),
            "total_messages": len(self.messages),
            "requests": len(reqs),
            "responses": len(resps),
            "notifications": len(notifications),
            "methods": methods,
        }

    def export_json(self) -> str:
        return json.dumps({
            "label": self.label,
            "start": datetime.fromtimestamp(self.start_time, tz=timezone.utc).isoformat(),
            "end": datetime.fromtimestamp(self.end_time, tz=timezone.utc).isoformat() if self.end_time else None,
            "duration_ms": round(self.duration_ms(), 1),
            "messages": [m.to_dict() for m in self.messages],
            "summary": self.summary(),
        }, indent=2, default=str)

    def export_mermaid(self) -> str:
        """Generate a Mermaid sequence diagram."""
        lines = ["sequenceDiagram", "    participant Client", "    participant Proxy", "    participant Server"]
        for m in self.messages:
            if m.is_request:
                lines.append(f"    Client->>+Proxy: {m.method}(id={m.message.get('id')})")
                lines.append(f"    Proxy->>+Server: {m.method}")
            elif m.is_response and "result" in m.message:
                latency = self.latency_for(m.message.get("id"))
                lat_str = f" [{latency:.0f}ms]" if latency else ""
                lines.append(f"    Server-->>-Proxy: result{lat_str}")
                lines.append(f"    Proxy-->>-Client: result (id={m.message.get('id')}){lat_str}")
            elif m.is_response and "error" in m.message:
                lines.append(f"    Server-->>-Proxy: ERROR")
                lines.append(f"    Proxy-->>-Client: ERROR (id={m.message.get('id')})")
        return "\n".join(lines)
