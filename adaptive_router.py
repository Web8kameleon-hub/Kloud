#!/usr/bin/env python3
"""
Adaptive Router: Intelligent Edge Gateway for Stigma Fabric
Routes requests intelligently based on fabric state and firewall rules
"""

import os
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify, Response
import requests

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

PORT = int(os.getenv("PORT", 8011))
OCEAN_CORE_URL = os.getenv("OCEAN_CORE_URL", "http://kloud-ocean-core:8030")

# ─────────────────────────────────────────────────────────────────
# Health & Status Endpoints
# ─────────────────────────────────────────────────────────────────


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok", "service": "adaptive-router"}), 200


@app.route("/status", methods=["GET"])
def status():
    """Service status endpoint"""
    return jsonify(
        {
            "service": "adaptive-router",
            "port": PORT,
            "ocean_core": OCEAN_CORE_URL,
            "status": "running",
        }
    ), 200


# ─────────────────────────────────────────────────────────────────
# Intelligent Routing
# ─────────────────────────────────────────────────────────────────


@app.route("/route", methods=["POST"])
def route_request():
    """
    Intelligent routing based on request characteristics and fabric state
    """
    try:
        data = request.get_json() or {}

        # Get fabric state from Ocean Core
        try:
            fabric_response = requests.get(f"{OCEAN_CORE_URL}/fabric/state", timeout=2)
            fabric_state = fabric_response.json() if fabric_response.ok else {}
        except Exception as e:
            logger.warning(f"Could not fetch fabric state: {e}")
            fabric_state = {}

        # Routing logic based on fabric state
        response = {
            "routed": True,
            "target": data.get("target", "default"),
            "fabric_state": fabric_state,
            "timestamp": str(datetime.now()),
        }

        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Routing error: {e}")
        return jsonify({"error": str(e)}), 500


# ─────────────────────────────────────────────────────────────────
# Proxy endpoints to backend services
# ─────────────────────────────────────────────────────────────────


@app.route("/proxy/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
def proxy(path):
    """Proxy requests to appropriate backend service"""
    try:
        # Route based on path prefix
        if path.startswith("fabric/"):
            target_url = f"{OCEAN_CORE_URL}/{path}"
        else:
            target_url = f"{OCEAN_CORE_URL}/{path}"

        # Forward request
        if request.method == "GET":
            resp = requests.get(target_url, timeout=5)
        elif request.method == "POST":
            resp = requests.post(target_url, json=request.get_json(), timeout=5)
        elif request.method == "PUT":
            resp = requests.put(target_url, json=request.get_json(), timeout=5)
        elif request.method == "DELETE":
            resp = requests.delete(target_url, timeout=5)
        else:
            return jsonify({"error": "Method not allowed"}), 405

        return Response(
            resp.content,
            status=resp.status_code,
            mimetype=resp.headers.get("content-type"),
        )

    except Exception as e:
        logger.error(f"Proxy error: {e}")
        return jsonify({"error": str(e)}), 500


# ─────────────────────────────────────────────────────────────────
# Startup
# ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    logger.info(f"🚀 Adaptive Router starting on port {PORT}")
    logger.info(f"📍 Ocean Core URL: {OCEAN_CORE_URL}")
    app.run(host="0.0.0.0", port=PORT, debug=False)
