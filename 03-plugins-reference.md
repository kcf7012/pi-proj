# Plugin 技術參考（完整規格）

> 📖 系列：Claude Code Plugin 完整學習系列 #03
> 🌐 原文：[code.claude.com/docs/zh-TW/plugins-reference](https://code.claude.com/docs/zh-TW/plugins-reference)
> 📅 整理日期：2026 / 01
> 🎯 適用版本：Claude Code v2.1.x

## 本章你會學到

完整 Plugin 技術規格攻略

- 🧩 **元件總覽**：7 種 Plugin 元件一次看懂
- 📋 **Manifest 完整架構**：plugin.json 所有欄位速查
- 🗂 **快取與目錄結構**：Plugin 怎麼被隔離與管理
- 🛠 **CLI 完整指令**：10 個 plugin 管理指令
- 🐛 **偵錯與開發工具**：claude --debug 與常見問題
- 📤 **發佈與版本控制**：semver 與發行策略
- 📑 **參考速查**：整合所有關鍵資訊

## Part 1: Plugin 元件總覽

7 種元件一次看懂

## Plugin 的 7 種元件

Plugin 可包含 7 種元件，各自放在獨立目錄

### Skills

`skills/<name>/SKILL.md` · 用 `/skill-name` 觸發

### Agents

`agents/<name>.md` · 自訂子任務代理人

### Hooks

`hooks/hooks.json` · 事件驅動腳本

### MCP Servers

`.mcp.json` · 連接外部服務

### LSP Servers

`.lsp.json` · 程式碼智慧

### Monitors

`monitors/monitors.json` · 背景監視器

### Themes

`themes/theme.json` · 自訂主題

## Skills 詳解

放在 `skills/<name>/SKILL.md`，每個 skill 一個資料夾

```markdown
---
description: Reviews code for best practices
disable-model-invocation: false
---

When reviewing code, check for:
1. Code organization
2. Error handling
3. Security concerns
```

| 欄位 | 必填 | 描述 |
|:-----|:-----|:-----|
| `description` | 是 | skill 描述 |
| `disable-model-invocation` | 否 | 禁止 Claude 自動呼叫 |

## Agents 詳解

放在 `agents/<name>.md`，可獨立執行任務

```markdown
---
name: security-reviewer
description: Reviews code for security issues
tools: Read, Grep, Glob
model: sonnet
---

You are a security reviewer...
```

| 欄位 | 必填 | 描述 |
|:-----|:-----|:-----|
| `name` | 是 | agent 名稱 |
| `description` | 是 | agent 用途 |
| `tools` | 否 | 可用工具清單 |
| `model` | 否 | 指定模型 |

## Hooks 詳解

放在 `hooks/hooks.json`，事件驅動的自動化

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

支援的事件：
- `PreToolUse`：工具執行前
- `PostToolUse`：工具執行後
- `Notification`：通知時
- `Stop`：結束時

## MCP Servers 詳解

放在 `.mcp.json`，連接外部服務

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

| 欄位 | 必填 | 描述 |
|:-----|:-----|:-----|
| `command` | 是 | 啟動 MCP server 的命令 |
| `args` | 否 | 命令參數 |
| `env` | 否 | 環境變數 |

## LSP Servers 詳解

放在 `.lsp.json`，提供程式碼智慧

```json
{
  "go": {
    "command": "gopls",
    "args": ["serve"],
    "extensionToLanguage": {
      ".go": "go"
    }
  }
}
```

支援的常見語言：
- TypeScript / JavaScript
- Python（pyright、pylsp）
- Rust（rust-analyzer）
- Go（gopls）

## Monitors 詳解

放在 `monitors/monitors.json`，背景監視日誌與外部狀態

```json
[
  {
    "name": "error-log",
    "command": "tail -F ./logs/error.log",
    "description": "Application error log"
  }
]
```

每個 stdout 行會作為通知傳遞給 Claude。

## Themes 與 Skills 目錄 Plugins

放在 `themes/theme.json`，自訂視覺主題

```json
{
  "name": "dark-pro",
  "colors": {
    "primary": "#FF6B35",
    "secondary": "#004E89"
  }
}
```

`--plugin-dir` 旗標可以一次載入多個 plugins：

```bash
claude --plugin-dir ./plugin1 --plugin-dir ./plugin2
```

## Part 2: Plugin Manifest 完整架構

plugin.json 所有欄位

## plugin.json 完整架構

```json
{
  "name": "my-plugin",
  "version": "1.0.0",
  "description": "Plugin 描述",
  "author": {
    "name": "Your Name",
    "email": "you@example.com"
  },
  "homepage": "https://example.com",
  "repository": "https://github.com/you/plugin",
  "license": "MIT",
  "keywords": ["keyword1", "keyword2"],
  "commands": "./commands",
  "hooks": "./hooks/hooks.json",
  "mcpServers": "./.mcp.json",
  "lspServers": "./.lsp.json"
}
```

## 中繼資料欄位速查

| 欄位 | 必填 | 類型 | 描述 |
|:-----|:-----|:-----|:-----|
| `name` | 是 | string | Plugin 名稱（kebab-case）|
| `version` | 否 | string | 語意化版本 |
| `description` | 否 | string | Plugin 描述 |
| `author` | 否 | object | 作者資訊 |
| `homepage` | 否 | string | Plugin 首頁 URL |
| `repository` | 否 | string | source code URL |
| `license` | 否 | string | 授權類型 |
| `keywords` | 否 | array | 搜尋標籤 |

## 元件路徑欄位速查

| 欄位 | 預設值 | 描述 |
|:-----|:-------|:-----|
| `commands` | `./commands` | Commands 目錄路徑 |
| `hooks` | `./hooks/hooks.json` | Hooks 配置檔路徑 |
| `mcpServers` | `./.mcp.json` | MCP 配置檔路徑 |
| `lspServers` | `./.lsp.json` | LSP 配置檔路徑 |

> 所有路徑必須是相對的，並以 `./` 開頭

## 使用者設定：userConfig

`userConfig` 讓 plugin 要求使用者提供設定值

```json
{
  "userConfig": {
    "apiKey": {
      "type": "string",
      "description": "Your API key",
      "required": true
    }
  }
}
```

使用者透過 `/plugin` 介面設定值，Claude Code 將值注入為環境變數。

## 3 個關鍵環境變數

| 環境變數 | 用途 |
|:---------|:-----|
| `${CLAUDE_PLUGIN_ROOT}` | Plugin 根目錄絕對路徑 |
| `${CLAUDE_PROJECT_DIR}` | 當前專案目錄 |
| `${USER_CONFIG_KEY}` | userConfig 設定值 |

```bash
#!/bin/bash
# hooks/format.sh
cd "${CLAUDE_PROJECT_DIR}"
prettier --write "${CLAUDE_PLUGIN_ROOT}/src/**/*.js"
```

## Part 3: 快取、目錄結構、CLI

Plugin 怎麼被隔離與管理

## Plugin 快取與檔案解析

Plugin 安裝後會被快取到 `~/.claude/plugins/cache/`

```
~/.claude/plugins/
├── cache/
│   └── company-tools/
│       ├── 1.0.0/
│       │   └── plugin/
│       └── latest/
└── installed.json
```

> 快取機制讓 plugin 不會影響全域環境，且可同時存在多個版本

## Plugin 完整目錄結構

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json
├── commands/
│   └── deploy.md
├── skills/
│   ├── code-review/
│   │   └── SKILL.md
│   └── pdf-processor/
│       ├── SKILL.md
│       └── scripts/
├── agents/
│   └── security-reviewer.md
├── hooks/
│   └── hooks.json
├── .mcp.json
├── .lsp.json
├── monitors/
│   └── monitors.json
├── themes/
│   └── theme.json
├── bin/
│   └── format.sh
├── settings.json
└── README.md
```

## Part 4: CLI 完整指令參考

10 個 plugin 管理指令

## plugin init — 快速搭建

```bash
/plugin init my-plugin
```

會自動建立：

- `.claude-plugin/plugin.json` manifest
- `README.md` 範本
- `.gitignore`

## plugin install / uninstall

```bash
# 安裝
/plugin install <plugin>@<marketplace>

# 解除安裝
/plugin uninstall <plugin>
```

> 解除安裝會移除 plugin 檔案但保留使用者設定

## prune / enable / disable

```bash
# 清理未使用的 plugins
/plugin prune

# 啟用已停用的 plugin
/plugin enable <plugin>

# 停用 plugin（不解除安裝）
/plugin disable <plugin>
```

## update / list / details / tag

```bash
# 更新 marketplace 副本
/plugin marketplace update

# 列出已安裝 plugins
/plugin list

# 查看 plugin 詳細資訊
/plugin details <plugin>

# 標記當前版本為發行版
/plugin tag <plugin> v1.0.0
```

## Part 5: 偵錯與開發工具

claude --debug 與常見問題

## 偵錯命令：claude --debug

```bash
claude --debug --plugin-dir ./my-plugin
```

顯示：
- 正在載入的 plugins
- Plugin manifest 錯誤
- Skill / agent / hook 註冊
- MCP server 初始化
- LSP server 啟動

## 常見問題與解決方案

| 問題 | 原因 | 解決方案 |
|:-----|:-----|:---------|
| Plugin 未載入 | 無效的 plugin.json | `claude plugin validate` |
| Skills 未出現 | 目錄結構錯誤 | 確保 skills/ 在 plugin 根目錄 |
| Hooks 未觸發 | 腳本不可執行 | `chmod +x script.sh` |
| MCP server 失敗 | 缺少環境變數 | 設定 `${CLAUDE_PLUGIN_ROOT}` |
| 路徑錯誤 | 使用了絕對路徑 | 改用相對路徑 |

## 範例錯誤訊息

```
Error: Plugin 'foo' failed to load
  - .claude-plugin/plugin.json: missing required field 'name'
  - skills/bar/SKILL.md: frontmatter description is empty
```

> 錯誤訊息會指出哪個檔案、哪個欄位有問題

## Hook 疑難排解速查

| 症狀 | 可能原因 |
|:-----|:---------|
| Hook 沒觸發 | matcher pattern 不對 |
| 權限錯誤 | 腳本沒 chmod +x |
| 環境變數空 | 沒用 `${CLAUDE_PLUGIN_ROOT}` |
| 輸出被截斷 | 超過 30 秒 timeout |

## 目錄結構錯誤：最常見陷阱

> ⚠️ 不要將 `commands/`、`agents/`、`skills/` 或 `hooks/` 放在 `.claude-plugin/` 目錄內

正確：
```
my-plugin/
├── .claude-plugin/plugin.json
└── skills/foo/SKILL.md
```

錯誤：
```
my-plugin/
└── .claude-plugin/
    ├── plugin.json
    └── skills/foo/SKILL.md  ← ❌ 這裡
```

## Part 6: 發佈與版本控制

semver 與發行策略

## 版本管理：4 種解析來源

| 來源 | 格式 | 範例 |
|:-----|:-----|:-----|
| 明確版本 | `1.2.3` | `"version": "1.2.3"` |
| Git tag | `v1.2.3` | 由 git 自動解析 |
| Git SHA | `abc1234` | 完整 commit SHA |
| latest | `latest` | 永遠抓最新 commit |

> 使用 `stable` 通道時必須是 `1.2.3` 格式；`latest` 通道接受任意 git ref

## Semantic Versioning 與 CHANGELOG

| 變更類型 | 版本變化 | 範例 |
|:---------|:---------|:-----|
| 不相容變更 | MAJOR | 1.0.0 → 2.0.0 |
| 新增功能（向後相容）| MINOR | 1.0.0 → 1.1.0 |
| Bug 修復 | PATCH | 1.0.0 → 1.0.1 |

建議維護 `CHANGELOG.md` 記錄每個版本的變更。

## plugin tag — 發行版標籤

```bash
# 標記當前版本
git tag v1.0.0
git push origin v1.0.0

# 在 plugin.json 引用
{
  "version": "1.0.0"
}
```

## Part 7: 參考速查與重點回顧

整合所有關鍵資訊

## 7 種元件總結速查

| 元件 | 目錄 | 用途 |
|:-----|:-----|:-----|
| Skills | `skills/` | 可重用的知識庫 |
| Agents | `agents/` | 隔離的子任務 |
| Hooks | `hooks/` | 事件自動化 |
| MCP Servers | `.mcp.json` | 外部服務 |
| LSP Servers | `.lsp.json` | 程式碼智慧 |
| Monitors | `monitors/` | 背景監視 |
| Themes | `themes/` | 自訂主題 |

## CLI 完整指令速查表

| 指令 | 用途 |
|:-----|:-----|
| `/plugin init` | 建立新 plugin |
| `/plugin install` | 安裝 plugin |
| `/plugin uninstall` | 解除安裝 |
| `/plugin enable` | 啟用 |
| `/plugin disable` | 停用 |
| `/plugin prune` | 清理未使用 |
| `/plugin list` | 列出已安裝 |
| `/plugin details` | 查看詳細資訊 |
| `/plugin tag` | 標記版本 |
| `/plugin marketplace` | 管理 marketplaces |

## 環境變數總結

| 環境變數 | 用途 |
|:---------|:-----|
| `${CLAUDE_PLUGIN_ROOT}` | Plugin 根目錄 |
| `${CLAUDE_PROJECT_DIR}` | 當前專案目錄 |
| `${USER_CONFIG_KEY}` | userConfig 設定值 |

## plugin.json 欄位總表

完整 plugin.json 欄位速查見 [Part 2: plugin.json 完整架構](#plugin-json-完整架構)

| 必填 | 選填 |
|:-----|:-----|
| `name` | `version`, `description`, `author`, `homepage`, `repository`, `license`, `keywords` |
| | `commands`, `hooks`, `mcpServers`, `lspServers`, `userConfig` |

## 路徑行為規則速查

| 路徑類型 | 解析規則 |
|:---------|:---------|
| `./xxx` | 相對於 plugin 根目錄 |
| `../xxx` | 相對於上層目錄 |
| `${CLAUDE_PLUGIN_ROOT}/xxx` | 絕對路徑 |
| 絕對路徑 | ❌ 不允許 |

## plugin validate 完整指南

```bash
# 驗證單一 plugin
claude plugin validate ./my-plugin

# 驗證 marketplace
claude plugin validate ./my-marketplace

# 詳細輸出
claude plugin validate --verbose ./my-plugin
```

檢查項目：
- JSON 語法
- 必填欄位
- 路徑存在性
- frontmatter 格式

## 發佈完整流程（明確版本）

1. 在 plugin.json 設定 `version: "1.0.0"`
2. `git tag v1.0.0`
3. `git push origin v1.0.0`
4. 在 marketplace.json 引用：
   ```json
   {
     "name": "my-plugin",
     "source": "./plugins/my-plugin",
     "version": "1.0.0"
   }
   ```
5. 推送 marketplace：`git push`
6. 使用者執行 `/plugin marketplace update`

## 相關文件與資源

| 文件 | 內容 |
|:-----|:-----|
| [01-plugin-marketplaces.md](./01-plugin-marketplaces.md) | Marketplace 完整攻略 |
| [02-plugins.md](./02-plugins.md) | Plugin 開發入門 |
| [04-skills.md](./04-skills.md) | Skills 完整指南 |
| [05-subagents.md](./05-subagents.md) | Subagents 自訂指南 |
| [06-hooks.md](./06-hooks.md) | Hooks 自動化指南 |

官方文件：[code.claude.com/docs/zh-TW/plugins-reference](https://code.claude.com/docs/zh-TW/plugins-reference)

## 重點回顧

- Plugin 包含 7 種元件：skills、agents、hooks、MCP、LSP、monitors、themes
- plugin.json 是 plugin 的身份證
- 目錄結構必須遵循規範（元件目錄在 plugin 根目錄）
- `${CLAUDE_PLUGIN_ROOT}` 是 hooks 必用的環境變數
- 用 `claude --debug` 排查問題
- 用 `claude plugin validate` 驗證
- 用 semver + git tag 管理版本

- 🎯 立刻：用 `claude plugin validate` 檢查現有 plugin
- 📚 30 分鐘：複習 7 種元件的目錄結構
- 🛠 2 小時：為 plugin 加上 hooks 自動化
- 🚀 一週：建立完整的 plugin 並發佈到 marketplace
