#!/usr/bin/env python3
"""
Test: Download functionality in Microsoft Edge
Tests: trigger download, verify completion, verify file exists

Prerequisites:
1. fsq-mac installed: pipx install fsq-mac
2. Appium server running: appium
3. macOS Accessibility permission granted
"""

import subprocess
import json
import time
import sys
import os
from pathlib import Path

MAC_CLI = "mac"
EDGE_BUNDLE_ID = "com.microsoft.edgemac"

# Test file URL (small, reliable)
TEST_DOWNLOAD_URL = "https://httpbin.org/bytes/1024"  # 1KB random bytes
TEST_DOWNLOAD_FILE = "1024"  # Default filename from httpbin

# Alternative: use a known small file
ALT_DOWNLOAD_URL = "https://www.google.com/robots.txt"
ALT_DOWNLOAD_FILE = "robots.txt"


def run_mac(*args, check=True):
    """Run mac CLI command and return parsed JSON output"""
    cmd = [MAC_CLI] + list(args)
    print(f"    $ {' '.join(cmd)}")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0 and check:
        print(f"    ❌ Error: {result.stderr or result.stdout}")
        return None
    
    try:
        return json.loads(result.stdout) if result.stdout.strip() else {}
    except json.JSONDecodeError:
        return {"raw": result.stdout}


def send_hotkey(*keys):
    """Send hotkey combination"""
    result = run_mac("input", "hotkey", *keys, check=False)
    time.sleep(0.3)
    return result and result.get("ok")


def type_text(text):
    """Type text"""
    result = run_mac("input", "type", text, check=False)
    time.sleep(0.2)
    return result and result.get("ok")


def check_environment():
    """Check critical environment requirements"""
    print("\n[Setup] Checking environment...")
    doctor = run_mac("doctor", check=False)
    if doctor:
        checks = doctor.get("error", {}).get("details", {}).get("checks", [])
        if not checks:
            checks = doctor.get("data", {}).get("checks", [])
        
        for check in checks:
            name = check.get("name")
            status = check.get("status")
            if name in ["accessibility_permission", "appium_server"]:
                if status != "pass":
                    print(f"    ❌ Critical: {name} failed")
                    return False
                print(f"    ✅ {name}: pass")
    return True


def setup_session():
    """Start session and launch Edge"""
    print("\n[Setup] Starting session...")
    session = run_mac("session", "start", check=False)
    if session and session.get("ok"):
        print(f"    ✅ Session: {session.get('data', {}).get('session_id', 'unknown')}")
    
    print("\n[Setup] Launching Edge...")
    subprocess.run(
        ["osascript", "-e", 'tell application "Microsoft Edge" to activate'],
        capture_output=True
    )
    time.sleep(1)
    return True


def get_downloads_folder():
    """Get user's Downloads folder path"""
    return Path.home() / "Downloads"


def clean_test_files():
    """Remove test files from previous runs"""
    downloads = get_downloads_folder()
    for filename in [TEST_DOWNLOAD_FILE, ALT_DOWNLOAD_FILE]:
        filepath = downloads / filename
        if filepath.exists():
            filepath.unlink()
            print(f"    Cleaned: {filepath}")


def test_trigger_download():
    """Test 1: Trigger a file download"""
    print("\n" + "=" * 50)
    print("Test 1: Trigger File Download")
    print("=" * 50)
    
    # Open new tab
    print("\n  Opening new tab...")
    if not send_hotkey("command", "t"):
        print("    ⚠️ Could not open new tab")
    
    time.sleep(0.5)
    
    # Navigate to download URL
    print(f"\n  Navigating to: {ALT_DOWNLOAD_URL}")
    
    # Focus address bar (Cmd+L)
    if not send_hotkey("command", "l"):
        print("    ❌ Could not focus address bar")
        return False
    
    time.sleep(0.3)
    
    # Type URL
    if not type_text(ALT_DOWNLOAD_URL):
        print("    ❌ Could not type URL")
        return False
    
    time.sleep(0.3)
    
    # Press Enter to navigate
    if not send_hotkey("return"):
        print("    ❌ Could not press Enter")
        return False
    
    print("    ✅ Navigation triggered")
    
    # Wait for page to load
    time.sleep(2)
    
    # Trigger download with Cmd+S (Save Page As)
    print("\n  Triggering download (Cmd+S)...")
    if not send_hotkey("command", "s"):
        print("    ❌ Could not trigger save")
        return False
    
    time.sleep(1)
    
    # Press Enter to confirm save dialog (use default location/name)
    print("    Confirming save dialog...")
    if not send_hotkey("return"):
        print("    ⚠️ Could not confirm save dialog")
    
    time.sleep(2)
    
    print("    ✅ Download triggered")
    return True


def test_verify_download():
    """Test 2: Verify download completed and file exists"""
    print("\n" + "=" * 50)
    print("Test 2: Verify Download Completed")
    print("=" * 50)
    
    downloads = get_downloads_folder()
    
    # Look for the downloaded file
    # robots.txt might be saved as robots.txt or robots.txt.html
    possible_files = [
        downloads / "robots.txt",
        downloads / "robots.txt.html",
        downloads / "robots.html",
    ]
    
    print(f"\n  Checking Downloads folder: {downloads}")
    
    # Wait a bit for download to complete
    max_wait = 10  # seconds
    found_file = None
    
    for i in range(max_wait):
        for filepath in possible_files:
            if filepath.exists():
                found_file = filepath
                break
        if found_file:
            break
        print(f"    Waiting... ({i + 1}s)")
        time.sleep(1)
    
    if found_file:
        size = found_file.stat().st_size
        print(f"\n    ✅ File found: {found_file.name}")
        print(f"    ✅ File size: {size} bytes")
        return True
    else:
        print("\n    ❌ Downloaded file not found")
        print(f"    Checked: {[f.name for f in possible_files]}")
        
        # List actual files in Downloads for debugging
        print(f"\n    Files in Downloads (recent):")
        recent_files = sorted(downloads.glob("*"), key=os.path.getmtime, reverse=True)[:5]
        for f in recent_files:
            print(f"      - {f.name}")
        
        return False


def teardown():
    """Cleanup: close tab and end session"""
    print("\n[Teardown] Cleaning up...")
    
    # Close the download tab
    send_hotkey("command", "w")
    
    # End session
    run_mac("session", "end", check=False)
    print("    ✅ Cleanup complete")


def main():
    """Main test runner"""
    print("\n" + "=" * 60)
    print("  Download Test Suite - Microsoft Edge")
    print("=" * 60)
    
    results = {}
    
    try:
        # Setup
        if not check_environment():
            print("\n❌ Environment check failed")
            sys.exit(1)
        
        if not setup_session():
            print("\n❌ Setup failed")
            sys.exit(1)
        
        # Clean previous test files
        print("\n[Setup] Cleaning previous test files...")
        clean_test_files()
        
        # Run tests
        results["trigger_download"] = test_trigger_download()
        results["verify_download"] = test_verify_download()
        
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Tests failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        teardown()
    
    # Summary
    print("\n" + "=" * 60)
    print("  Test Summary")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {name}")
    
    print(f"\n  Total: {passed}/{total} tests passed")
    print("=" * 60 + "\n")
    
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
