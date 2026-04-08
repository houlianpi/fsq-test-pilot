# 环境搭建指南

本文档记录 AI-Native Testing POC 的开发环境配置步骤。

## 前置条件

- macOS
- Python 3.10+
- Node.js 18+
- Xcode Command Line Tools

## 安装步骤

### 1. 安装 fsq-mac CLI

```bash
# 推荐使用 pipx（隔离环境）
brew install pipx
pipx install fsq-mac --python python3.12

# 验证安装
mac --version
# 预期输出: fsq-mac 0.2.1
```

### 2. 安装 Appium + Mac2 驱动

```bash
# 安装 Appium
npm install -g appium

# 安装 Mac2 驱动
appium driver install mac2

# 验证驱动安装
appium driver list
# 预期看到: mac2@x.x.x [installed]
```

### 3. 配置 macOS 权限

#### Accessibility 权限

1. 打开 **System Settings > Privacy & Security > Accessibility**
2. 点击 `+` 添加你的终端应用（Terminal / iTerm2 / VS Code）
3. 确保开关已打开

#### Xcode 首次启动配置（如有完整 Xcode）

```bash
sudo xcodebuild -runFirstLaunch
```

### 4. 启动 Appium 服务

```bash
# 新开一个终端窗口
appium

# 默认监听 http://127.0.0.1:4723
```

### 5. 验证环境

```bash
# 在另一个终端运行
mac doctor
```

预期输出（所有检查通过）：
```json
{
  "ok": true,
  "command": "doctor",
  "data": {
    "checks": [
      {"name": "accessibility_permission", "status": "pass"},
      {"name": "xcode_first_launch", "status": "pass"},
      {"name": "appium_server", "status": "pass"},
      {"name": "mac2_driver", "status": "pass"},
      {"name": "config_file", "status": "pass"}
    ],
    "all_pass": true
  }
}
```

## 常见问题

### Q: `mac doctor` 显示 `accessibility_permission` 失败

**解决方案：**
1. 打开 System Settings > Privacy & Security > Accessibility
2. 添加你的终端应用并开启权限
3. 重启终端后重试

### Q: `appium_server` 检查失败

**解决方案：**
1. 确保 Appium 服务正在运行：`appium`
2. 检查端口是否被占用：`lsof -i :4723`

### Q: Python 版本不兼容

**解决方案：**
```bash
# 安装 Python 3.12
brew install python@3.12

# 使用 pipx 指定 Python 版本
pipx install fsq-mac --python python3.12
```

## 验证清单

- [x] fsq-mac CLI 安装成功 (`mac --version`)
- [x] Appium 安装成功 (`appium --version`)
- [x] Mac2 驱动安装成功 (`appium driver list`)
- [ ] Accessibility 权限配置（需要手动配置）
- [ ] `mac doctor` 全部通过（需要启动 Appium 服务）

## 下一步

环境搭建完成后，继续执行 Issue #2：跑通第一个测试（Tab 新建场景）。
