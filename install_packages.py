#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kloud Package Installation Script
Resolves conflicts between Python backend and npm frontend packages
"""

import os
import sys
import subprocess
import json

def run_command(cmd, cwd=None, description=""):
    """Run a command and return success status"""
    try:
        print(f"🔧 {description}")
        print(f"   Command: {cmd}")
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   ✅ Success")
            return True
        else:
            print(f"   ❌ Failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    print("🚀 KLOUD PACKAGE INSTALLATION")
    print("=" * 50)

    workspace_root = os.getcwd()

    # 1. Install root npm packages
    print("\n📦 Installing root npm packages...")
    if not run_command("npm install", workspace_root, "Root npm install"):
        print("❌ Root npm install failed")
        return False

    # 2. Install apps/web npm packages
    web_dir = os.path.join(workspace_root, "apps", "web")
    if os.path.exists(web_dir):
        print("\n📦 Installing apps/web npm packages...")
        if not run_command("npm install", web_dir, "Apps/web npm install"):
            print("❌ Apps/web npm install failed")
            return False

    # 3. Install frontend npm packages
    frontend_dir = os.path.join(workspace_root, "frontend")
    if os.path.exists(frontend_dir):
        print("\n📦 Installing frontend npm packages...")
        if not run_command("npm install", frontend_dir, "Frontend npm install"):
            print("❌ Frontend npm install failed")
            return False

    # 4. Install Python packages
    print("\n🐍 Installing Python packages...")
    if not run_command("pip install -r requirements.txt", workspace_root, "Python requirements install"):
        print("❌ Python requirements install failed")
        return False

    # 5. Install apps/api Python packages
    api_dir = os.path.join(workspace_root, "apps", "api")
    if os.path.exists(os.path.join(api_dir, "requirements.txt")):
        print("\n🐍 Installing apps/api Python packages...")
        if not run_command("pip install -r requirements.txt", api_dir, "Apps/api Python requirements install"):
            print("❌ Apps/api Python requirements install failed")
            return False

    print("\n🎉 ALL PACKAGES INSTALLED SUCCESSFULLY!")
    print("\n💡 You can now run:")
    print("   Backend: python start_Kloud.py")
    print("   Frontend: cd frontend && npm run dev")
    print("   Web App: cd apps/web && npm run dev")

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

