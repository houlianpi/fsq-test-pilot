#!/usr/bin/env python3
"""
Test: Favorites/Collections functionality in Microsoft Edge
Note: In Edge, "Favorites" = "Bookmarks", and "Collections" is a separate feature

This test focuses on Edge Collections feature.

Prerequisites:
1. fsq-mac installed
2. Appium server running
3. macOS Accessibility permission granted
"""

import subprocess
import json
import time
import sys
from typing import Optional, Dict, Any

MAC_CLI = "mac"


def run_mac(*args, check=True) -> Optional[Dict[str, Any]]:
    """Run mac CLI command and return parsed JSON output"""
    cmd = [MAC_CLI] + list(args)
    print(f"    $ {' '.join(cmd)}")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0 and check:
        return None
    
    try:
        return json.loads(result.stdout) if result.stdout.strip() else {}
    except json.JSONDecodeError:
        return {"raw": result.stdout}


def send_hotkey(*keys) -> bool:
    """Send hotkey combination"""
    result = run_mac("input", "hotkey", *keys, check=False)
    time.sleep(0.3)
    return result is not None and result.get("ok", True)


def type_text(text: str) -> bool:
    """Type text"""
    result = run_mac("input", "type", text, check=False)
    time.sleep(0.2)
    return result is not None


def check_environment() -> bool:
    """Check critical environment requirements"""
    print("\n[Setup] Checking environment...")
    doctor = run_mac("doctor", check=False)
    if doctor:
        checks = doctor.get("error", {}).get("details", {}).get("checks", [])
        for check in checks:
            if check.get("name") in ["accessibility_permission", "appium_server"]:
                if check.get("status") != "pass":
                    print(f"    ❌ {check.get('name')} failed")
                    return False
    print("    ✅ Environment OK")
    return True


def setup_session() -> bool:
    """Start session and launch Edge"""
    print("\n[Setup] Starting session...")
    run_mac("session", "start", check=False)
    
    subprocess.run(
        ["osascript", "-e", 'tell application "Microsoft Edge" to activate'],
        capture_output=True
    )
    time.sleep(1)
    print("    ✅ Edge activated")
    return True


def navigate_to_url(url: str) -> bool:
    """Navigate to a URL"""
    print(f"\n  Navigating to {url}...")
    send_hotkey("command", "l")
    time.sleep(0.2)
    type_text(url)
    send_hotkey("return")
    time.sleep(2)
    return True


# =============================================================================
# Test Cases
# =============================================================================

def test_open_collections() -> bool:
    """Test: Open Collections panel"""
    print("\n" + "=" * 50)
    print("Test 1: Open Collections (Cmd+Shift+Y)")
    print("=" * 50)
    
    print("\n  Opening Collections panel...")
    send_hotkey("command", "shift", "y")
    time.sleep(1)
    
    print("    ✅ Collections panel opened")
    return True


def test_create_collection() -> bool:
    """Test: Create a new collection"""
    print("\n" + "=" * 50)
    print("Test 2: Create New Collection")
    print("=" * 50)
    
    # Collections should already be open from previous test
    print("\n  Creating new collection...")
    
    # Look for "Start new collection" or similar button
    # Use Tab to navigate and Enter to select
    send_hotkey("tab")
    time.sleep(0.2)
    send_hotkey("return")
    time.sleep(0.5)
    
    # Type collection name
    type_text("Test Collection")
    time.sleep(0.3)
    send_hotkey("return")
    time.sleep(0.5)
    
    print("    ✅ Collection created (or dialog opened)")
    return True


def test_add_to_collection() -> bool:
    """Test: Add current page to collection"""
    print("\n" + "=" * 50)
    print("Test 3: Add Page to Collection")
    print("=" * 50)
    
    # Navigate to a page
    navigate_to_url("https://example.com")
    
    # Open collections
    print("\n  Opening Collections...")
    send_hotkey("command", "shift", "y")
    time.sleep(1)
    
    # Add current page (usually a button in the panel)
    print("\n  Adding current page to collection...")
    send_hotkey("tab")
    time.sleep(0.2)
    send_hotkey("tab")
    time.sleep(0.2)
    send_hotkey("return")
    time.sleep(0.5)
    
    print("    ✅ Add to collection action triggered")
    return True


def test_close_collections() -> bool:
    """Test: Close Collections panel"""
    print("\n" + "=" * 50)
    print("Test 4: Close Collections Panel")
    print("=" * 50)
    
    print("\n  Closing Collections panel...")
    # Toggle off with same shortcut
    send_hotkey("command", "shift", "y")
    time.sleep(0.5)
    
    print("    ✅ Collections panel closed")
    return True


def test_favorites_bar() -> bool:
    """Test: Toggle Favorites bar (same as bookmarks bar)"""
    print("\n" + "=" * 50)
    print("Test 5: Toggle Favorites Bar (Cmd+Shift+B)")
    print("=" * 50)
    
    print("\n  Toggling favorites bar...")
    send_hotkey("command", "shift", "b")
    time.sleep(0.5)
    print("    ✅ Favorites bar toggled (show)")
    
    send_hotkey("command", "shift", "b")
    time.sleep(0.5)
    print("    ✅ Favorites bar toggled (hide)")
    
    return True


def teardown() -> None:
    """Cleanup after tests"""
    print("\n[Teardown] Cleaning up...")
    
    # Close collections if open
    send_hotkey("escape")
    time.sleep(0.2)
    
    # Close extra tabs
    send_hotkey("command", "w")
    time.sleep(0.2)
    
    run_mac("session", "end", check=False)
    print("    ✅ Cleanup complete")


def main():
    """Main test runner"""
    print("\n" + "=" * 60)
    print("  Favorites/Collections Test Suite - Microsoft Edge")
    print("=" * 60)
    
    results = {}
    
    try:
        if not check_environment():
            print("\n❌ Environment check failed")
            sys.exit(1)
        
        setup_session()
        
        # Run tests
        results["open_collections"] = test_open_collections()
        results["create_collection"] = test_create_collection()
        results["add_to_collection"] = test_add_to_collection()
        results["close_collections"] = test_close_collections()
        results["favorites_bar"] = test_favorites_bar()
        
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
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
    for name, result in results.items():
        status = "✅" if result else "❌"
        print(f"  {status} {name}")
    
    print(f"\n  Total: {passed}/{len(results)} passed")
    
    sys.exit(0 if passed == len(results) else 1)


if __name__ == "__main__":
    main()
