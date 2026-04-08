#!/usr/bin/env python3
"""
Mac2 Driver Crash Recovery Module
Detects driver crashes and automatically recovers

Usage:
    from scripts.crash_recovery import with_recovery, CrashRecovery
    
    @with_recovery(max_retries=3)
    def my_test():
        # test code
        pass
"""

import subprocess
import json
import time
import functools
import logging
from dataclasses import dataclass, field
from typing import Callable, Optional, Any, List
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("crash_recovery")


class CrashType(Enum):
    """Types of crashes we can detect"""
    DRIVER_NOT_RUNNING = "driver_not_running"
    SESSION_LOST = "session_lost"
    APPIUM_UNREACHABLE = "appium_unreachable"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"


@dataclass
class CrashEvent:
    """Record of a crash event"""
    crash_type: CrashType
    error_message: str
    timestamp: float = field(default_factory=time.time)
    recovered: bool = False
    recovery_time_ms: float = 0


@dataclass
class RecoveryConfig:
    """Configuration for crash recovery"""
    max_retries: int = 3
    retry_delay_seconds: float = 2.0
    backoff_multiplier: float = 1.5
    restart_appium: bool = False
    appium_start_wait: float = 5.0


class CrashRecovery:
    """Handles Mac2 Driver crash detection and recovery"""
    
    def __init__(self, config: Optional[RecoveryConfig] = None):
        self.config = config or RecoveryConfig()
        self.crash_history: List[CrashEvent] = []
        self._session_active = False
    
    def detect_crash(self, error: str) -> CrashType:
        """Detect crash type from error message"""
        error_lower = error.lower()
        
        if "cannot be proxied to mac2 driver" in error_lower:
            return CrashType.DRIVER_NOT_RUNNING
        if "process is not running" in error_lower:
            return CrashType.DRIVER_NOT_RUNNING
        if "no session" in error_lower or "session not found" in error_lower:
            return CrashType.SESSION_LOST
        if "econnrefused" in error_lower or "connection refused" in error_lower:
            return CrashType.APPIUM_UNREACHABLE
        if "timeout" in error_lower:
            return CrashType.TIMEOUT
        
        return CrashType.UNKNOWN
    
    def check_appium_status(self) -> bool:
        """Check if Appium server is running"""
        try:
            result = subprocess.run(
                ["curl", "-s", "http://127.0.0.1:4723/status"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return data.get("value", {}).get("ready", False)
        except Exception:
            pass
        return False
    
    def restart_session(self) -> bool:
        """Restart the Mac2 session"""
        logger.info("Attempting to restart session...")
        
        # End existing session
        try:
            subprocess.run(
                ["mac", "session", "end"],
                capture_output=True, timeout=10
            )
        except Exception:
            pass
        
        time.sleep(1)
        
        # Start new session
        try:
            result = subprocess.run(
                ["mac", "session", "start"],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                logger.info("Session restarted successfully")
                self._session_active = True
                return True
        except Exception as e:
            logger.error(f"Failed to restart session: {e}")
        
        return False
    
    def restart_appium(self) -> bool:
        """Attempt to restart Appium server"""
        if not self.config.restart_appium:
            logger.warning("Appium restart disabled in config")
            return False
        
        logger.info("Attempting to restart Appium...")
        
        # Kill existing Appium
        subprocess.run(["pkill", "-f", "appium"], capture_output=True)
        time.sleep(2)
        
        # Start Appium in background
        subprocess.Popen(
            ["appium"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        # Wait for Appium to be ready
        wait_time = self.config.appium_start_wait
        while wait_time > 0:
            if self.check_appium_status():
                logger.info("Appium restarted successfully")
                return True
            time.sleep(1)
            wait_time -= 1
        
        logger.error("Appium failed to start")
        return False
    
    def recover(self, crash_type: CrashType, error: str) -> bool:
        """Attempt to recover from a crash"""
        start_time = time.time()
        event = CrashEvent(crash_type=crash_type, error_message=error)
        
        logger.info(f"Attempting recovery from {crash_type.value}...")
        
        success = False
        
        if crash_type == CrashType.DRIVER_NOT_RUNNING:
            # Try restarting session first
            success = self.restart_session()
            if not success and self.config.restart_appium:
                success = self.restart_appium() and self.restart_session()
        
        elif crash_type == CrashType.SESSION_LOST:
            success = self.restart_session()
        
        elif crash_type == CrashType.APPIUM_UNREACHABLE:
            if self.check_appium_status():
                success = self.restart_session()
            elif self.config.restart_appium:
                success = self.restart_appium() and self.restart_session()
        
        elif crash_type == CrashType.TIMEOUT:
            # Simple retry after delay
            time.sleep(self.config.retry_delay_seconds)
            success = True
        
        else:
            # Unknown - try session restart
            success = self.restart_session()
        
        event.recovered = success
        event.recovery_time_ms = (time.time() - start_time) * 1000
        self.crash_history.append(event)
        
        if success:
            logger.info(f"Recovery successful ({event.recovery_time_ms:.0f}ms)")
        else:
            logger.error("Recovery failed")
        
        return success
    
    def get_stats(self) -> dict:
        """Get crash recovery statistics"""
        if not self.crash_history:
            return {"total_crashes": 0, "recovery_rate": 1.0}
        
        total = len(self.crash_history)
        recovered = sum(1 for e in self.crash_history if e.recovered)
        avg_time = sum(e.recovery_time_ms for e in self.crash_history) / total
        
        by_type = {}
        for event in self.crash_history:
            t = event.crash_type.value
            if t not in by_type:
                by_type[t] = {"count": 0, "recovered": 0}
            by_type[t]["count"] += 1
            if event.recovered:
                by_type[t]["recovered"] += 1
        
        return {
            "total_crashes": total,
            "total_recovered": recovered,
            "recovery_rate": recovered / total if total > 0 else 1.0,
            "avg_recovery_time_ms": avg_time,
            "by_type": by_type
        }


def with_recovery(
    max_retries: int = 3,
    retry_delay: float = 2.0,
    config: Optional[RecoveryConfig] = None
):
    """
    Decorator to add crash recovery to a function
    
    Usage:
        @with_recovery(max_retries=3)
        def test_something():
            # test code that might crash
            pass
    """
    if config is None:
        config = RecoveryConfig(
            max_retries=max_retries,
            retry_delay_seconds=retry_delay
        )
    
    recovery = CrashRecovery(config)
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_error = None
            delay = config.retry_delay_seconds
            
            for attempt in range(config.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    error_str = str(e)
                    crash_type = recovery.detect_crash(error_str)
                    
                    logger.warning(
                        f"Attempt {attempt + 1}/{config.max_retries + 1} failed: "
                        f"{crash_type.value}"
                    )
                    
                    if attempt < config.max_retries:
                        if recovery.recover(crash_type, error_str):
                            time.sleep(delay)
                            delay *= config.backoff_multiplier
                            continue
                    
                    break
            
            # Log final stats
            stats = recovery.get_stats()
            logger.info(f"Recovery stats: {stats}")
            
            raise last_error
        
        # Attach recovery instance for inspection
        wrapper._recovery = recovery
        return wrapper
    
    return decorator


# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("  Mac2 Driver Crash Recovery Module")
    print("=" * 60)
    
    recovery = CrashRecovery()
    
    # Test crash detection
    test_errors = [
        "'GET /status' cannot be proxied to Mac2 Driver server because its process is not running",
        "No session found",
        "ECONNREFUSED - connection refused",
        "Operation timed out",
        "Some unknown error",
    ]
    
    print("\nCrash type detection:")
    for error in test_errors:
        crash_type = recovery.detect_crash(error)
        print(f"  {crash_type.value}: {error[:50]}...")
    
    # Check current Appium status
    print(f"\nAppium status: {'Running' if recovery.check_appium_status() else 'Not running'}")
    
    print("\n" + "=" * 60)
    print("  Usage Example")
    print("=" * 60)
    print("""
    from scripts.crash_recovery import with_recovery
    
    @with_recovery(max_retries=3)
    def test_tab_creation():
        run_mac("input", "hotkey", "command", "t")
        # ... rest of test
    """)
