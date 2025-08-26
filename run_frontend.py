#!/usr/bin/env python3
"""
HealthSync Frontend Startup Script
"""
import subprocess
import sys
import os
from pathlib import Path

def main():
    frontend_dir = Path(__file__).parent / "frontend"
    
    if not frontend_dir.exists():
        print("❌ Frontend directory not found!")
        sys.exit(1)
    
    print("🎨 Starting HealthSync Frontend...")
    print(f"📁 Frontend directory: {frontend_dir}")
    
    try:
        # Check if npm is available
        try:
            subprocess.run(["npm", "--version"], check=True, capture_output=True, shell=True)
            print("✅ npm found successfully")
        except:
            print("❌ npm not found! Please install Node.js or restart your terminal")
            sys.exit(1)
        
        # Change to frontend directory and run npm dev
        os.chdir(frontend_dir)
        
        # Check if node_modules exists, if not run npm install
        if not (frontend_dir / "node_modules").exists():
            print("📦 Installing frontend dependencies...")
            subprocess.run(["npm", "install"], check=True, shell=True)
            print("✅ Dependencies installed!")
        
        print("🚀 Starting development server...")
        subprocess.run(["npm", "run", "dev"], check=True, shell=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting frontend: {e}")
        print("💡 Make sure you've run 'npm install' in the frontend directory")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ npm not found! Please install Node.js or restart your terminal")
        sys.exit(1)

if __name__ == "__main__":
    main()
