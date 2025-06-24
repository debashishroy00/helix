#!/usr/bin/env python3
"""
Quick API restart script for testing
"""

import uvicorn
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.api.main import app

if __name__ == "__main__":
    print("🚀 Starting Helix AI Engine API...")
    print("   Fixed division by zero issues")
    print("   Server will start on http://localhost:8000")
    print("   Press Ctrl+C to stop")
    print()
    
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    except KeyboardInterrupt:
        print("\n🔽 Server stopped")
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        sys.exit(1)