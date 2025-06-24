#!/usr/bin/env python3
"""
Quick test of the fixed API
"""

import json
import time
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

def test_api():
    """Test the fixed API endpoints."""
    
    base_url = "http://localhost:8000"
    
    print("Testing Helix AI Engine API...")
    
    # Test 1: API Status
    print("1. API Status...", end=" ")
    try:
        with urlopen(f"{base_url}/") as response:
            data = json.loads(response.read().decode())
            print(f"PASS ({data.get('layers_initialized', 0)} layers)")
    except Exception as e:
        print(f"FAIL ({e})")
        return False
    
    # Test 2: Smart endpoint (semantic layer only)
    print("2. Smart Endpoint...", end=" ")
    try:
        request_data = {
            "intent": "login button",
            "platform": "salesforce_lightning",
            "html_content": '<button type="submit">Login</button>'
        }
        
        req = Request(f"{base_url}/find_element_smart", 
                     data=json.dumps(request_data).encode('utf-8'))
        req.add_header('Content-Type', 'application/json')
        
        with urlopen(req) as response:
            data = json.loads(response.read().decode())
            if data.get("found"):
                print(f"PASS ({data.get('selector')}, {data.get('confidence', 0):.2f})")
            else:
                print("FAIL (not found)")
                return False
    except Exception as e:
        print(f"FAIL ({e})")
        return False
    
    # Test 3: Comprehensive endpoint
    print("3. Comprehensive Endpoint...", end=" ")
    try:
        request_data = {
            "intent": "username field",
            "platform": "salesforce_lightning",
            "html_content": '<input type="email" placeholder="Username">',
            "max_strategies": 5
        }
        
        req = Request(f"{base_url}/find_element_comprehensive", 
                     data=json.dumps(request_data).encode('utf-8'))
        req.add_header('Content-Type', 'application/json')
        
        with urlopen(req) as response:
            data = json.loads(response.read().decode())
            if data.get("found"):
                stats = data.get("stats", {})
                print(f"PASS ({len(data.get('strategies', []))} strategies, {stats.get('layers_executed', 0)} layers)")
            else:
                print("FAIL (not found)")
                return False
    except Exception as e:
        print(f"FAIL ({e})")
        return False
    
    print("\n✅ All critical tests passed! Helix AI Engine is working.")
    return True

if __name__ == "__main__":
    success = test_api()
    if not success:
        print("\n❌ Tests failed. Check the API server.")