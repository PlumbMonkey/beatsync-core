#!/usr/bin/env python3
"""
Quick test to upload audio file to /api/analysis and inspect the response
"""
import requests
import json

url = "http://127.0.0.1:8000/api/analysis"
test_file = "d:/Dev Projects 2026/BEATSYNC/beatsync-core/fixtures/audio/click_120.wav"

print(f"Uploading test file: {test_file}")
print(f"Target endpoint: {url}")

with open(test_file, 'rb') as f:
    files = {"file": f}
    try:
        response = requests.post(url, files=files, timeout=30)
        print(f"\nHTTP Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body:")
        if response.headers.get('content-type', '').startswith('application/json'):
            try:
                print(json.dumps(response.json(), indent=2))
            except:
                print(response.text)
        else:
            print(response.text)
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
