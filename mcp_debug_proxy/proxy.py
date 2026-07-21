"""
MCP Debug Proxy Server — stdio-to-stdio proxy with recording.
"""
import asyncio
import json
import logging
import sys
from datetime import datetime, timezone
from .core import Session

log = logging.getLogger("mcp-debug.proxy")

class MCPDebugProxy:
    """Intercepts stdio MCP traffic between client and server."""

    def __init__(self, server_cmd: list[str], label: str = None, record_raw: bool = True):
        self.server_cmd = server_cmd
        self.session = Session(label)
        self.record_raw = record_raw
        self.server_proc = None
        self._running = False

    async def start(self):
        log.info(f"Starting MCP server: {self.server_cmd}")
        self.server_proc = await asyncio.create_subprocess_exec(
            *self.server_cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        self._running = True

    async def proxy_loop(self):
        """Read from stdin, forward to server, read response, forward to stdout."""
        async def read_stdin():
            buffer = ""
            while self._running:
                try:
                    line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                    if not line:
                        break
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        msg = json.loads(line)
                        self.session.record_send(msg)
                        self.server_proc.stdin.write((line + "\n").encode())
                        await self.server_proc.stdin.drain()
                    except json.JSONDecodeError:
                        log.warning(f"Invalid JSON from client: {line[:100]}")
                except EOFError:
                    break
            self._running = False

        async def read_server():
            while self._running:
                line = await self.server_proc.stdout.readline()
                if not line:
                    break
                decoded = line.decode().strip()
                if not decoded:
                    continue
                try:
                    msg = json.loads(decoded)
                    self.session.record_recv(msg)
                    print(decoded, flush=True)
                except json.JSONDecodeError:
                    print(decoded, flush=True)

        async def read_stderr():
            while self._running:
                line = await self.server_proc.stderr.readline()
                if not line:
                    break
                log.warning(f"Server stderr: {line.decode().strip()}")

        await asyncio.gather(read_stdin(), read_server(), read_stderr())
        self.session.close()

    async def stop(self):
        self._running = False
        if self.server_proc:
            self.server_proc.terminate()
            await self.server_proc.wait()

    @classmethod
    async def run(cls, server_cmd: list[str], label: str = None):
        proxy = cls(server_cmd, label)
        await proxy.start()
        try:
            await proxy.proxy_loop()
        except KeyboardInterrupt:
            pass
        finally:
            await proxy.stop()
        return proxy.session
