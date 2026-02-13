#!/usr/bin/env python3
"""
Asana API Collector
Fetches tasks assigned to Rebecca from samuraitechnology.jp workspace
"""

import requests
import json
from datetime import datetime
from pathlib import Path

# Configuration
TOKEN_FILE = Path.home() / ".openclaw" / ".asana_token"
WORKSPACE_NAME = "samuraitechnology.jp"
OUTPUT_FILE = Path(__file__).parent.parent / "data" / "asana_tasks.json"

def read_token():
    """Read Asana Personal Access Token from file"""
    with open(TOKEN_FILE, 'r') as f:
        return f.read().strip()

def get_headers(token):
    """Create API headers"""
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

def get_workspace_gid(headers, workspace_name):
    """Find workspace GID by name"""
    response = requests.get("https://app.asana.com/api/1.0/workspaces", headers=headers)
    response.raise_for_status()
    
    workspaces = response.json()['data']
    for ws in workspaces:
        if workspace_name.lower() in ws['name'].lower():
            return ws['gid']
    
    raise ValueError(f"Workspace '{workspace_name}' not found")

def get_user_gid(headers):
    """Get current user's GID"""
    response = requests.get("https://app.asana.com/api/1.0/users/me", headers=headers)
    response.raise_for_status()
    
    user = response.json()['data']
    return user['gid'], user['name']

def get_tasks(headers, workspace_gid, user_gid):
    """Fetch active tasks assigned to user"""
    url = "https://app.asana.com/api/1.0/tasks"
    params = {
        "workspace": workspace_gid,
        "assignee": user_gid,
        "completed_since": "now",
        "opt_fields": "name,due_on,due_at,completed,notes,projects.name,tags.name,created_at,modified_at"
    }
    
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    
    return response.json()['data']

def main():
    """Main execution"""
    try:
        # Setup
        token = read_token()
        headers = get_headers(token)
        
        # Get workspace and user
        workspace_gid = get_workspace_gid(headers, WORKSPACE_NAME)
        user_gid, user_name = get_user_gid(headers)
        
        # Fetch tasks
        tasks = get_tasks(headers, workspace_gid, user_gid)
        
        # Prepare output
        output = {
            "timestamp": datetime.now().isoformat(),
            "workspace": WORKSPACE_NAME,
            "workspace_gid": workspace_gid,
            "user": user_name,
            "user_gid": user_gid,
            "task_count": len(tasks),
            "tasks": tasks
        }
        
        # Save to file
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Fetched {len(tasks)} tasks from {WORKSPACE_NAME}")
        print(f"📁 Saved to: {OUTPUT_FILE}")
        
        # Print summary
        if tasks:
            print("\n📋 Tasks:")
            for task in tasks:
                due = task.get('due_on') or task.get('due_at') or 'No due date'
                projects = ', '.join([p['name'] for p in task.get('projects', [])])
                print(f"  - {task['name']}")
                print(f"    Due: {due} | Projects: {projects}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
