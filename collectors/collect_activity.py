#!/usr/bin/env python3
import json
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Constants
JST = timezone(timedelta(hours=9))
PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "src" / "data"
OUTPUT_FILE = OUTPUT_DIR / "activity.json"
SESSIONS_DIR = Path.home() / ".openclaw" / "agents" / "main" / "sessions"

def log(msg):
    print(f"[activity] {msg}", file=sys.stderr)

def get_recent_activity(limit=15):
    activities = []
    try:
        if not SESSIONS_DIR.is_dir():
            return []
        
        # Get all .jsonl files, sorted by mtime
        jsonl_files = sorted(
            SESSIONS_DIR.glob("*.jsonl"),
            key=lambda f: f.stat().st_mtime,
            reverse=True
        )
        
        for f in jsonl_files[:10]: # Check last 10 sessions
            with open(f, 'r') as file:
                lines = file.readlines()
                for line in reversed(lines):
                    try:
                        data = json.loads(line)
                        if data.get('type') == 'message':
                            msg = data.get('message', {})
                            role = msg.get('role')
                            content = msg.get('content', [])
                            
                            if role in ['user', 'assistant']:
                                # Convert ISO timestamp (handling Z or +00:00)
                                ts_str = data.get('timestamp')
                                if ts_str:
                                    timestamp = datetime.fromisoformat(ts_str.replace('Z', '+00:00')).astimezone(JST)
                                else:
                                    timestamp = datetime.fromtimestamp(f.stat().st_mtime, tz=JST)
                                
                                text = ""
                                for item in content:
                                    if item.get('type') == 'text':
                                        text += item.get('text', '')
                                
                                # Truncate and clean
                                text = text.strip().replace('\n', ' ')
                                # Filter out the heartbeat and progress reporting garbage if possible
                                if "HEARTBEAT" in text and role == "user": continue
                                if "[cron:" in text: continue
                                
                                text = text[:120] + ("..." if len(text) > 120 else "")
                                if not text or len(text) < 10: continue
                                
                                activities.append({
                                    "timestamp": timestamp.isoformat(),
                                    "role": role,
                                    "text": text,
                                    "type": "chat"
                                })
                                if len(activities) >= limit: break
                    except:
                        continue
            if len(activities) >= limit: break
            
    except Exception as e:
        log(f"Error: {e}")
    
    return sorted(activities, key=lambda x: x['timestamp'], reverse=True)

def main():
    if not OUTPUT_DIR.exists():
        os.makedirs(OUTPUT_DIR)
    
    activities = get_recent_activity()
    output = {
        "timestamp": datetime.now(JST).isoformat(),
        "activities": activities
    }
    
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    log(f"Wrote {len(activities)} activities to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
