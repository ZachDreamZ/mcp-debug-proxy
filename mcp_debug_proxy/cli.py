"""
MCP Debug Proxy CLI
"""
import argparse
import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timezone

from . import __version__
from .proxy import MCPDebugProxy
from .report import generate_report
from .replay import ReplayEngine

def setup_logging(verbose: bool):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(levelname)s [%(name)s] %(message)s",
        stream=sys.stderr,
    )

def main():
    parser = argparse.ArgumentParser(
        description="MCP Debug Proxy — intercept, log, and replay MCP server traffic",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  mcp-debug -- npx @modelcontextprotocol/server-filesystem /tmp
  mcp-debug --report session.json
  mcp-debug --replay session.json --rate 2.0
  mcp-debug --mermaid session.json
""",
    )
    
    # Mode selection
    mode = parser.add_argument_group("mode (default: proxy)")
    mode.add_argument("server", nargs="*", help="MCP server command to proxy")
    mode.add_argument("--report", metavar="FILE", help="Generate text report from recorded session")
    mode.add_argument("--json", metavar="FILE", help="Export session as JSON")
    mode.add_argument("--mermaid", metavar="FILE", help="Generate Mermaid sequence diagram")
    mode.add_argument("--replay", metavar="FILE", help="Replay a recorded session")
    mode.add_argument("--list", action="store_true", help="List all recorded sessions in a directory")
    
    # Options
    parser.add_argument("--label", default=None, help="Session label")
    parser.add_argument("--out", default=None, help="Output file for session recording (.json)")
    parser.add_argument("--rate", type=float, default=1.0, help="Replay speed multiplier")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    parser.add_argument("--version", action="store_true", help="Show version")
    
    args = parser.parse_args()
    
    if args.version:
        print(f"mcp-debug v{__version__}")
        return
    
    setup_logging(args.verbose)
    
    # Report mode
    if args.report:
        with open(args.report) as f:
            data = json.load(f)
        from .core import Session
        session = Session()
        session.label = data.get("label", args.report)
        session.start_time = datetime.fromisoformat(data["start"]).timestamp() if "start" in data else 0
        session.end_time = datetime.fromisoformat(data["end"]).timestamp() if data.get("end") else session.start_time
        for md in data.get("messages", []):
            from .core import MessageRecord
            rec = MessageRecord(md["direction"], md["body"], md.get("timestamp", 0), md.get("id"))
            session.messages.append(rec)
        print(generate_report(session, format="text"))
        return
    
    # JSON export mode
    if args.json:
        with open(args.json) as f:
            data = json.load(f)
        from .core import Session
        session = Session()
        session.label = data.get("label", args.json)
        for md in data.get("messages", []):
            from .core import MessageRecord
            rec = MessageRecord(md["direction"], md["body"], md.get("timestamp", 0), md.get("id"))
            session.messages.append(rec)
        if args.out:
            with open(args.out, "w") as f:
                f.write(session.export_json())
            print(f"Session exported to {args.out}")
        else:
            print(session.export_json())
        return
    
    # Mermaid mode
    if args.mermaid:
        with open(args.mermaid) as f:
            data = json.load(f)
        from .core import Session
        session = Session()
        session.label = data.get("label", args.mermaid)
        for md in data.get("messages", []):
            from .core import MessageRecord
            rec = MessageRecord(md["direction"], md["body"], md.get("timestamp", 0), md.get("id"))
            session.messages.append(rec)
        print(session.export_mermaid())
        return
    
    # Replay mode
    if args.replay:
        with open(args.replay) as f:
            data = json.load(f)
        asyncio.run(ReplayEngine.replay_from_file(data, rate=args.rate))
        return
    
    # Proxy mode
    if not args.server:
        parser.print_help()
        return
    
    asyncio.run(MCPDebugProxy.run(args.server, label=args.label))

if __name__ == "__main__":
    main()
