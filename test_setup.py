#!/usr/bin/env python3
"""
Test script to verify ADB connection and template matching setup
"""

import os
import sys
import subprocess
import json

def test_adb_installation():
    """Test if ADB is available in PATH"""
    try:
        result = subprocess.run(["adb", "version"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ ADB is installed and accessible")
            print(f"   Version: {result.stdout.strip()}")
            return True
        else:
            print("❌ ADB is installed but not working properly")
            return False
    except FileNotFoundError:
        print("❌ ADB not found in PATH")
        print("   Please install Android SDK Platform Tools and add to PATH")
        return False
    except subprocess.TimeoutExpired:
        print("❌ ADB command timeout")
        return False

def test_config_file():
    """Test if config.json exists and is valid"""
    try:
        with open("config.json", 'r') as f:
            config = json.load(f)
        print("✅ config.json is valid")
        print(f"   Device address: {config['adb']['device_address']}")
        return True
    except FileNotFoundError:
        print("❌ config.json not found")
        return False
    except json.JSONDecodeError:
        print("❌ config.json contains invalid JSON")
        return False

def test_template_images():
    """Test if all required template images exist"""
    required_images = [
        "Career.png", "next.png", "auto_select_1.png", "auto_select_2.png",
        "start_career_1.png", "start_career_2.png", "skip.png", "skip_btn.png",
        "confirm.png", "skip_off.png", "menu.png", "give_up_1.png", "give_up_2.png",
        "restore.png", "use.png", "max.png", "close.png"
    ]
    
    missing_images = []
    for image in required_images:
        image_path = os.path.join("assets", "buttons", image)
        if not os.path.exists(image_path):
            missing_images.append(image)
    
    if not missing_images:
        print("✅ All required template images are present")
        return True
    else:
        print("❌ Missing template images:")
        for image in missing_images:
            print(f"   - {image}")
        return False

def test_adb_connection():
    """Test ADB connection to device"""
    try:
        # Load config to get device address
        with open("config.json", 'r') as f:
            config = json.load(f)
        
        device_address = config['adb']['device_address']
        
        # Try to connect
        result = subprocess.run(
            ["adb", "connect", device_address],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if "connected" in result.stdout.lower():
            print(f"✅ Successfully connected to {device_address}")
            return True
        else:
            print(f"❌ Failed to connect to {device_address}")
            print(f"   Response: {result.stdout.strip()}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing ADB connection: {e}")
        return False

def test_python_dependencies():
    """Test if required Python packages are installed"""
    required_packages = ["cv2", "numpy"]
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == "cv2":
                import cv2
                print(f"✅ OpenCV version: {cv2.__version__}")
            elif package == "numpy":
                import numpy
                print(f"✅ NumPy version: {numpy.__version__}")
        except ImportError:
            missing_packages.append(package)
    
    if not missing_packages:
        print("✅ All required Python packages are installed")
        return True
    else:
        print("❌ Missing Python packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("   Run: pip install -r requirements.txt")
        return False

def main():
    """Run all tests"""
    print("🔍 Testing Uma Automation Setup...\n")
    
    tests = [
        ("ADB Installation", test_adb_installation),
        ("Configuration File", test_config_file),
        ("Template Images", test_template_images),
        ("Python Dependencies", test_python_dependencies),
        ("ADB Connection", test_adb_connection)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"Testing {test_name}...")
        if test_func():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your setup is ready.")
        print("   You can now run: python uma_automation.py")
    else:
        print("⚠️  Some tests failed. Please fix the issues above before running the automation.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
