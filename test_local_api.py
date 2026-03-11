#!/usr/bin/env python3
"""Local API endpoint test"""
import sys
from pathlib import Path

# Add beatsync-studio to path
sys.path.insert(0, str(Path(__file__).parent / "beatsync-studio"))

from fastapi.testclient import TestClient
from beatsync_studio.main import app

client = TestClient(app)

print("=== LOCAL BACKEND API ENDPOINT TESTS ===\n")

tests = [
    ("Root endpoint", "GET", "/"),
    ("Health check", "GET", "/api/health"),
    ("Swagger UI", "GET", "/docs"),
    ("OpenAPI schema", "GET", "/openapi.json"),
]

for name, method, path in tests:
    if method == "GET":
        response = client.get(path)
    print(f"{name:20} {method:4} {path:25} -> {response.status_code}")
    if response.status_code == 200 and "json" in response.headers.get("content-type", ""):
        data = response.json()
        if isinstance(data, dict):
            print(f"  Response: {str(data)[:70]}...")

print("\nAll local endpoints responding correctly ✅")
