#!/usr/bin/env python3

"""
Test script to verify imports work correctly
"""

import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

print("🧪 Testing imports...")

try:
    from app.core.config import settings
    print("✅ Settings imported successfully")
except Exception as e:
    print(f"❌ Settings import failed: {e}")
    sys.exit(1)

try:
    from app.api.v1.api import api_router
    print("✅ API router imported successfully")
except Exception as e:
    print(f"❌ API router import failed: {e}")
    sys.exit(1)

try:
    from app.core.database import engine
    print("✅ Database engine imported successfully")
except Exception as e:
    print(f"❌ Database engine import failed: {e}")
    sys.exit(1)

try:
    from app.core.background_tasks import background_task_manager
    print("✅ Background task manager imported successfully")
except Exception as e:
    print(f"❌ Background task manager import failed: {e}")
    sys.exit(1)

print("🎉 All imports successful!") 