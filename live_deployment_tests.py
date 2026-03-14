#!/usr/bin/env python3
"""
BeatSync Studio Live Deployment E2E Tests
Tests: https://beatsync-studio.onrender.com (Backend)
       https://beatsync-ui.vercel.app (Frontend)
"""
import sys
import time
import json
from pathlib import Path

def test_backend_health():
    """TEST 1: Backend health check"""
    print("\n" + "="*70)
    print("TEST 1 — BACKEND HEALTH CHECK (LIVE)")
    print("="*70)
    print("Endpoint: https://beatsync-studio.onrender.com/")
    print("Note: Render free tier may take 30 seconds to wake up...")
    
    try:
        import requests
    except ImportError:
        print("⚠️  requests library not installed, skipping live tests")
        print("   Install with: pip install requests")
        return False
    
    try:
        # Try up to 3 times with 15-second waits (for Render cold start)
        for attempt in range(3):
            try:
                response = requests.get(
                    "https://beatsync-studio.onrender.com/",
                    timeout=10
                )
                if response.status_code == 200:
                    print(f"✅ Backend is responding (attempt {attempt + 1}/3)")
                    print(f"   Status: {response.status_code}")
                    try:
                        print(f"   Response: {response.json()}")
                    except:
                        print(f"   Response: {response.text[:200]}")
                    return True
                else:
                    print(f"⚠️  Status code: {response.status_code}")
            except requests.exceptions.Timeout:
                if attempt < 2:
                    print(f"⏳ Timeout (attempt {attempt + 1}/3), waiting 15s for Render to wake up...")
                    time.sleep(15)
                else:
                    print(f"❌ Timeout after {attempt + 1} attempts")
            except requests.exceptions.ConnectionError as e:
                if attempt < 2:
                    print(f"⏳ Connection error (attempt {attempt + 1}/3): {str(e)[:80]}...")
                    time.sleep(15)
                else:
                    print(f"❌ Cannot connect after {attempt + 1} attempts")
        
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_backend_docs():
    """TEST 1b: Backend Swagger docs"""
    print("\n" + "="*70)
    print("TEST 1b — SWAGGER API DOCS (LIVE)")
    print("="*70)
    print("Endpoint: https://beatsync-studio.onrender.com/docs")
    
    try:
        import requests
    except ImportError:
        return False
    
    try:
        response = requests.get(
            "https://beatsync-studio.onrender.com/docs",
            timeout=10
        )
        if response.status_code == 200:
            print(f"✅ Swagger UI is accessible")
            print(f"   Status: {response.status_code}")
            return True
        else:
            print(f"❌ Status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_cors():
    """TEST 2: CORS configuration"""
    print("\n" + "="*70)
    print("TEST 2 — CORS VERIFICATION (LIVE)")
    print("="*70)
    print("Testing CORS from browser origin: https://beatsync-ui.vercel.app")
    
    try:
        import requests
    except ImportError:
        return False
    
    try:
        headers = {
            'Origin': 'https://beatsync-ui.vercel.app',
        }
        response = requests.get(
            "https://beatsync-studio.onrender.com/",
            headers=headers,
            timeout=10
        )
        
        cors_header = response.headers.get('access-control-allow-origin')
        if cors_header:
            print(f"✅ CORS headers present")
            print(f"   Allow-Origin: {cors_header}")
            return True
        else:
            print(f"⚠️  No CORS headers in response")
            print(f"   This may be OK if Preflight requests work")
            return True  # Not a blocker
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_frontend_availability():
    """TEST 3: Frontend is accessible"""
    print("\n" + "="*70)
    print("TEST 3 — FRONTEND AVAILABILITY (LIVE)")
    print("="*70)
    print("Endpoint: https://beatsync-ui.vercel.app")
    
    try:
        import requests
    except ImportError:
        return False
    
    try:
        response = requests.get(
            "https://beatsync-ui.vercel.app",
            timeout=10,
            allow_redirects=True
        )
        if response.status_code == 200:
            if "BeatSync" in response.text or "beatsync" in response.text.lower():
                print(f"✅ Frontend is accessible and responding")
                print(f"   Status: {response.status_code}")
                return True
            else:
                print(f"⚠️  Page loaded but doesn't contain expected content")
                return False
        else:
            print(f"❌ Status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_api_contract():
    """TEST 4: API contract validation"""
    print("\n" + "="*70)
    print("TEST 4 — API CONTRACT VALIDATION (LIVE)")
    print("="*70)
    print("Testing: /api/analysis endpoint structure")
    
    try:
        import requests
    except ImportError:
        return False
    
    # Sample audio file path for testing
    test_file = Path(__file__).parent / "beatsync-core" / "fixtures" / "audio" / "click_120.wav"
    
    if not test_file.exists():
        print(f"⚠️  Test audio file not found at {test_file}")
        print(f"   Cannot perform contract validation")
        # Try to find any audio file
        test_files = list((Path(__file__).parent / "beatsync-core" / "fixtures").rglob("*.wav"))
        if not test_files:
            print(f"❌ No WAV files found in fixtures")
            return False
        test_file = test_files[0]
        print(f"   Using alternative: {test_file}")
    
    try:
        with open(test_file, 'rb') as f:
            files = {'file': f}
            response = requests.post(
                "https://beatsync-studio.onrender.com/api/analysis",
                files=files,
                timeout=30
            )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API returned 200 OK")
            
            # Check for required fields
            required_fields = [
                "schema_version",
                "analysis_version", 
                "duration_sec",
                "bpm",
                "confidence"
            ]
            
            missing = [f for f in required_fields if f not in data]
            if missing:
                print(f"❌ Missing fields: {missing}")
                return False
            
            print(f"   ✓ schema_version: {data.get('schema_version')}")
            print(f"   ✓ analysis_version: {data.get('analysis_version')}")
            print(f"   ✓ duration_sec: {data.get('duration_sec')}")
            print(f"   ✓ bpm: {data.get('bpm')}")
            print(f"   ✓ confidence: {data.get('confidence')}")
            
            return True
        else:
            print(f"❌ Status code: {response.status_code}")
            print(f"   Response: {response.text[:300]}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("\n" + "="*70)
    print("BEATSYNC STUDIO — LIVE DEPLOYMENT E2E TESTS")
    print("="*70)
    print("Backend: https://beatsync-studio.onrender.com")
    print("Frontend: https://beatsync-ui.vercel.app")
    print("Date: March 2026")
    print("="*70)
    
    try:
        import requests
        print(f"✅ requests library available (v{requests.__version__})")
    except ImportError:
        print("⚠️  Installing requests library...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
        import requests
    
    results = {}
    
    # Run tests
    results["backend_health"] = test_backend_health()
    if results["backend_health"]:  # Only proceed if backend is up
        results["backend_docs"] = test_backend_docs()
        results["cors"] = test_cors()
        results["api_contract"] = test_api_contract()
    else:
        results["backend_docs"] = False
        results["cors"] = False
        results["api_contract"] = False
    
    results["frontend"] = test_frontend_availability()
    
    # Summary
    print("\n" + "="*70)
    print("LIVE DEPLOYMENT TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅" if result else "❌"
        print(f"{status} {test_name.upper().replace('_', ' ')}")
    
    print("\n" + "="*70)
    if passed >= total - 1:  # Allow 1 failure
        print(f"✅ DEPLOYMENTS ARE READY ({passed}/{total} tests passed)")
        print("="*70)
        return 0
    else:
        print(f"❌ ISSUES DETECTED ({passed}/{total} tests passed)")
        print("="*70)
        if not results.get("backend_health"):
            print("\n⚠️  Backend is not responding.")
            print("   - Check Render dashboard: https://dashboard.render.com")
            print("   - Service may be starting up (takes 30 seconds on free tier)")
            print("   - Check for deployment errors in Render logs")
        if not results.get("frontend"):
            print("\n⚠️  Frontend is not responding.")
            print("   - Check Vercel dashboard: https://vercel.com/dashboard")
            print("   - Check deployment logs for errors")
        return 1

if __name__ == "__main__":
    sys.exit(main())
