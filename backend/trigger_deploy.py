#!/usr/bin/env python3
"""
Deployment Trigger Script
This script creates a file that will trigger a new Railway deployment
"""

import os
import time
from pathlib import Path

def create_deploy_trigger():
    """Create a file that will trigger Railway to redeploy"""
    trigger_file = Path("deploy_trigger.txt")
    
    # Create a file with current timestamp
    with open(trigger_file, "w") as f:
        f.write(f"Deploy trigger created at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("This file triggers Railway to redeploy with migration fixes\n")
    
    print(f"✅ Created deploy trigger: {trigger_file}")
    print("📦 Railway will detect this change and redeploy")
    print("🔄 The new deployment will include database migrations")

if __name__ == "__main__":
    create_deploy_trigger() 