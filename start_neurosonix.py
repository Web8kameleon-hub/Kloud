#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kloud Server Startup Script
"""

import uvicorn
from Kloud_industrial_api import app

if __name__ == "__main__":
    print("🚀 Starting Kloud Industrial Backend (REAL)")
    print("🌐 Web8 Division - EuroSonix")
    print("📡 Server starting on http://localhost:8000")

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8001,
        log_level="info"
    )

