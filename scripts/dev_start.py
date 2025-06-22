#!/usr/bin/env python3
"""
Helix Development Startup Script
================================

Starts the development environment with all dependencies.
"""

import os
import sys
import subprocess
import time
import asyncio
from pathlib import Path


def check_requirements():
    """Check if all required tools are available."""
    # Check Python (try both python and python3)
    python_available = False
    for python_cmd in ["python", "python3"]:
        try:
            result = subprocess.run([python_cmd, "--version"], 
                                  capture_output=True, check=True, text=True)
            if "Python 3" in result.stdout:
                python_available = True
                break
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    
    if not python_available:
        print("❌ Python 3 is required but not found")
        print("   Please install Python 3.10+ from https://python.org")
        sys.exit(1)
    
    # Check Docker tools
    docker_tools = ["docker", "docker-compose"]
    missing = []
    
    for tool in docker_tools:
        try:
            subprocess.run([tool, "--version"], 
                         capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            missing.append(tool)
    
    if missing:
        print(f"❌ Missing required tools: {', '.join(missing)}")
        if "docker" in missing:
            print("   Please install Docker Desktop from https://docker.com")
        if "docker-compose" in missing:
            print("   Docker Compose should be included with Docker Desktop")
        sys.exit(1)
    
    print("✅ All required tools are available")


def setup_environment():
    """Set up the development environment."""
    # Check if .env exists, if not copy from .env.example
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        print("📋 Creating .env file from .env.example")
        env_file.write_text(env_example.read_text())
        print("⚠️  Please edit .env file with your OpenAI API key")
        return False
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        with open(".env", "r") as f:
            env_content = f.read()
        
        if "your_openai_api_key_here" in env_content:
            print("⚠️  Please set your OPENAI_API_KEY in .env file")
            return False
    
    return True


def start_services():
    """Start Docker services."""
    print("🚀 Starting Helix services...")
    
    try:
        # Start infrastructure services first
        subprocess.run([
            "docker-compose", "up", "-d", 
            "postgres", "redis", "prometheus", "grafana"
        ], check=True)
        
        print("⏳ Waiting for services to be ready...")
        time.sleep(10)
        
        # Start the main API service
        subprocess.run([
            "docker-compose", "up", "-d", "helix-api"
        ], check=True)
        
        print("✅ All services started successfully")
        print("\n🌐 Available endpoints:")
        print("   - API:        http://localhost:8000")
        print("   - Docs:       http://localhost:8000/docs")
        print("   - Grafana:    http://localhost:3000 (admin/admin)")
        print("   - Prometheus: http://localhost:9090")
        print("   - Database:   localhost:5432 (helix/helix_password)")
        print("   - Redis:      localhost:6379")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start services: {e}")
        return False


def install_dependencies():
    """Install Python dependencies locally for development."""
    print("📦 Installing Python dependencies...")
    
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True)
        
        # Install Playwright browsers
        subprocess.run([
            sys.executable, "-m", "playwright", "install", "chromium"
        ], check=True)
        
        print("✅ Dependencies installed")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def run_tests():
    """Run basic tests to verify setup."""
    print("🧪 Running tests to verify setup...")
    
    try:
        subprocess.run([
            sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"
        ], check=True)
        
        print("✅ Tests passed")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Some tests failed: {e}")
        return False


def main():
    """Main setup routine."""
    print("🎯 Helix Development Environment Setup")
    print("=====================================\n")
    
    # Step 1: Check requirements
    check_requirements()
    
    # Step 2: Setup environment
    if not setup_environment():
        sys.exit(1)
    
    # Step 3: Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Step 4: Start services
    if not start_services():
        sys.exit(1)
    
    # Step 5: Run tests
    run_tests()
    
    print("\n🎉 Helix development environment is ready!")
    print("\nNext steps:")
    print("1. Visit http://localhost:8000/docs to see the API documentation")
    print("2. Try the example request:")
    print("""
    curl -X POST "http://localhost:8000/find_element" \\
         -H "Content-Type: application/json" \\
         -d '{
           "platform": "salesforce_lightning",
           "url": "https://example.com",
           "intent": "submit button",
           "page_type": "form"
         }'
    """)
    print("3. Monitor metrics at http://localhost:3000")


if __name__ == "__main__":
    main()