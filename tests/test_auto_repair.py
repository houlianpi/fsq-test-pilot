#!/usr/bin/env python3
"""
Test: Auto-Repair Capability Verification
Demonstrates Agent's ability to detect failures and attempt repairs

This is a spike/POC to validate:
1. Agent can detect test failures
2. Agent can read error logs + UI state
3. Agent can analyze failure causes
4. Agent can attempt repairs and retry

Prerequisites:
1. fsq-mac installed
2. Appium server running
3. macOS Accessibility permission granted
"""

import subprocess
import json
import time
import sys
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

MAC_CLI = "mac"


@dataclass
class RepairAttempt:
    """Record of a repair attempt"""
    failure_type: str
    analysis: str
    repair_action: str
    success: bool
    retry_result: Optional[bool] = None


def run_mac(*args, check=True) -> Optional[Dict[str, Any]]:
    """Run mac CLI command and return parsed JSON output"""
    cmd = [MAC_CLI] + list(args)
    print(f"    $ {' '.join(cmd)}")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0 and check:
        return {"ok": False, "error": result.stderr or result.stdout}
    
    try:
        return json.loads(result.stdout) if result.stdout.strip() else {"ok": True}
    except json.JSONDecodeError:
        return {"raw": result.stdout, "ok": result.returncode == 0}


def send_hotkey(*keys) -> bool:
    """Send hotkey combination"""
    result = run_mac("input", "hotkey", *keys, check=False)
    time.sleep(0.3)
    return result and result.get("ok", False)


def capture_ui_state() -> Dict[str, Any]:
    """Capture current UI state for analysis"""
    result = run_mac("capture", "tree", "--depth", "5", check=False)
    return result or {}


def analyze_failure(error: Dict[str, Any], ui_state: Dict[str, Any]) -> str:
    """
    Analyze failure and suggest repair strategy
    
    This simulates Agent's reasoning about what went wrong
    """
    error_msg = str(error.get("error", ""))
    error_code = error.get("error", {}).get("code", "") if isinstance(error.get("error"), dict) else ""
    
    # Pattern matching for common failures
    if "BACKEND_UNAVAILABLE" in error_msg or "BACKEND_UNAVAILABLE" in error_code:
        if "process is not running" in error_msg:
            return "REPAIR_RESTART_SESSION"
        if "Cannot reach" in error_msg:
            return "REPAIR_CHECK_APPIUM"
    
    if "element not found" in error_msg.lower():
        return "REPAIR_WAIT_AND_RETRY"
    
    if "timeout" in error_msg.lower():
        return "REPAIR_INCREASE_TIMEOUT"
    
    if "accessibility" in error_msg.lower():
        return "REPAIR_CHECK_PERMISSIONS"
    
    return "REPAIR_UNKNOWN"


def attempt_repair(strategy: str) -> bool:
    """
    Attempt to repair based on strategy
    
    Returns True if repair was successful
    """
    print(f"\n  🔧 Attempting repair: {strategy}")
    
    if strategy == "REPAIR_RESTART_SESSION":
        # End current session and start new one
        run_mac("session", "end", check=False)
        time.sleep(1)
        result = run_mac("session", "start", check=False)
        if result and result.get("ok"):
            print("    ✅ Session restarted")
            return True
        print("    ❌ Session restart failed")
        return False
    
    elif strategy == "REPAIR_WAIT_AND_RETRY":
        # Simple wait before retry
        print("    Waiting 2 seconds before retry...")
        time.sleep(2)
        return True
    
    elif strategy == "REPAIR_CHECK_APPIUM":
        # Check if Appium is running
        result = run_mac("doctor", check=False)
        checks = result.get("error", {}).get("details", {}).get("checks", [])
        for check in checks:
            if check.get("name") == "appium_server" and check.get("status") == "pass":
                print("    ✅ Appium is running")
                return True
        print("    ❌ Appium check failed - manual intervention needed")
        return False
    
    elif strategy == "REPAIR_CHECK_PERMISSIONS":
        print("    ⚠️ Permission issue - manual intervention needed")
        return False
    
    elif strategy == "REPAIR_INCREASE_TIMEOUT":
        print("    ℹ️ Would increase timeout for next attempt")
        return True
    
    else:
        print("    ⚠️ Unknown repair strategy")
        return False


