# Plugin 開發介紹

> 這份簡報示範從零開始建立 Claude Code Plugin

## Part 1: 基礎概念

理解 Plugin 是什麼

## Plugin vs 獨立配置

兩種擴展 Claude Code 的方式

| 面向 | 獨立配置（.claude/） | Plugin |
|:-----|:------------------|:-------|
| Skill 名稱 | `/hello`（簡短）| `/plugin-name:hello`（命名空間）|
| 可用範圍 | 僅當前專案 | 跨專案、跨團隊 |
| 分享方式 | 手動複製 | 透過 marketplace 一鍵安裝 |
| 版本管理 | 無 | semver 或 git SHA |
| 適合情境 | 個人、實驗、單一專案 | 團隊、正式、跨專案 |

## Plugin 的 3 種元件

### Skills

可重用的知識庫 · `/skill-name` 觸發

### Agents

隔離的子任務 · 用 Task 工具呼叫

### Hooks

事件驅動腳本 · PreToolUse / PostToolUse

## 下一步

建立你的第一個 Plugin

- 🎯 立刻：建立 `.claude-plugin/plugin.json`
- 📚 30 分鐘：翻完 [02-plugins.md](../../02-plugins.md)
- 🛠 2 小時：建立 hello-world plugin
