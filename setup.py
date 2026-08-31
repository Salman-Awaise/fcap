#!/usr/bin/env python3
"""
FCAP Enterprise Setup Script
"""

import os
import subprocess
import sys

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"{description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"{description} failed: {e.stderr}")
        return False

def main():
    print("FCAP Enterprise Setup")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("Python 3.8+ is required")
        sys.exit(1)
    
    print(f"Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Install requirements
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        print("Failed to install dependencies")
        sys.exit(1)
    
    # Check for HF_TOKEN
    if not os.getenv("HF_TOKEN"):
        print("HF_TOKEN environment variable not set")
        print("   Please set your Hugging Face token:")
        print("   export HF_TOKEN='your_token_here'")
        print("   Or add it to your .env file")
    
    print("\nSetup completed successfully!")
    print("\nTo start the platform:")
    print("  python3 main.py")
    print("\nAccess points:")
    print("  Patient Interface: http://localhost:8000")
    print("  Clinic Interface: http://localhost:8000/clinic")
    print("  Admin Interface: http://localhost:8000/admin")
    print("  Health Check: http://localhost:8000/health/llm")

if __name__ == "__main__":
    main()
