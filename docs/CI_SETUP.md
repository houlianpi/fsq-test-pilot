# CI/CD 配置指南

## GitHub Actions Workflows

### 1. test.yml - 主测试流程

**触发条件**：
- Push 到 main 分支
- PR 到 main 分支
- 手动触发

**Jobs**：
| Job | Runner | 说明 |
|-----|--------|------|
| lint | ubuntu-latest | Python 语法检查 |
| env-check | ubuntu-latest | 验证环境脚本 |
| report | ubuntu-latest | 生成测试摘要 |

### 2. pr-comment.yml - PR 评论

自动在 PR 上添加测试报告评论。

## Self-Hosted Runner 配置

由于 macOS GUI 测试需要：
- Accessibility 权限
- Appium 服务
- 屏幕访问

需要配置 self-hosted runner：

### 步骤

1. **在 GitHub 仓库设置中添加 runner**
   ```
   Settings → Actions → Runners → New self-hosted runner
   ```

2. **在 Mac 上安装 runner**
   ```bash
   # 下载并解压 runner
   mkdir actions-runner && cd actions-runner
   curl -o actions-runner-osx-arm64.tar.gz -L https://github.com/actions/runner/releases/download/v2.XXX.X/actions-runner-osx-arm64-2.XXX.X.tar.gz
   tar xzf ./actions-runner-osx-arm64.tar.gz
   
   # 配置
   ./config.sh --url https://github.com/YOUR_ORG/YOUR_REPO --token YOUR_TOKEN
   
   # 作为服务运行
   ./svc.sh install
   ./svc.sh start
   ```

3. **确保环境就绪**
   ```bash
   # 安装依赖
   pipx install fsq-mac
   npm install -g appium
   appium driver install mac2
   
   # 启动 Appium（作为服务或在后台）
   nohup appium > /tmp/appium.log 2>&1 &
   
   # 验证
   ./scripts/check-env.sh
   ```

4. **启用 workflow 中的 macOS job**
   
   取消 `test.yml` 中 `macos-test` job 的注释。

## 测试报告

测试结果会显示在：
- GitHub Actions 运行摘要
- PR 评论
- Commit 状态检查

## 常见问题

### Q: 为什么不用 GitHub 托管的 macOS runner？

A: GitHub 托管的 macOS runner 没有 GUI session，无法运行 Accessibility 自动化测试。

### Q: Self-hosted runner 安全吗？

A: 建议：
- 仅在私有仓库使用
- 或设置 runner 只接受特定 label 的 job
- 定期更新 runner 版本
