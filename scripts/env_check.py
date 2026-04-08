#!/usr/bin/env python3
"""
Environment Check & Auto-Fix Script
Checks and repairs common environment issues for fsq-mac + Appium Mac2

Usage:
    python scripts/env_check.py          # Check only
    python scripts/env_check.py --fix    # Check and auto-fix
"""

import subprocess
import json
import sys
import os
import shutil
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, List, Tuple

# ANSI colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


@dataclass
class CheckResult:
    name: str
    passed: bool
    message: str
    fixable: bool = False
    fix_command: Optional[str] = None


def run_cmd(cmd: List[str], timeout: int = 30) -> Tuple[int, str, str]:
    """Run command and return (returncode, stdout, stderr)"""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except FileNotFoundError:
        return -1, "", f"Command not found: {cmd[0]}"


def check_mac_cli() -> CheckResult:
    """Check if fsq-mac CLI is installed"""
    code, out, err = run_cmd(["mac", "--version"])
    if code == 0:
        version = out.strip()
        return CheckResult("fsq-mac CLI", True, f"Installed: {version}")
    return CheckResult(
        "fsq-mac CLI", False, "Not installed",
        fixable=True, fix_command="pipx install fsq-mac"
    )


def check_appium() -> CheckResult:
    """Check if Appium is installed"""
    code, out, err = run_cmd(["appium", "--version"])
    if code == 0:
        version = out.strip()
        return CheckResult("Appium", True, f"Installed: {version}")
    return CheckResult(
        "Appium", False, "Not installed",
        fixable=True, fix_command="npm install -g appium"
    )


def check_mac2_driver() -> CheckResult:
    """Check if Mac2 driver is installed"""
    code, out, err = run_cmd(["appium", "driver", "list", "--installed"])
    if code == 0 and "mac2" in out.lower():
        return CheckResult("Mac2 Driver", True, "Installed")
    return CheckResult(
        "Mac2 Driver", False, "Not installed",
        fixable=True, fix_command="appium driver install mac2"
    )


def check_appium_server() -> CheckResult:
    """Check if Appium server is running"""
    code, out, err = run_cmd(["curl", "-s", "http://127.0.0.1:4723/status"])
    if code == 0:
        try:
            data = json.loads(out)
            if data.get("value", {}).get("ready"):
                return CheckResult("Appium Server", True, "Running on :4723")
        except json.JSONDecodeError:
            pass
    return CheckResult(
        "Appium Server", False, "Not running",
        fixable=False, fix_command="appium (run in separate terminal)"
    )


def check_accessibility() -> CheckResult:
    """Check Accessibility permission"""
    # Try a simple AppleScript that requires accessibility
    script = 'tell application "System Events" to get name of first process'
    code, out, err = run_cmd(["osascript", "-e", script], timeout=5)
    if code == 0:
        return CheckResult("Accessibility Permission", True, "Granted")
    return CheckResult(
        "Accessibility Permission", False,
        "Not granted - add Terminal to Accessibility in System Settings",
        fixable=False
    )


def check_xcode_cli() -> CheckResult:
    """Check Xcode Command Line Tools"""
    code, out, err = run_cmd(["xcode-select", "-p"])
    if code == 0:
        return CheckResult("Xcode CLI Tools", True, f"Path: {out.strip()}")
    return CheckResult(
        "Xcode CLI Tools", False, "Not installed",
        fixable=True, fix_command="xcode-select --install"
    )


def check_xcode_first_launch() -> CheckResult:
    """Check Xcode first launch setup"""
    # Check if license is accepted
    code, out, err = run_cmd(["xcrun", "simctl", "help"], timeout=10)
    if code == 0:
        return CheckResult("Xcode First Launch", True, "Configured")
    return CheckResult(
        "Xcode First Launch", False,
        "Run: sudo xcodebuild -runFirstLaunch",
        fixable=False  # Requires sudo
    )


def check_mac_doctor() -> CheckResult:
    """Run mac doctor for comprehensive check"""
    code, out, err = run_cmd(["mac", "doctor"])
    if code == 0:
        try:
            data = json.loads(out)
            if data.get("ok"):
                return CheckResult("mac doctor", True, "All checks passed")
        except json.JSONDecodeError:
            pass
    
    # Parse individual checks
    try:
        data = json.loads(out)
        checks = data.get("error", {}).get("details", {}).get("checks", [])
        failed = [c["name"] for c in checks if c.get("status") != "pass"]
        if failed:
            return CheckResult(
                "mac doctor", False,
                f"Failed: {', '.join(failed)}"
            )
    except (json.JSONDecodeError, KeyError):
        pass
    
    return CheckResult("mac doctor", False, "Check failed")


def run_fix(fix_command: str) -> bool:
    """Run a fix command"""
    print(f"  {BLUE}Running: {fix_command}{RESET}")
    code, out, err = run_cmd(fix_command.split())
    if code == 0:
        print(f"  {GREEN}✓ Fix successful{RESET}")
        return True
    print(f"  {RED}✗ Fix failed: {err or out}{RESET}")
    return False


def main():
    auto_fix = "--fix" in sys.argv
    
    print(f"\n{'='*60}")
    print("  FSQ Test Pilot - Environment Check")
    print(f"{'='*60}\n")
    
    checks = [
        check_mac_cli,
        check_appium,
        check_mac2_driver,
        check_appium_server,
        check_accessibility,
        check_xcode_cli,
        check_xcode_first_launch,
        check_mac_doctor,
    ]
    
    results: List[CheckResult] = []
    
    for check_func in checks:
        result = check_func()
        results.append(result)
        
        status = f"{GREEN}✓{RESET}" if result.passed else f"{RED}✗{RESET}"
        print(f"  {status} {result.name}: {result.message}")
        
        # Auto-fix if enabled and fixable
        if not result.passed and auto_fix and result.fixable and result.fix_command:
            run_fix(result.fix_command)
    
    # Summary
    passed = sum(1 for r in results if r.passed)
    total = len(results)
    
    print(f"\n{'='*60}")
    print(f"  Summary: {passed}/{total} checks passed")
    print(f"{'='*60}")
    
    # Show fix suggestions
    fixable = [r for r in results if not r.passed and r.fix_command]
    if fixable and not auto_fix:
        print(f"\n  {YELLOW}Fixable issues:{RESET}")
        for r in fixable:
            prefix = "[auto]" if r.fixable else "[manual]"
            print(f"    {prefix} {r.name}: {r.fix_command}")
        print(f"\n  Run with --fix to auto-fix where possible")
    
    # Exit code
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
