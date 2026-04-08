# FSQ Test Pilot - 环境配置指南

## 前置条件

- macOS 13+ (Ventura 或更高)
- Python 3.9+
- Node.js 18+
- Xcode Command Line Tools

## 快速开始

### 1. 安装依赖

```bash
# fsq-mac CLI
pipx install fsq-mac

# Appium
npm install -g appium

# Mac2 Driver
appium driver install mac2
```

### 2. Xcode 配置 (重要!)

```bash
# 安装 Xcode CLI Tools
xcode-select --install

# 完成首次启动设置 (需要 sudo)
sudo xcodebuild -runFirstLaunch

# 接受许可证
sudo xcodebuild -license accept
```

### 3. 系统权限

打开 **系统设置 → 隐私与安全性 → 辅助功能**，添加：
- Terminal.app (或你使用的终端)
- Appium

### 4. 启动 Appium

```bash
# 在单独的终端窗口运行
appium
```

### 5. 验证环境

```bash
# 使用环境检查脚本
python scripts/env_check.py

# 或使用 mac doctor
mac doctor
```

## 常见问题

### xcode_first_launch 失败

```
错误: Xcode first launch setup incomplete
```

**解决方案**:
```bash
sudo xcodebuild -runFirstLaunch
```

如果仍然失败，尝试：
```bash
# 重置 Xcode 设置
sudo xcode-select --reset

# 重新运行
sudo xcodebuild -runFirstLaunch
```

### Mac2 Driver 未安装

```
错误: Mac2 Driver not installed
```

**解决方案**:
```bash
appium driver install mac2
```

### Accessibility 权限问题

```
错误: Accessibility permission not granted
```

**解决方案**:
1. 打开 系统设置 → 隐私与安全性 → 辅助功能
2. 点击 + 添加你的终端应用
3. 重启终端

### Appium 服务未运行

```
错误: Appium server not running
```

**解决方案**:
```bash
# 启动 Appium (保持运行)
appium

# 或后台运行
nohup appium > /tmp/appium.log 2>&1 &
```

## 环境检查清单

运行 `python scripts/env_check.py` 应该显示：

```
✓ fsq-mac CLI: Installed
✓ Appium: Installed
✓ Mac2 Driver: Installed
✓ Appium Server: Running
✓ Accessibility Permission: Granted
✓ Xcode CLI Tools: Installed
✓ Xcode First Launch: Configured
✓ mac doctor: All checks passed

Summary: 8/8 checks passed
```

## 下一步

环境配置完成后，可以运行测试：

```bash
# 运行所有测试
python -m pytest tests/

# 运行单个测试
python tests/test_tab_new.py
```
