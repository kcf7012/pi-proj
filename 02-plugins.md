# Plugin 開發入門

> 📖 系列：Claude Code Plugin 完整學習系列 #02
> 🌐 原文：[code.claude.com/docs/zh-TW/plugins](https://code.claude.com/docs/zh-TW/plugins)
> 📅 整理日期：2026 / 01
> 🎯 適用版本：Claude Code v2.1.x

## 本章你會學到

從零到發布的完整 Plugin 開發指南

- 🛠 **從零開始**：建立你的第一個 Plugin 並進行本地測試
- 📁 **理解結構**：掌握 Plugin 目錄組織與 manifest 配置
- ⚙️ **加入元件**：擴充 Skills、Agents、Hooks、MCP Servers
- 📤 **轉換與分享**：將獨立配置轉換並提交到 Marketplace

## Part 1: Plugin vs 獨立配置

兩種擴展 Claude Code 的方式

## Plugin vs 獨立配置

兩種擴展 Claude Code 的方式

| 面向 | 獨立配置（.claude/） | Plugin |
|:-----|:------------------|:-------|
| Skill 名稱 | `/hello`（簡短）| `/my-plugin:hello`（命名空間）|
| 可用範圍 | 僅當前專案 | 跨專案、跨團隊 |
| 分享方式 | 手動複製 | 透過 marketplace 一鍵安裝 |
| 版本管理 | 無 | semver 或 git SHA |
| 適合情境 | 個人、實驗、單一專案 | 團隊、正式、跨專案 |
| 建議起點 | ✓ 先用這個 | 確認要共享再升級 |

> 💡 建議路徑：在 .claude/ 中從獨立配置開始快速迭代，準備好共享時再轉成 plugin

## 什麼時候該升級成 Plugin？

明確的決策依據

| ✅ 用 Plugin 的時機 | ⏸️ 維持獨立的時機 |
|:---|:---|
| 想跟團隊成員共享 | 只是個人實驗 |
| 需要在多個專案重用 | 只在單一專案使用 |
| 需要版本控制和更新機制 | 不需要分享 |
| 透過 marketplace 發布 | 希望有簡短 skill 名稱 |
| 接受命名空間化（/plugin-name:hello）| 還在快速迭代階段 |
| 預期要長期維護 | 短期一次性使用 |

## Part 2: 5 步建立第一個 Plugin

從零到完成的完整流程

## 建立 Plugin 的 5 個步驟

從目錄結構到本地測試

### 1. 建立目錄

mkdir my-first-plugin · 建立 plugin 根目錄

### 2. 建立 manifest

.claude-plugin/plugin.json · 定義身份中繼資料

### 3. 加入 skill

skills/hello/SKILL.md · 第一個可呼叫的指令

### 4. 本地測試

claude --plugin-dir ./... · 用 CLI 旗標載入

### 5. 嘗試使用

/my-first-plugin:hello · 驗證功能正常

## Step 1：建立 Plugin 目錄

每個 plugin 位於自己的目錄中

```bash
mkdir my-first-plugin
```

## Step 2：建立 Plugin Manifest

定義 plugin 的中繼資料

`my-first-plugin/.claude-plugin/plugin.json`：

```json
{
  "name": "my-first-plugin",
  "description": "A greeting plugin to learn the basics",
  "version": "1.0.0",
  "author": {
    "name": "Your Name"
  }
}
```

| 欄位 | 用途 |
|:-----|:-----|
| `name` | 唯一識別碼和 skill 命名空間 |
| `description` | 在 plugin 管理器中顯示 |
| `version` | 選用，語意化版本控制 |
| `author` | 選用，作者資訊 |

## Step 3：加入第一個 Skill

每個 skill 是包含 SKILL.md 的資料夾

```bash
mkdir -p my-first-plugin/skills/hello
```

`my-first-plugin/skills/hello/SKILL.md`：

```markdown
---
description: Greet the user with a friendly message
disable-model-invocation: true
---

Greet the user warmly and ask how you can help them today.
```

## Step 4：用 --plugin-dir 本地測試

使用 CLI 旗標載入 plugin

```bash
claude --plugin-dir ./my-first-plugin
```

## Step 5：嘗試使用你的 Skill

驗證 skill 功能

```bash
/my-first-plugin:hello
```

Claude 會以問候語回應。執行 `/help` 會看到 skill 列在 plugin 命名空間下。

## Part 3: Plugin 完整結構

理解每個目錄的用途

## 完整 Plugin 目錄結構

每個元件的用途說明

| 目錄 | 位置 | 用途 |
|:-----|:-----|:-----|
| `.claude-plugin/` | Plugin 根目錄 | 包含 `plugin.json` manifest |
| `skills/` | Plugin 根目錄 | 作為 `<name>/SKILL.md` 目錄的 Skills |
| `commands/` | Plugin 根目錄 | 作為平面 Markdown 檔案的 Skills |
| `agents/` | Plugin 根目錄 | 自訂 agent 定義 |
| `hooks/` | Plugin 根目錄 | `hooks.json` 中的事件處理程式 |
| `.mcp.json` | Plugin 根目錄 | MCP server 配置 |
| `.lsp.json` | Plugin 根目錄 | LSP server 配置 |
| `monitors/` | Plugin 根目錄 | 背景監視器配置 |
| `bin/` | Plugin 根目錄 | 加入到 PATH 的可執行檔 |
| `settings.json` | Plugin 根目錄 | 預設設定 |

> ⚠️ 不要將 commands/、agents/、skills/ 或 hooks/ 放在 .claude-plugin/ 目錄內

## Plugin Manifest 完整欄位

plugin.json 所有可用欄位

| 欄位 | 必填 | 用途 |
|:-----|:-----|:-----|
| `name` | 是 | 唯一識別碼，skill 命名空間前綴 |
| `description` | 是 | 在 plugin 管理器中顯示 |
| `version` | 否 | 語意化版本，影響更新通知 |
| `author` | 否 | 作者資訊（name, email, url） |
| `homepage` | 否 | plugin 首頁 URL |
| `repository` | 否 | source code URL |
| `license` | 否 | 授權類型 |
| `keywords` | 否 | 搜尋標籤 |
| `commands` | 否 | 預設啟用的 commands |
| `hooks` | 否 | plugin 預設 hooks |
| `mcpServers` | 否 | MCP server 宣告 |
| `lspServers` | 否 | LSP server 宣告 |

> 如果省略 `version` 且 plugin 透過 git 分發，會使用 commit SHA 作為版本

## Part 4: 加入更多元件

Skills、Agents、Hooks、MCP

## 加入更多 Skills

在 plugin 根目錄新增 `skills/` 目錄

```text
my-plugin/
├── .claude-plugin/
│   └── plugin.json
└── skills/
    └── code-review/
        └── SKILL.md
```

`SKILL.md` 包含 YAML frontmatter 和說明：

```yaml
---
description: Reviews code for best practices and potential issues. Use when reviewing code, checking PRs, or analyzing code quality.
---

When reviewing code, check for:
1. Code organization and structure
2. Error handling
3. Security concerns
4. Test coverage
```

## 加入 Agents 和 Hooks

自訂 agent 與事件處理

**Agents** 放在 `agents/` 目錄：

```text
agents/
├── security-reviewer.md
└── performance-tester.md
```

**Hooks** 放在 `hooks/hooks.json`：

```json
{
  "PostToolUse": [
    {
      "matcher": "Write|Edit",
      "hooks": [
        {
          "type": "command",
          "command": "${CLAUDE_PLUGIN_ROOT}/scripts/format.sh"
        }
      ]
    }
  ]
}
```

## 加入 MCP Servers 和 LSP

連接外部服務與程式碼智慧

**MCP server** 配置在 `.mcp.json`：

```json
{
  "github": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-github"],
    "env": {
      "GITHUB_TOKEN": "${GITHUB_TOKEN}"
    }
  }
}
```

**LSP server** 配置在 `.lsp.json`：

```json
{
  "go": {
    "command": "gopls",
    "args": ["serve"]
  }
}
```

> 對於 TypeScript、Python、Rust 等常見語言，從官方 marketplace 安裝預先建立的 LSP plugins

## Part 5: 轉換獨立配置 + 除錯

從 .claude/ 升級到 plugin

## 將獨立配置轉換為 Plugin

從 `.claude/` 升級到完整 plugin

### Step 1：建立新目錄

```bash
mkdir -p my-plugin/.claude-plugin
```

### Step 2：建立 manifest

`my-plugin/.claude-plugin/plugin.json`：

```json
{
  "name": "my-plugin",
  "description": "Migrated from standalone configuration",
  "version": "1.0.0"
}
```

### Step 3：複製你的配置

```bash
# Copy commands
cp -r .claude/commands my-plugin/

# Copy agents (if any)
cp -r .claude/agents my-plugin/

# Copy skills (if any)
cp -r .claude/skills my-plugin/
```

### Step 4：處理 hooks

如果你在設定中有 hooks，建立 hooks 目錄：

```bash
mkdir my-plugin/hooks
```

## 常見問題與除錯

排除 plugin 開發問題

### 使用 Debug 模式

```bash
claude --debug --plugin-dir ./my-plugin
```

這會顯示：
- 正在載入哪些 plugins
- Plugin manifests 中的任何錯誤
- Skill、agent 和 hook 註冊
- MCP server 初始化

### 常見錯誤與解決方案

| 問題 | 原因 | 解決方案 |
|:-----|:-----|:---------|
| Plugin 未載入 | 無效的 `plugin.json` | 執行 `claude plugin validate` |
| Skills 未出現 | 目錄結構錯誤 | 確保 `skills/` 在 plugin 根目錄 |
| Hooks 未觸發 | 腳本不可執行 | 執行 `chmod +x script.sh` |
| MCP server 失敗 | 缺少 `${CLAUDE_PLUGIN_ROOT}` | 對所有 plugin 路徑使用變數 |
| 路徑錯誤 | 使用了絕對路徑 | 所有路徑必須是相對的 |
| LSP 找不到執行檔 | 語言伺服器未安裝 | 安裝對應的二進位檔 |

## 提交到 Marketplace

讓其他人可以使用你的 plugin

### 提交前檢查清單

- 在本地驗證：`claude plugin validate`
- 確保完整文件：`README.md` 包含安裝和使用說明
- 測試所有元件：skills、agents、hooks、MCP servers
- 檢查 marketplace.json：所有 source 路徑都正確
- 版本控制：選擇合適的版本策略

### 提交到社群 Marketplace

使用應用內提交表單：

- **claude.ai**：[claude.ai/admin-settings/directory/submissions/plugins/new](https://claude.ai/admin-settings/directory/submissions/plugins/new)
- **Console**：[platform.claude.com/plugins/submit](https://platform.claude.com/plugins/submit)

> 已批准的 plugins 會固定到 anthropics/claude-plugins-community 目錄中的特定 commit SHA

## 重點回顧

- Plugins 是可分享、可版本化的擴展套件
- 用 `claude --plugin-dir ./path` 本地測試
- 完整結構：`.claude-plugin/` + skills + agents + hooks + MCP
- 從獨立配置開始，準備好時升級成 plugin
- 用 `claude plugin validate` 驗證
- 透過 marketplace 分享給團隊或社群

- 🎯 立刻：用 `--plugin-dir` 建立第一個 plugin
- 📚 30 分鐘：翻完 [03-plugins-reference.md](./03-plugins-reference.md)
- 🛠 2 小時：建立一個有 skill + agent 的 plugin
- 🚀 一週：透過 marketplace 分享給團隊

## 建立你的第一個 Plugin！📦

從 [02-plugins.md](./02-plugins.md) Step 1 開始，建立你的第一個 plugin

整理自官方文件 · 繁體中文教學用途
