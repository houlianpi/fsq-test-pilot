# PRD: AI-Native Testing POC

## 项目概述

**项目名称**: fsq-test-pilot  
**目标**: 验证 fsq-mac 工具能否支撑 AI Agent 执行 macOS 自动化测试

## 背景

- `fsq-mac`: Agent-first macOS 自动化 CLI，支持 trace 录制/回放/codegen
- `edge-mac-test`: 现有 Edge Mac 测试用例（Behave BDD）

## 目标能力

| 能力 | 描述 | 验收标准 |
|------|------|----------|
| **Agent 能跑测试** | AI Agent 调用 fsq-mac CLI 执行测试 | Agent 能成功执行 3+ 测试场景 |
| **Agent 能自动修复** | 测试失败时，Agent 能读日志+UI状态，尝试修复 | 至少 1 个自动修复成功案例 |
| **Agent 能生成测试** | Agent 能从现有代码或 trace 生成新测试 | 生成 3+ 可执行的新测试用例 |

## Phase 1: POC 范围

### 1.1 选定测试场景（从 edge-mac-test 选）

- [ ] Tab 管理（新建/关闭/切换）
- [ ] 下载功能
- [ ] 历史记录

### 1.2 交付物

1. **Agent 测试执行器** — 能调用 fsq-mac 跑测试的 Agent 配置/脚本
2. **自动修复示例** — 至少 1 个测试失败→Agent 修复→重跑通过的案例
3. **测试生成示例** — Agent 生成的 3+ 新测试用例
4. **POC 报告** — 能力验证结果、限制、建议

## Phase 2: AI-Native 测试流程（POC 成功后）

- 建立标准化的 Agent 测试流程
- 集成 CI/CD
- 文档化最佳实践

## 技术依赖

- `fsq-mac` CLI
- macOS + Edge 浏览器
- Appium Mac2 Driver

## 里程碑

| 里程碑 | 目标 | 日期 |
|--------|------|------|
| M1 | 环境搭建 + 跑通第一个测试 | TBD |
| M2 | 3 个场景全部跑通 | TBD |
| M3 | 自动修复 + 测试生成验证 | TBD |
| M4 | POC 报告产出 | TBD |

## 团队

- **PM**: 康夫
- **Tech Lead**: Mattt
- **Dev**: 机器猫

---

*Last updated: 2026-04-07*
