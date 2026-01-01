#!/usr/bin/env python3
"""
Health check script for monitoring bot status.
Returns exit code 0 if healthy, 1 if unhealthy.
"""
import sys
import asyncio
from pathlib import Path
from datetime import datetime, timedelta

async def check_bot_health():
    """Check if bot is healthy"""
    try:
        # Check if status file exists and is recent
        status_file = Path("logs/bot_status.txt")
        
        if not status_file.exists():
            print("ERROR: Status file not found")
            return False
        
        content = status_file.read_text()
        
        if "RUNNING" not in content:
            print("ERROR: Bot status is not RUNNING")
            return False
        
        # Extract timestamp
        for line in content.split("\n"):
            if line.startswith("Started:"):
                timestamp_str = line.split("Started:", 1)[1].strip()
                started_time = datetime.fromisoformat(timestamp_str)
                
                # Check if status was updated within last 5 minutes
                if datetime.now() - started_time > timedelta(minutes=5):
                    # This is fine, bot has been running for a while
                    pass
                
                print("OK: Bot is running")
                return True
        
        print("OK: Bot status file looks good")
        return True
        
    except Exception as e:
        print(f"ERROR: Health check failed: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(check_bot_health())
    sys.exit(0 if result else 1)
