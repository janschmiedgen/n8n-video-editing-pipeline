#!/usr/bin/env python3
"""
Test script for n8n Video Processing Pipeline API
================================================

Tests the API endpoints and functionality.
"""

import requests
import json
import time

# API configuration
API_URL = "http://localhost:5000"

def test_health_endpoint():
    """Test the health check endpoint"""
    print("Testing /health endpoint...")
    try:
        response = requests.get(f"{API_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ API is not running. Start it with: python3 n8n-video-api.py")

def test_status_endpoint():
    """Test the status endpoint"""
    print("\nTesting /status endpoint...")
    try:
        response = requests.get(f"{API_URL}/status")
        if response.status_code == 200:
            print("✅ Status check passed")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"❌ Status check failed: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ API is not running")

def test_process_endpoint():
    """Test the main processing endpoint with sample data"""
    print("\nTesting /process endpoint...")
    
    # Sample test data (you'll need to adjust the input_file path)
    test_data = [
        {
            "input_file": "/opt/n8n_scripts/video/_input-files/testvideo-portrait.MOV",
            "target_formats": ["portrait", "landscape"],
            "logo_file": "codify-logo-blur.png",
            "icon_file": "codify-icon.png",
            "socialmediahandle_file": "codify-sm-handle.png",
            "enable_captions": True,
            "captiontemplate": "landscape_fancy.ass -style social"
        }
    ]
    
    try:
        print("Sending request...")
        print(f"Data: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(
            f"{API_URL}/process",
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=600  # 10 minutes timeout
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Processing request completed")
        else:
            print(f"❌ Processing failed: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ API is not running")
    except requests.exceptions.Timeout:
        print("❌ Request timed out (processing took too long)")

if __name__ == "__main__":
    print("=== n8n Video Processing API Test ===")
    
    test_health_endpoint()
    test_status_endpoint()
    
    # Uncomment to test processing (make sure you have a test video file)
    # test_process_endpoint()
    
    print("\n=== Test Complete ===")