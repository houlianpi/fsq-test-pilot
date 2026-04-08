# Auto-Repair Strategy Documentation

## Overview

This document describes the auto-repair capability implemented for the fsq-test-pilot POC.

## Repair Flow

```
Test Execution
     │
     ▼
  Failure?
     │
   ┌─┴─┐
  No   Yes
   │    │
   ▼    ▼
 Done  Capture UI State
          │
          ▼
      Analyze Error
          │
          ▼
      Select Strategy
          │
          ▼
      Attempt Repair
          │
        ┌─┴─┐
      Fail  Success
        │     │
        ▼     ▼
      Report  Retry
              │
            ┌─┴─┐
          Fail  Success
            │     │
            ▼     ▼
          Report  Done
```

## Supported Repair Strategies

### 1. REPAIR_RESTART_SESSION
- **Trigger**: Backend unavailable, process crashed
- **Action**: End current session, start new session
- **Success Rate**: High (when Appium is healthy)

### 2. REPAIR_WAIT_AND_RETRY
- **Trigger**: Element not found (may be timing issue)
- **Action**: Wait 2 seconds, retry operation
- **Success Rate**: Medium (depends on actual cause)

### 3. REPAIR_CHECK_APPIUM
- **Trigger**: Cannot reach Appium server
- **Action**: Run doctor check, verify Appium status
- **Success Rate**: Low (usually needs manual restart)

### 4. REPAIR_CHECK_PERMISSIONS
- **Trigger**: Accessibility permission error
- **Action**: Alert user, cannot auto-repair
- **Success Rate**: N/A (requires manual intervention)

### 5. REPAIR_INCREASE_TIMEOUT
- **Trigger**: Timeout errors
- **Action**: Increase timeout for next attempt
- **Success Rate**: Medium

## Error Pattern Matching

| Error Pattern | Strategy |
|---------------|----------|
| `BACKEND_UNAVAILABLE` + `process is not running` | REPAIR_RESTART_SESSION |
| `BACKEND_UNAVAILABLE` + `Cannot reach` | REPAIR_CHECK_APPIUM |
| `element not found` | REPAIR_WAIT_AND_RETRY |
| `timeout` | REPAIR_INCREASE_TIMEOUT |
| `accessibility` | REPAIR_CHECK_PERMISSIONS |

## Limitations

1. **Cannot fix Appium crashes** - Requires manual restart
2. **Cannot grant permissions** - Requires user action
3. **Limited retry attempts** - Currently single retry only
4. **No learning** - Strategies are rule-based, not adaptive

## Future Improvements

1. **Retry with backoff** - Multiple retries with increasing delays
2. **Context-aware repair** - Use UI state to inform repair decisions
3. **Repair history** - Track which repairs work in which contexts
4. **Self-healing scripts** - Generate repair code for common failures
