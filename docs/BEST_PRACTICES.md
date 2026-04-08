# Agent 测试最佳实践

本文档总结了使用 AI Agent + fsq-mac 进行 Mac 应用自动化测试的最佳实践。

## 目录

1. [环境配置](#环境配置)
2. [测试编写规范](#测试编写规范)
3. [自动修复策略](#自动修复策略)
4. [错误处理](#错误处理)
5. [常见问题 FAQ](#常见问题-faq)

---

## 环境配置

### 快速检查

```bash
# 一键检查环境
./scripts/check-env.sh

# 或使用 Python 版本（支持自动修复）
python scripts/env_check.py --fix
```

### 必需组件

| 组件 | 安装命令 | 验证命令 |
|------|----------|----------|
| fsq-mac | `pipx install fsq-mac` | `mac --version` |
| Appium | `npm install -g appium` | `appium --version` |
| Mac2 Driver | `appium driver install mac2` | `appium driver list` |

### 权限配置

1. **Accessibility 权限**
   - 系统设置 → 隐私与安全性 → 辅助功能
   - 添加 Terminal.app 和 Appium

2. **Xcode 首次启动**
   ```bash
   sudo xcodebuild -runFirstLaunch
   ```

---

## 测试编写规范

### 测试结构

```python
#!/usr/bin/env python3
"""
Test: [功能名称]
描述测试目的
"""

import subprocess
import json
import time
import sys

MAC_CLI = "mac"

# 1. 工具函数
def run_mac(*args, check=True):
    """运行 mac CLI 命令"""
    cmd = [MAC_CLI] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0 and check:
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"raw": result.stdout}

def send_hotkey(*keys):
    """发送快捷键"""
    result = run_mac("input", "hotkey", *keys, check=False)
    time.sleep(0.3)  # 等待 UI 响应
    return result and result.get("ok", False)

# 2. 环境检查
def check_environment():
    """检查关键环境项"""
    doctor = run_mac("doctor", check=False)
    # 只检查关键项
    if doctor:
        checks = doctor.get("error", {}).get("details", {}).get("checks", [])
        for check in checks:
            if check.get("name") in ["accessibility_permission", "appium_server"]:
                if check.get("status") != "pass":
                    return False
    return True

# 3. Setup / Teardown
def setup_session():
    """启动测试会话"""
    run_mac("session", "start", check=False)
    subprocess.run(["osascript", "-e", 
        'tell application "Microsoft Edge" to activate'], 
        capture_output=True)
    time.sleep(1)

def teardown():
    """清理"""
    run_mac("session", "end", check=False)

# 4. 测试函数
def test_example():
    """测试用例"""
    # 测试逻辑
    pass

# 5. 主入口
def main():
    try:
        if not check_environment():
            print("❌ 环境检查失败")
            sys.exit(1)
        
        setup_session()
        test_example()
        
    finally:
        teardown()

if __name__ == "__main__":
    main()
```

### 命名规范

- 文件名：`test_<功能>.py`（如 `test_tab_management.py`）
- 函数名：`test_<具体场景>()`（如 `test_open_new_tab()`）
- 使用中文注释说明测试目的

### 等待策略

```python
# ❌ 不好：固定等待
time.sleep(5)

# ✅ 好：适当等待
time.sleep(0.3)  # 快捷键后
time.sleep(1)    # 应用启动后
time.sleep(2)    # 页面加载后

# ✅ 更好：条件等待（未来改进）
def wait_for_element(selector, timeout=10):
    # 轮询检查元素是否存在
    pass
```

---

## 自动修复策略

### 使用装饰器

```python
from scripts.crash_recovery import with_recovery

@with_recovery(max_retries=3)
def test_something():
    """自动获得崩溃恢复能力"""
    run_mac("input", "hotkey", "command", "t")
```

### 崩溃类型

| 类型 | 触发条件 | 恢复策略 |
|------|----------|----------|
| DRIVER_NOT_RUNNING | Mac2 Driver 崩溃 | 重启 Session |
| SESSION_LOST | Session 丢失 | 重启 Session |
| APPIUM_UNREACHABLE | Appium 无响应 | 检查并重启 |
| TIMEOUT | 操作超时 | 延迟重试 |

### 手动恢复

```python
from scripts.crash_recovery import CrashRecovery

recovery = CrashRecovery()

try:
    # 测试代码
    run_mac("input", "hotkey", "command", "t")
except Exception as e:
    crash_type = recovery.detect_crash(str(e))
    if recovery.recover(crash_type, str(e)):
        # 重试
        run_mac("input", "hotkey", "command", "t")
```

---

## 错误处理

### 常见错误码

| 错误码 | 含义 | 解决方案 |
|--------|------|----------|
| `BACKEND_UNAVAILABLE` | 后端不可用 | 检查 Appium 和 Mac2 Driver |
| `NO_SESSION` | 无活动会话 | 调用 `session start` |
| `ELEMENT_NOT_FOUND` | 元素未找到 | 增加等待时间 |
| `PERMISSION_DENIED` | 权限不足 | 检查 Accessibility |

### 错误处理模式

```python
def safe_operation():
    """安全的操作模式"""
    result = run_mac("input", "hotkey", "command", "t", check=False)
    
    if result is None:
        print("命令执行失败")
        return False
    
    if not result.get("ok"):
        error = result.get("error", {})
        code = error.get("code", "UNKNOWN")
        
        if code == "NO_SESSION":
            run_mac("session", "start")
            return safe_operation()  # 重试
        
        print(f"错误: {code}")
        return False
    
    return True
```

---

## 常见问题 FAQ

### Q: mac doctor 显示 xcode_first_launch 失败

**A**: 运行以下命令：
```bash
sudo xcodebuild -runFirstLaunch
sudo xcodebuild -license accept
```

### Q: Accessibility 权限已添加但仍报错

**A**: 
1. 完全退出终端应用
2. 重新打开终端
3. 如果使用 VS Code，需要给 VS Code 也添加权限

### Q: Appium Server 无法连接

**A**: 
1. 确认 Appium 正在运行：`curl http://127.0.0.1:4723/status`
2. 如果没有运行，启动它：`appium`
3. 检查端口是否被占用：`lsof -i :4723`

### Q: Mac2 Driver 频繁崩溃

**A**: 
1. 使用 `@with_recovery` 装饰器自动恢复
2. 增加操作间的等待时间
3. 确保 Xcode First Launch 已完成

### Q: 测试运行太慢

**A**: 
1. 减少不必要的 `time.sleep()`
2. 使用条件等待替代固定等待
3. 并行运行独立的测试

### Q: 如何调试测试

**A**: 
1. 使用 `mac capture tree` 查看当前 UI 结构
2. 添加 `print()` 输出中间状态
3. 使用 `--dry-run` 模式（如果支持）

---

## 附录

### 常用快捷键

| 操作 | 快捷键 | 代码 |
|------|--------|------|
| 新建 Tab | Cmd+T | `send_hotkey("command", "t")` |
| 关闭 Tab | Cmd+W | `send_hotkey("command", "w")` |
| 刷新 | Cmd+R | `send_hotkey("command", "r")` |
| 地址栏 | Cmd+L | `send_hotkey("command", "l")` |
| 书签 | Cmd+D | `send_hotkey("command", "d")` |
| 历史 | Cmd+Y | `send_hotkey("command", "y")` |
| 下载 | Cmd+Shift+J | `send_hotkey("command", "shift", "j")` |

### 项目结构

```
fsq-test-pilot/
├── docs/
│   ├── SETUP.md          # 环境配置
│   ├── BEST_PRACTICES.md # 最佳实践（本文档）
│   └── POC-REPORT.md     # POC 报告
├── scripts/
│   ├── env_check.py      # 环境检查（Python）
│   ├── check-env.sh      # 环境检查（Bash）
│   └── crash_recovery.py # 崩溃恢复模块
└── tests/
    ├── test_tab_new.py
    ├── test_tab_management.py
    ├── test_download.py
    ├── test_history.py
    └── ...
```
