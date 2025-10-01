#!/usr/bin/env python3
"""
FastAPI ML Analytics Test Client
Test script for the FastAPI backend
"""

import requests
import json
import time
import os
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000"
TEST_FILE = "test_data.csv"  # Change this to your test file

def test_api():
    """Test the FastAPI endpoints"""
    print("🧪 Testing FastAPI ML Analytics Backend")
    print(f"📍 Base URL: {BASE_URL}")
    print("-" * 50)
    
    # Test 1: Health Check
    print("1️⃣ Testing Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Status: {response.json()['status']}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Test 2: API Status
    print("\n2️⃣ Testing API Status...")
    try:
        response = requests.get(f"{BASE_URL}/status")
        if response.status_code == 200:
            print("✅ API status check passed")
            data = response.json()
            print(f"   Python Available: {data['python_available']}")
            print(f"   Uploads Directory: {data['uploads_directory']}")
        else:
            print(f"❌ API status check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ API status check error: {e}")
    
    # Test 3: File Upload (if test file exists)
    if os.path.exists(TEST_FILE):
        print(f"\n3️⃣ Testing File Upload with {TEST_FILE}...")
        try:
            with open(TEST_FILE, 'rb') as f:
                files = {'file': (TEST_FILE, f, 'text/csv')}
                response = requests.post(f"{BASE_URL}/upload", files=files)
            
            if response.status_code == 200:
                print("✅ File upload successful")
                data = response.json()
                file_id = data['file_id']
                print(f"   File ID: {file_id}")
                print(f"   Analysis URL: {data['analysis_url']}")
                
                # Test 4: Check Analysis Status
                print(f"\n4️⃣ Checking Analysis Status for {file_id}...")
                max_attempts = 10
                attempt = 0
                
                while attempt < max_attempts:
                    try:
                        response = requests.get(f"{BASE_URL}/analysis/{file_id}")
                        if response.status_code == 200:
                            data = response.json()
                            if data['success']:
                                analysis = data['analysis']
                                if analysis['status'] == 'completed':
                                    print("✅ Analysis completed successfully")
                                    print(f"   Churn Analysis: {'✅' if analysis['results']['churn']['success'] else '❌'}")
                                    print(f"   Segmentation: {'✅' if analysis['results']['segmentation']['success'] else '❌'}")
                                    print(f"   Sales Forecast: {'✅' if analysis['results']['sales']['success'] else '❌'}")
                                    break
                                elif analysis['status'] == 'error':
                                    print(f"❌ Analysis failed: {analysis.get('error', 'Unknown error')}")
                                    break
                                else:
                                    print(f"⏳ Analysis in progress... (attempt {attempt + 1}/{max_attempts})")
                                    time.sleep(5)
                                    attempt += 1
                            else:
                                print(f"⏳ Analysis not ready yet... (attempt {attempt + 1}/{max_attempts})")
                                time.sleep(5)
                                attempt += 1
                        else:
                            print(f"❌ Analysis check failed: {response.status_code}")
                            break
                    except Exception as e:
                        print(f"❌ Analysis check error: {e}")
                        break
                
                if attempt >= max_attempts:
                    print("⏰ Analysis timeout - check manually")
                
            else:
                print(f"❌ File upload failed: {response.status_code}")
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"❌ File upload error: {e}")
    else:
        print(f"\n3️⃣ Skipping file upload test (test file {TEST_FILE} not found)")
    
    # Test 5: Get All Analyses
    print("\n5️⃣ Testing Get All Analyses...")
    try:
        response = requests.get(f"{BASE_URL}/analysis")
        if response.status_code == 200:
            print("✅ Get all analyses successful")
            data = response.json()
            print(f"   Total analyses: {data['count']}")
        else:
            print(f"❌ Get all analyses failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Get all analyses error: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Test completed!")
    print(f"📖 API Documentation: {BASE_URL}/docs")
    print(f"🔍 Alternative Docs: {BASE_URL}/redoc")

if __name__ == "__main__":
    test_api()



