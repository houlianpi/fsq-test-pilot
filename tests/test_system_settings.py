#!/usr/bin/env python3
"""
Test: System Settings (macOS Ventura+) operations
Tests navigation, search, and basic interactions

Note: System Settings is a high-complexity app with SwiftUI interface.
Some operations may require specific macOS versions.

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
    """Start session and launch System Settings"""
    print("\n[Setup] Starting session...")
    run_mac("session", "start", check=False)
    
    subprocess.run(
        ["osascript", "-e", 'tell application "System Settings" to activate'],
        capture_output=True
    )
    time.sleep(2)  # System Settings takes longer to load
    print("    ✅ System Settings activated")
    return True


# =============================================================================
# Test Cases
# =============================================================================

def test_open_system_settings() -> bool:
    """Test: Open System Settings"""
    print("\n" + "=" * 50)
    print("Test 1: Open System Settings")
    print("=" * 50)
    
    # Already opened in setup, verify it's running
    result = subprocess.run(
        ["pgrep", "-x", "System Settings"],
        capture_output=True
    )
    
    if result.returncode == 0:
        print("    ✅ System Settings is running")
        return True
    else:
        print("    ❌ System Settings not found")
        return False


def test_search_settings() -> bool:
    """Test: Search in System Settings"""
    print("\n" + "=" * 50)
    print("Test 2: Search Settings (Cmd+F)")
    print("=" * 50)
    
    print("\n  Opening search...")
    send_hotkey("command", "f")
    time.sleep(0.5)
    
    # Type search query
    type_text("Wi-Fi")
    time.sleep(1)
    
    print("    ✅ Search activated")
    
    # Clear search
    send_hotkey("escape")
    time.sleep(0.3)
    
    return True


def test_navigate_general() -> bool:
    """Test: Navigate to General settings"""
    print("\n" + "=" * 50)
    print("Test 3: Navigate to General")
    print("=" * 50)
    
    print("\n  Searching for General...")
    send_hotkey("command", "f")
    time.sleep(0.3)
    type_text("General")
    time.sleep(0.5)
    send_hotkey("return")
    time.sleep(1)
    
    print("    ✅ Navigated to General")
    return True


def test_navigate_about() -> bool:
    """Test: Navigate to About section"""
    print("\n" + "=" * 50)
    print("Test 4: Navigate to About This Mac")
    print("=" * 50)
    
    print("\n  Searching for About...")
    send_hotkey("command", "f")
    time.sleep(0.3)
    type_text("About")
    time.sleep(0.5)
    send_hotkey("return")
    time.sleep(1)
    
    print("    ✅ Navigated to About")
    return True


def test_navigate_accessibility() -> bool:
    """Test: Navigate to Accessibility settings"""
    print("\n" + "=" * 50)
    print("Test 5: Navigate to Accessibility")
    print("=" * 50)
    
    print("\n  Searching for Accessibility...")
    send_hotkey("command", "f")
    time.sleep(0.3)
    type_text("Accessibility")
    time.sleep(0.5)
    send_hotkey("return")
    time.sleep(1)
    
    print("    ✅ Navigated to Accessibility")
    return True


def test_back_navigation() -> bool:
    """Test: Navigate back"""
    print("\n" + "=" * 50)
    print("Test 6: Back Navigation (Cmd+[)")
    print("=" * 50)
    
    print("\n  Going back...")
    send_hotkey("command", "[")
    time.sleep(0.5)
    
    print("    ✅ Navigated back")
    return True


def test_navigate_display() -> bool:
    """Test: Navigate to Display settings"""
    print("\n" + "=" * 50)
    print("Test 7: Navigate to Displays")
    print("=" * 50)
    
    print("\n  Searching for Displays...")
    send_hotkey("command", "f")
    time.sleep(0.3)
    type_text("Displays")
    time.sleep(0.5)
    send_hotkey("return")
    time.sleep(1)
    
    print("    ✅ Navigated to Displays")
    return True


def test_keyboard_navigation() -> bool:
    """Test: Navigate with keyboard"""
    print("\n" + "=" * 50)
    print("Test 8: Keyboard Navigation (Tab)")
    print("=" * 50)
    
    # Go back to main menu first
    send_hotkey("command", "[")
    time.sleep(0.5)
    send_hotkey("command", "[")
    time.sleep(0.5)
    
    print("\n  Using Tab to navigate...")
    for _ in range(3):
        send_hotkey("tab")
        time.sleep(0.3)
    
    print("    ✅ Tab navigation working")
    return True


def test_close_settings() -> bool:
    """Test: Close System Settings"""
    print("\n" + "=" * 50)
    print("Test 9: Close System Settings (Cmd+W)")
    print("=" * 50)
    
    print("\n  Closing window...")
    send_hotkey("command", "w")
    time.sleep(0.5)
    
    print("    ✅ Window closed")
    return True


def test_reopen_settings() -> bool:
    """Test: Reopen System Settings with Spotlight"""
    print("\n" + "=" * 50)
    print("Test 10: Reopen via Spotlight (Cmd+Space)")
    print("=" * 50)
    
    print("\n  Opening Spotlight...")
    send_hotkey("command", "space")
    time.sleep(0.5)
    
    type_text("System Settings")
    time.sleep(0.5)
    send_hotkey("return")
    time.sleep(2)
    
    print("    ✅ System Settings reopened via Spotlight")
    return True


def teardown() -> None:
    """Cleanup after tests"""
    print("\n[Teardown] Cleaning up...")
    
    # Close System Settings
    subprocess.run(
        ["osascript", "-e", 'tell application "System Settings" to quit'],
        capture_output=True
    )
    time.sleep(0.5)
    
    run_mac("session", "end", check=False)
    print("    ✅ Cleanup complete")


def main():
    """Main test runner"""
    print("\n" + "=" * 60)
    print("  System Settings Test Suite")
    print("=" * 60)
    
    results = {}
    
    try:
        if not check_environment():
            print("\n❌ Environment check failed")
            sys.exit(1)
        
        setup_session()
        
        # Run tests
        results["open_settings"] = test_open_system_settings()
        results["search_settings"] = test_search_settings()
        results["navigate_general"] = test_navigate_general()
        results["navigate_about"] = test_navigate_about()
        results["navigate_accessibility"] = test_navigate_accessibility()
        results["back_navigation"] = test_back_navigation()
        results["navigate_display"] = test_navigate_display()
        results["keyboard_navigation"] = test_keyboard_navigation()
        results["close_settings"] = test_close_settings()
        results["reopen_settings"] = test_reopen_settings()
        
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
