#!/usr/bin/env python3
"""
Simple DKT Microservice Startup
Bypasses dependency installation issues by using minimal requirements
"""

import subprocess
import sys
import os
import time

def main():
    print("=" * 50)
    print("Simple DKT Microservice Startup")
    print("=" * 50)
    
    # Change to the correct directory
    service_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(service_dir)
    print(f"Working directory: {service_dir}")
    
    # Try to install minimal dependencies directly
    print("Installing minimal dependencies...")
    try:
        # Install only essential packages
        subprocess.run([sys.executable, "-m", "pip", "install", 
                       "fastapi==0.104.1", "uvicorn==0.24.0", "pydantic==2.5.0"], 
                      check=True, capture_output=False)
        print("✅ Essential dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Some dependencies failed, continuing anyway: {e}")
    
    print("\nStarting DKT Microservice...")
    try:
        # Start the service directly with main.py
        cmd = [sys.executable, "main.py"]
        print(f"Running command: {' '.join(cmd)}")
        
        # Run the service
        subprocess.run(cmd, check=False)
        
    except Exception as e:
        print(f"❌ Failed to start DKT service: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)