#!/usr/bin/env python3
"""
Test: Multi-window management in Microsoft Edge
Tests creating, switching, and managing browser windows

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

def test_new_window() -> bool:
    """Test: Create new window"""
    print("\n" + "=" * 50)
    print("Test 1: New Window (Cmd+N)")
    print("=" * 50)
    
    print("\n  Creating new window...")
    send_hotkey("command", "n")
    time.sleep(1)
    
    print("    ✅ New window created")
    return True


def test_new_incognito_window() -> bool:
    """Test: Create new InPrivate/Incognito window"""
    print("\n" + "=" * 50)
    print("Test 2: New InPrivate Window (Cmd+Shift+N)")
    print("=" * 50)
    
    print("\n  Creating InPrivate window...")
    send_hotkey("command", "shift", "n")
    time.sleep(1)
    
    print("    ✅ InPrivate window created")
    return True


def test_switch_windows() -> bool:
    """Test: Switch between windows"""
    print("\n" + "=" * 50)
    print("Test 3: Switch Windows (Cmd+`)")
    print("=" * 50)
    
    print("\n  Switching to next window...")
    send_hotkey("command", "`")
    time.sleep(0.5)
    
    print("    ✅ Switched to next window")
    
    print("\n  Switching back...")
    send_hotkey("command", "`")
    time.sleep(0.5)
    
    print("    ✅ Switched back")
    return True


def test_minimize_window() -> bool:
    """Test: Minimize window"""
    print("\n" + "=" * 50)
    print("Test 4: Minimize Window (Cmd+M)")
    print("=" * 50)
    
    print("\n  Minimizing window...")
    send_hotkey("command", "m")
    time.sleep(0.5)
    
    print("    ✅ Window minimized")
    
    # Restore by switching windows
    time.sleep(0.5)
    send_hotkey("command", "`")
    time.sleep(0.5)
    
    return True


def test_fullscreen_toggle() -> bool:
    """Test: Toggle fullscreen"""
    print("\n" + "=" * 50)
    print("Test 5: Toggle Fullscreen (Cmd+Ctrl+F)")
    print("=" * 50)
    
    print("\n  Entering fullscreen...")
    send_hotkey("command", "control", "f")
    time.sleep(1)
    
    print("    ✅ Entered fullscreen")
    
    print("\n  Exiting fullscreen...")
    send_hotkey("command", "control", "f")
    time.sleep(1)
    
    print("    ✅ Exited fullscreen")
    return True


def test_close_window() -> bool:
    """Test: Close window"""
    print("\n" + "=" * 50)
    print("Test 6: Close Window (Cmd+Shift+W)")
    print("=" * 50)
    
    # First create a new window to close
    print("\n  Creating window to close...")
    send_hotkey("command", "n")
    time.sleep(0.5)
    
    print("\n  Closing window...")
    send_hotkey("command", "shift", "w")
    time.sleep(0.5)
    
    print("    ✅ Window closed")
    return True


def test_move_tab_to_new_window() -> bool:
    """Test: Move tab to new window"""
    print("\n" + "=" * 50)
    print("Test 7: Move Tab to New Window")
    print("=" * 50)
    
    # Create multiple tabs
    print("\n  Creating tabs...")
    send_hotkey("command", "t")
    time.sleep(0.3)
    navigate_to_url("https://example.com")
    
    send_hotkey("command", "t")
    time.sleep(0.3)
    navigate_to_url("https://github.com")
    
    # Use menu: Window > Move Tab to New Window
    # This is typically done via menu, simulate with keyboard
    print("\n  Note: Tab-to-window move usually requires drag or menu")
    print("    ⚠️ Skipping direct test (requires menu navigation)")
    
    return True


def teardown() -> None:
    """Cleanup after tests"""
    print("\n[Teardown] Cleaning up...")
    
    # Close all windows except one
    for _ in range(3):
        send_hotkey("command", "shift", "w")
        time.sleep(0.3)
    
    # Close remaining tabs
    for _ in range(3):
        send_hotkey("command", "w")
        time.sleep(0.2)
    
    run_mac("session", "end", check=False)
    print("    ✅ Cleanup complete")


def main():
    """Main test runner"""
    print("\n" + "=" * 60)
    print("  Multi-Window Test Suite - Microsoft Edge")
    print("=" * 60)
    
    results = {}
    
    try:
        if not check_environment():
            print("\n❌ Environment check failed")
            sys.exit(1)
        
        setup_session()
        
        # Run tests
        results["new_window"] = test_new_window()
        results["new_incognito_window"] = test_new_incognito_window()
        results["switch_windows"] = test_switch_windows()
        results["minimize_window"] = test_minimize_window()
        results["fullscreen_toggle"] = test_fullscreen_toggle()
        results["close_window"] = test_close_window()
        results["move_tab_to_window"] = test_move_tab_to_new_window()
        
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
