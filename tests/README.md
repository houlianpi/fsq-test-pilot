# Test Scripts

This directory contains test scripts for the AI-Native Testing POC.

## Prerequisites

1. **fsq-mac CLI** installed (`mac --version`)
2. **Appium server** running (`appium`)
3. **macOS Accessibility** permission granted
4. **Microsoft Edge** installed

## Running Tests

### Start Appium Server (in a separate terminal)

```bash
appium
```

### Run Tab Test

```bash
# From project root
python3 tests/test_tab_new.py
```

## Test Scripts

| File | Description |
|------|-------------|
| `test_tab_new.py` | Create a new tab in Edge |

## Expected Output

```
==================================================
Test: Create New Tab in Microsoft Edge
==================================================

[1/5] Checking environment...
  ✅ Environment OK

[2/5] Starting session...
  ✅ Session started: abc123

[3/5] Launching Microsoft Edge...
  ✅ Edge launched

[4/5] Creating new tab...
  ✅ Cmd+T sent

[5/5] Verifying new tab...
  ✅ UI tree captured

==================================================
✅ Test Passed: New tab created successfully!
==================================================
```

## Troubleshooting

### `mac doctor` fails

1. Check Appium is running: `lsof -i :4723`
2. Check Accessibility permission in System Settings
3. Restart terminal after granting permission

### Edge doesn't launch

1. Make sure Edge is installed
2. Try launching manually first
3. Check bundle ID: `osascript -e 'id of app "Microsoft Edge"'`
