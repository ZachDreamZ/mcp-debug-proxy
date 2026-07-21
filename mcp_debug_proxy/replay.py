"""
Replay Engine — replay recorded MCP sessions.
"""
import asyncio
import json
import time
import sys
from datetime import datetime, timezone

class ReplayEngine:
    @staticmethod
    async def replay_from_file(data: dict, rate: float = 1.0):
        """Replay a recorded session at a given speed multiplier."""
        messages = data.get("messages", [])
        if not messages:
            print("No messages to replay.")
            return
        
        start_ts = messages[0]["timestamp"]
        print(f"Replaying {len(messages)} messages at {rate}x speed...")
        print("---")
        
        for msg in messages:
            delay = (msg["timestamp"] - start_ts) / rate
            if delay > 0:
                await asyncio.sleep(delay)
            start_ts = msg["timestamp"]
            
            direction = ">>>" if msg["direction"] == "send" else "<<<"
            body = json.dumps(msg["body"])
            print(f"{direction} {body}", flush=True)
        
        print("---")
        print("Replay complete.")
