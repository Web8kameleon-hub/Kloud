#!/usr/bin/env python3
"""
🧠 Kloud Industrial Backend - Test Script
===============================================
Test script për verifikimin e të gjithë endpoints të API-së
"""

import requests
import time
import threading
from Kloud_industrial_api import app
import uvicorn
import json

def start_server():
    """Start server in background thread"""
    uvicorn.run(app, host='127.0.0.1', port=8000, log_level='error')

def test_endpoint(url, description):
    """Test a single endpoint"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {description}: {url}")
            return True, data
        else:
            print(f"❌ {description}: {url} - Status {response.status_code}")
            return False, None
    except Exception as e:
        print(f"❌ {description}: {url} - Error: {e}")
        return False, None

def main():
    """Main test function"""
    print("🧠 Kloud INDUSTRIAL BACKEND - COMPREHENSIVE TEST")
    print("=" * 60)

    # Start server in background
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    # Wait for server to start
    print("⏳ Starting server...")
    time.sleep(3)

    # Test endpoints
    endpoints = [
        ("http://localhost:8000/", "Root Endpoint"),
        ("http://localhost:8000/health", "Health Check"),
        ("http://localhost:8000/status", "System Status"),
        ("http://localhost:8000/api/alba/status", "ALBA Status"),
        ("http://localhost:8000/asi/status", "ASI Status"),
        ("http://localhost:8000/asi/health", "ASI Health"),
        ("http://localhost:8000/api/data-sources", "Data Sources"),
        ("http://localhost:8000/db/ping", "Database Ping"),
        ("http://localhost:8000/redis/ping", "Redis Ping"),
    ]

    results = []
    for url, description in endpoints:
        success, data = test_endpoint(url, description)
        results.append((url, success, data))

    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)

    successful = sum(1 for _, success, _ in results if success)
    total = len(results)

    print(f"✅ Successful endpoints: {successful}/{total}")
    print(f"❌ Failed endpoints: {total - successful}/{total}")

    if successful == total:
        print("\n🎉 ALL ENDPOINTS OPERATIONAL!")
        print("🌐 Kloud Industrial Backend is fully functional")
        print("📡 Server: http://localhost:8000")

        # Show sample data from key endpoints
        print("\n" + "=" * 60)
        print("📋 SAMPLE DATA FROM KEY ENDPOINTS")
        print("=" * 60)

        for url, success, data in results:
            if success and data:
                endpoint_name = url.split('/')[-1] if url != "http://localhost:8000/" else "root"
                print(f"\n🔍 {endpoint_name.upper()}:")
                if isinstance(data, dict):
                    for key, value in list(data.items())[:3]:  # Show first 3 keys
                        print(f"   {key}: {value}")
                else:
                    print(f"   {data}")
    else:
        print(f"\n⚠️  {total - successful} endpoints need attention")

    print("\n" + "=" * 60)
    print("🔄 Server will continue running in background")
    print("💡 Use Ctrl+C to stop the server")
    print("=" * 60)

if __name__ == "__main__":
    main()

