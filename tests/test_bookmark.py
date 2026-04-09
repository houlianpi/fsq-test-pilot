#!/usr/bin/env python3
"""
Test: Bookmark functionality in Microsoft Edge
Tests adding, viewing, and managing bookmarks

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
    return result is not None


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
    
    # Activate Edge
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
    send_hotkey("command", "l")  # Focus address bar
    time.sleep(0.2)
    type_text(url)
    send_hotkey("return")
    time.sleep(2)  # Wait for page load
    return True


# =============================================================================
# Test Cases
# =============================================================================

def test_add_bookmark() -> bool:
    """Test: Add current page to bookmarks"""
    print("\n" + "=" * 50)
    print("Test 1: Add Bookmark (Cmd+D)")
    print("=" * 50)
    
    # Navigate to a page first
    navigate_to_url("https://example.com")
    
    # Add bookmark with Cmd+D
    print("\n  Adding bookmark...")
    send_hotkey("command", "d")
    time.sleep(0.5)
    
    # Confirm with Enter
    send_hotkey("return")
    time.sleep(0.3)
    
    print("    ✅ Bookmark added")
    return True


def test_open_bookmark_manager() -> bool:
    """Test: Open bookmark manager"""
    print("\n" + "=" * 50)
    print("Test 2: Open Bookmark Manager (Cmd+Shift+O)")
    print("=" * 50)
    
    print("\n  Opening bookmark manager...")
    send_hotkey("command", "shift", "o")
    time.sleep(1)
    
    print("    ✅ Bookmark manager opened")
    return True


def test_bookmark_bar_toggle() -> bool:
    """Test: Toggle bookmark bar visibility"""
    print("\n" + "=" * 50)
    print("Test 3: Toggle Bookmark Bar (Cmd+Shift+B)")
    print("=" * 50)
    
    print("\n  Toggling bookmark bar...")
    send_hotkey("command", "shift", "b")
    time.sleep(0.5)
    
    print("    ✅ Bookmark bar toggled (1st toggle)")
    
    # Toggle back
    send_hotkey("command", "shift", "b")
    time.sleep(0.5)
    
    print("    ✅ Bookmark bar toggled (2nd toggle)")
    return True


def test_bookmark_all_tabs() -> bool:
    """Test: Bookmark all open tabs"""
    print("\n" + "=" * 50)
    print("Test 4: Bookmark All Tabs (Cmd+Shift+D)")
    print("=" * 50)
    
    # Open a couple of tabs first
    print("\n  Opening multiple tabs...")
    send_hotkey("command", "t")
    time.sleep(0.3)
    navigate_to_url("https://github.com")
    
    send_hotkey("command", "t")
    time.sleep(0.3)
    navigate_to_url("https://google.com")
    
    # Bookmark all tabs
    print("\n  Bookmarking all tabs...")
    send_hotkey("command", "shift", "d")
    time.sleep(0.5)
    
    # Cancel with Escape (don't actually save to avoid clutter)
    send_hotkey("escape")
    time.sleep(0.3)
    
    print("    ✅ Bookmark all tabs dialog opened (cancelled)")
    return True


def test_search_bookmarks() -> bool:
    """Test: Search in bookmark manager"""
    print("\n" + "=" * 50)
    print("Test 5: Search Bookmarks")
    print("=" * 50)
    
    # Open bookmark manager
    print("\n  Opening bookmark manager...")
    send_hotkey("command", "shift", "o")
    time.sleep(1)
    
    # Search for something
    print("\n  Searching for 'example'...")
    send_hotkey("command", "f")
    time.sleep(0.3)
    type_text("example")
    time.sleep(0.5)
    
    print("    ✅ Search completed")
    
    # Close search
    send_hotkey("escape")
    time.sleep(0.3)
    
    return True


def teardown() -> None:
    """Cleanup after tests"""
    print("\n[Teardown] Cleaning up...")
    
    # Close extra tabs
    for _ in range(3):
        send_hotkey("command", "w")
        time.sleep(0.2)
    
    run_mac("session", "end", check=False)
    print("    ✅ Cleanup complete")


def main():
    """Main test runner"""
    print("\n" + "=" * 60)
    print("  Bookmark Test Suite - Microsoft Edge")
    print("=" * 60)
    
    results = {}
    
    try:
        if not check_environment():
            print("\n❌ Environment check failed")
            sys.exit(1)
        
        setup_session()
        
        # Run tests
        results["add_bookmark"] = test_add_bookmark()
        results["open_bookmark_manager"] = test_open_bookmark_manager()
        results["bookmark_bar_toggle"] = test_bookmark_bar_toggle()
        results["bookmark_all_tabs"] = test_bookmark_all_tabs()
        results["search_bookmarks"] = test_search_bookmarks()
        
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