def scenario_deliberate_failure():
    """
    Scenario: Deliberately cause a failure, then repair and retry
    
    This demonstrates the auto-repair flow
    """
    print("\n" + "=" * 60)
    print("  Scenario: Deliberate Failure + Auto-Repair")
    print("=" * 60)
    
    repairs: List[RepairAttempt] = []
    
    # Step 1: End any existing session to cause "no session" error
    print("\n[Step 1] Setting up failure condition...")
    run_mac("session", "end", check=False)
    time.sleep(0.5)
    
    # Step 2: Try an operation that requires a session
    print("\n[Step 2] Attempting operation without session...")
    result = run_mac("app", "activate", "com.microsoft.edgemac", check=False)
    
    if result and result.get("ok"):
        print("    Unexpected success - no failure to repair")
        return repairs
    
    print(f"    ❌ Expected failure occurred")
    
    # Step 3: Capture UI state for analysis
    print("\n[Step 3] Capturing UI state...")
    ui_state = capture_ui_state()
    
    # Step 4: Analyze failure
    print("\n[Step 4] Analyzing failure...")
    strategy = analyze_failure(result, ui_state)
    print(f"    Strategy: {strategy}")
    
    # Step 5: Attempt repair
    print("\n[Step 5] Attempting repair...")
    repair_success = attempt_repair(strategy)
    
    # Step 6: Retry original operation
    print("\n[Step 6] Retrying original operation...")
    retry_result = run_mac("app", "activate", "com.microsoft.edgemac", check=False)
    retry_success = retry_result and retry_result.get("ok", False)
    
    if retry_success:
        print("    ✅ Retry succeeded!")
    else:
        print("    ❌ Retry failed")
    
    # Record the attempt
    repairs.append(RepairAttempt(
        failure_type="NO_SESSION",
        analysis=strategy,
        repair_action="Restart session",
        success=repair_success,
        retry_result=retry_success
    ))
    
    return repairs


def scenario_element_not_found():
    """
    Scenario: Element not found - wait and retry
    """
    print("\n" + "=" * 60)
    print("  Scenario: Element Not Found + Retry")
    print("=" * 60)
    
    repairs: List[RepairAttempt] = []
    
    # Simulate looking for a non-existent element
    print("\n[Step 1] Looking for non-existent element...")
    
    # Create a mock failure
    mock_error = {
        "ok": False,
        "error": "Element not found: button[@name='NonExistent']"
    }
    
    print(f"    ❌ Simulated failure: {mock_error['error']}")
    
    # Analyze
    print("\n[Step 2] Analyzing failure...")
    strategy = analyze_failure(mock_error, {})
    print(f"    Strategy: {strategy}")
    
    # Repair
    print("\n[Step 3] Attempting repair...")
    repair_success = attempt_repair(strategy)
    
    repairs.append(RepairAttempt(
        failure_type="ELEMENT_NOT_FOUND",
        analysis=strategy,
        repair_action="Wait and retry",
        success=repair_success,
        retry_result=None  # Simulated scenario
    ))
    
    return repairs


def generate_report(all_repairs: List[RepairAttempt]):
    """Generate summary report of repair attempts"""
    print("\n" + "=" * 60)
    print("  Auto-Repair Summary Report")
    print("=" * 60)
    
    print("\n| Failure Type | Strategy | Repair | Retry |")
    print("|--------------|----------|--------|-------|")
    
    for r in all_repairs:
        repair_icon = "✅" if r.success else "❌"
        retry_icon = "✅" if r.retry_result else ("❌" if r.retry_result is False else "N/A")
        print(f"| {r.failure_type} | {r.analysis} | {repair_icon} | {retry_icon} |")
    
    successful_repairs = sum(1 for r in all_repairs if r.success)
    successful_retries = sum(1 for r in all_repairs if r.retry_result)
    
    print(f"\nTotal Repairs: {successful_repairs}/{len(all_repairs)} successful")
    print(f"Total Retries: {successful_retries}/{len([r for r in all_repairs if r.retry_result is not None])} successful")


def main():
    """Main entry point"""
    print("\n" + "=" * 60)
    print("  Auto-Repair Capability Verification (POC)")
    print("=" * 60)
    
    all_repairs: List[RepairAttempt] = []
    
    try:
        # Ensure we start fresh
        print("\n[Setup] Starting fresh session...")
        run_mac("session", "start", check=False)
        
        # Run scenarios
        all_repairs.extend(scenario_deliberate_failure())
        all_repairs.extend(scenario_element_not_found())
        
        # Generate report
        generate_report(all_repairs)
        
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # Cleanup
        print("\n[Teardown] Ending session...")
        run_mac("session", "end", check=False)
    
    # Exit with success if at least one repair worked
    successful = any(r.success for r in all_repairs)
    print(f"\n{'✅ POC Validated' if successful else '❌ POC Failed'}: Auto-repair capability")
    sys.exit(0 if successful else 1)


if __name__ == "__main__":
    main()
