#!/usr/bin/env python3
"""
DKT Microservice Startup Script

This script helps start the DKT microservice with proper error handling
and dependency checking.
"""

import sys
import subprocess
import os
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        return False
    return True

def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        return True
    except subprocess.CalledProcessError:
        print("Error: Failed to install dependencies")
        return False

def start_service(host="0.0.0.0", port=8001, reload=False):
    """Start the DKT microservice"""
    print(f"Starting DKT microservice on {host}:{port}")
    
    cmd = [
        sys.executable, "-m", "uvicorn", 
        "main:app",
        "--host", host,
        "--port", str(port)
    ]
    
    if reload:
        cmd.append("--reload")
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError:
        print("Error: Failed to start service")
        return False
    except KeyboardInterrupt:
        print("\nShutting down DKT microservice...")
        return True

def main():
    """Main startup function"""
    print("=" * 50)
    print("DKT Microservice Startup")
    print("=" * 50)
    
    # Change to script directory
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)
    print(f"Working directory: {script_dir}")
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check if requirements.txt exists
    if not Path("requirements.txt").exists():
        print("Error: requirements.txt not found")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Parse command line arguments
    reload = "--reload" in sys.argv
    host = "0.0.0.0"
    port = 8001
    
    for i, arg in enumerate(sys.argv):
        if arg == "--host" and i + 1 < len(sys.argv):
            host = sys.argv[i + 1]
        elif arg == "--port" and i + 1 < len(sys.argv):
            try:
                port = int(sys.argv[i + 1])
            except ValueError:
                print(f"Error: Invalid port number: {sys.argv[i + 1]}")
                sys.exit(1)
    
    print(f"Configuration:")
    print(f"  Host: {host}")
    print(f"  Port: {port}")
    print(f"  Reload: {reload}")
    print()
    
    # Start the service
    start_service(host, port, reload)

if __name__ == "__main__":
    main()