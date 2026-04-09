#!/bin/bash
# FSQ Test Pilot - 一键环境检查脚本
# Usage: ./scripts/check-env.sh

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASS=0
FAIL=0

check() {
    if eval "$2" > /dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} $1"
        ((PASS++))
    else
        echo -e "  ${RED}✗${NC} $1"
        ((FAIL++))
    fi
}

echo ""
echo "=============================================="
echo "  FSQ Test Pilot - 环境检查"
echo "=============================================="

echo -e "\n[基础依赖]"
check "Python 3" "python3 --version"
check "Node.js" "node --version"

echo -e "\n[fsq-mac]"
check "fsq-mac CLI" "mac --version"

echo -e "\n[Appium]"
check "Appium" "appium --version"
check "Mac2 Driver" "appium driver list --installed 2>&1 | grep -qi mac2"
check "Appium Server" "curl -s http://127.0.0.1:4723/status | grep -q ready"

echo -e "\n[Xcode]"
check "Xcode CLI Tools" "xcode-select -p"
check "Xcode First Launch" "xcrun simctl help"

echo -e "\n[权限]"
check "Accessibility" "osascript -e 'tell app \"System Events\" to get name of first process'"

TOTAL=$((PASS + FAIL))
echo -e "\n=============================================="
echo "  结果: $PASS/$TOTAL 通过"
echo "=============================================="

if [ $FAIL -gt 0 ]; then
    echo -e "\n${YELLOW}修复建议:${NC}"
    mac --version > /dev/null 2>&1 || echo "  • fsq-mac: pipx install fsq-mac"
    appium --version > /dev/null 2>&1 || echo "  • Appium: npm install -g appium"
    appium driver list --installed 2>&1 | grep -qi mac2 || echo "  • Mac2 Driver: appium driver install mac2"
    curl -s http://127.0.0.1:4723/status | grep -q ready 2>/dev/null || echo "  • Appium Server: 运行 appium"
    xcrun simctl help > /dev/null 2>&1 || echo "  • Xcode: sudo xcodebuild -runFirstLaunch"
    exit 1
fi

echo -e "\n${GREEN}环境就绪！${NC}\n"
