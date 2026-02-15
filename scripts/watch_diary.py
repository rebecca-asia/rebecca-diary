#!/usr/bin/env python3
"""
watch_diary.py — Real-time Diary Updater.

Watches Obsidian Vault & Memory directory.
Triggers update_diary.py on change.
"""
import sys
import time
import subprocess
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- Config ---
WATCH_DIRS = [
    Path("/Users/rebeccacyber/.openclaw/workspace/memory"),
    Path("/Users/rebeccacyber/Documents/Obsidian Vault"),
]
UPDATE_SCRIPT = Path(__file__).resolve().parent / "update_diary.py"

class DiaryHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.is_directory:
            return
        if not event.src_path.endswith(".md"):
            return
        
        print(f"Detect change: {event.src_path}")
        self.trigger_update()

    def on_created(self, event):
        if not event.src_path.endswith(".md"):
            return
        print(f"Detect new file: {event.src_path}")
        self.trigger_update()

    def trigger_update(self):
        print("Triggering diary update...", flush=True)
        try:
            subprocess.run([sys.executable, str(UPDATE_SCRIPT)], check=True)
            print("Update complete.", flush=True)
        except subprocess.CalledProcessError as e:
            print(f"Update failed: {e}", flush=True)
        except Exception as e:
            print(f"Unexpected error during update: {e}", flush=True)

def main():
    observer = Observer()
    handler = DiaryHandler()

    print("Starting Diary Watchdog...", flush=True)
    for d in WATCH_DIRS:
        if d.is_dir():
            print(f"Watching: {d}", flush=True)
            observer.schedule(handler, str(d), recursive=False)
        else:
            print(f"Warning: Directory not found: {d}", flush=True)

    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()
