"""Tests for MCP Debug Proxy core."""
import json
import time
import pytest
from mcp_debug_proxy.core import Session, MessageRecord

class TestMessageRecord:
    def test_request_record(self):
        msg = {"jsonrpc": "2.0", "id": 1, "method": "tools/list"}
        rec = MessageRecord("send", msg, 1000.0, "abc123")
        assert rec.direction == "send"
        assert rec.method == "tools/list"
        assert rec.is_request == True
        assert rec.is_response == False
        assert rec.id == "abc123"

    def test_response_record(self):
        msg = {"jsonrpc": "2.0", "id": 1, "result": {"tools": []}}
        rec = MessageRecord("recv", msg, 1000.0)
        assert rec.is_response == True
        assert rec.is_request == False

    def test_notification_record(self):
        msg = {"jsonrpc": "2.0", "method": "notifications/initialized"}
        rec = MessageRecord("send", msg, 1000.0)
        assert rec.is_notification == True
        assert rec.is_request == False

    def test_to_dict(self):
        msg = {"jsonrpc": "2.0", "id": 1, "method": "tools/list"}
        rec = MessageRecord("send", msg, 1000000.0, "test1")
        d = rec.to_dict()
        assert d["direction"] == "send"
        assert d["method"] == "tools/list"
        assert d["id"] == "test1"

class TestSession:
    def test_empty_session(self):
        s = Session("test-session")
        assert s.label == "test-session"
        assert len(s.messages) == 0

    def test_record_send(self):
        s = Session()
        msg = {"jsonrpc": "2.0", "id": 1, "method": "tools/list"}
        rec = s.record_send(msg)
        assert len(s.messages) == 1
        assert rec.direction == "send"

    def test_record_recv(self):
        s = Session()
        msg = {"jsonrpc": "2.0", "id": 1, "result": {"tools": []}}
        rec = s.record_recv(msg)
        assert len(s.messages) == 1
        assert rec.direction == "recv"

    def test_request_response_pair(self):
        s = Session()
        s.record_send({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
        time.sleep(0.01)
        s.record_recv({"jsonrpc": "2.0", "id": 1, "result": {"tools": []}})
        s.close()
        latency = s.latency_for(1)
        assert latency is not None
        assert latency > 5  # at least 5ms

    def test_summary(self):
        s = Session()
        s.record_send({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
        s.record_recv({"jsonrpc": "2.0", "id": 1, "result": {"tools": []}})
        s.record_send({"jsonrpc": "2.0", "id": 2, "method": "resources/list"})
        s.record_recv({"jsonrpc": "2.0", "id": 2, "error": {"code": -32603, "message": "Internal error"}})
        s.close()
        summary = s.summary()
        assert summary["requests"] == 2
        assert summary["responses"] == 2
        assert summary["methods"]["tools/list"] == 1
        assert summary["methods"]["resources/list"] == 1

    def test_export_json(self):
        s = Session("export-test")
        s.record_send({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
        s.record_recv({"jsonrpc": "2.0", "id": 1, "result": {"tools": []}})
        s.close()
        exported = json.loads(s.export_json())
        assert exported["label"] == "export-test"
        assert len(exported["messages"]) == 2

    def test_mermaid_diagram(self):
        s = Session()
        s.record_send({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
        s.record_recv({"jsonrpc": "2.0", "id": 1, "result": {"tools": []}})
        s.record_send({"jsonrpc": "2.0", "id": 2, "method": "resources/list"})
        s.record_recv({"jsonrpc": "2.0", "id": 2, "error": {"code": -32603, "message": "Internal error"}})
        s.close()
        diagram = s.export_mermaid()
        assert "sequenceDiagram" in diagram
        assert "tools/list" in diagram
        assert "ERROR" in diagram
