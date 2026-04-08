#!/usr/bin/env python3
"""
Test: Tab Management in Microsoft Edge
Complete test for: create, switch, close tabs

Prerequisites:
1. fsq-mac installed: pipx install fsq-mac
2. Appium server running: appium
3. macOS Accessibility permission granted
"""

import subprocess
import json
import time
import sys

MAC_CLI = "mac"
EDGE_BUNDLE_ID = "com.microsoft.edgemac"


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
    # Try osascript first (more reliable)
    subprocess.run(
        ["osascript", "-e", f'tell application "Microsoft Edge" to activate'],
        capture_output=True
    )
    time.sleep(1)
    return True


def send_hotkey(*keys):
    """Send hotkey combination"""
    result = run_mac("input", "hotkey", *keys, check=False)
    time.sleep(0.3)
    return result and result.get("ok")


def test_create_multiple_tabs():
    """Test 1: Create multiple tabs"""
    print("\n" + "=" * 50)
    print("Test 1: Create Multiple Tabs")
    print("=" * 50)
    
    tabs_to_create = 3
    created = 0
    
    for i in range(tabs_to_create):
        print(f"\n  Creating tab {i + 1}/{tabs_to_create}...")
        if send_hotkey("command", "t"):
            created += 1
            print(f"    ✅ Tab {i + 1} created")
        else:
            print(f"    ❌ Failed to create tab {i + 1}")
    
    time.sleep(0.5)
    
    if created == tabs_to_create:
        print(f"\n  ✅ Test Passed: Created {created} tabs")
        return True
    else:
        print(f"\n  ❌ Test Failed: Only created {created}/{tabs_to_create} tabs")
        return False


def test_switch_tabs():
    """Test 2: Switch between tabs"""
    print("\n" + "=" * 50)
    print("Test 2: Switch Tabs")
    print("=" * 50)
    
    tests = [
        ("Next tab (Ctrl+Tab)", ["control", "tab"]),
        ("Previous tab (Ctrl+Shift+Tab)", ["control", "shift", "tab"]),
        ("Go to tab 1 (Cmd+1)", ["command", "1"]),
        ("Go to tab 2 (Cmd+2)", ["command", "2"]),
    ]
    
    passed = 0
    for name, keys in tests:
        print(f"\n  {name}...")
        if send_hotkey(*keys):
            print(f"    ✅ {name}")
            passed += 1
        else:
            print(f"    ❌ {name}")
    
    if passed == len(tests):
        print(f"\n  ✅ Test Passed: All {passed} switch operations succeeded")
        return True
    else:
        print(f"\n  ⚠️ Test Partial: {passed}/{len(tests)} switch operations succeeded")
        return passed > 0


def test_close_tab():
    """Test 3: Close a tab"""
    print("\n" + "=" * 50)
    print("Test 3: Close Tab")
    print("=" * 50)
    
    print("\n  Closing current tab (Cmd+W)...")
    if send_hotkey("command", "w"):
        print("    ✅ Tab closed")
        return True
    else:
        print("    ❌ Failed to close tab")
        return False


def test_close_all_tabs():
    """Test 4: Close all tabs"""
    print("\n" + "=" * 50)
    print("Test 4: Close All Tabs (cleanup)")
    print("=" * 50)
    
    # Close remaining tabs (we created 3, closed 1, so ~2 left + original)
    # Use Cmd+Shift+W to close window or close tabs one by one
    
    print("\n  Closing remaining tabs...")
    for i in range(5):  # Close up to 5 tabs to be safe
        if not send_hotkey("command", "w"):
            break
        print(f"    Closed tab {i + 1}")
    
    print("\n  ✅ Cleanup complete")
    return True


def teardown():
    """Cleanup: end session"""
    print("\n[Teardown] Ending session...")
    run_mac("session", "end", check=False)
    print("    ✅ Session ended")


def main():
    """Main test runner"""
    print("\n" + "=" * 60)
    print("  Tab Management Test Suite - Microsoft Edge")
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
        
        # Run tests
        results["create_multiple_tabs"] = test_create_multiple_tabs()
        results["switch_tabs"] = test_switch_tabs()
        results["close_tab"] = test_close_tab()
        results["close_all_tabs"] = test_close_all_tabs()
        
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Tests failed with error: {e}")
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
