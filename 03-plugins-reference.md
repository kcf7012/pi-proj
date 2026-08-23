# Plugin 技術參考（完整規格）

> 📖 **系列**：Claude Code Plugin 完整學習系列 #03
> 🌐 **原文**：[code.claude.com/docs/zh-TW/plugins-reference](https://code.claude.com/docs/zh-TW/plugins-reference)
> 📅 **整理日期**：2026 / 01
> 🎯 **適用版本**：Claude Code v2.1.x

> 💡 **本系列總覽**：見 [00-claude-code-plugins-series.md](./00-claude-code-plugins-series.md)
> 📚 **上一篇**：[02-plugins.md](./02-plugins.md)（Plugin 開發指南）
> 📚 **下一篇**：[04-skills.md](./04-skills.md)（Skills 完整指南）

## 目錄

1. [Plugin 元件參考](#plugin-元件參考)
2. [Plugin 安裝範圍](#plugin-安裝範圍)
3. [Skills 目錄 Plugins](#skills-目錄-plugins)
4. [Plugin manifest 完整架構](#plugin-manifest-完整架構)
5. [Plugin 快取與檔案解析](#plugin-快取與檔案解析)
6. [Plugin 目錄結構](#plugin-目錄結構)
7. [CLI 完整指令參考](#cli-完整指令參考)
8. [偵錯與開發工具](#偵錯與開發工具)
9. [發佈與版本控制](#發佈與版本控制)

---

## Plugin 元件參考

Plugin 元件包括 **skills、agents、hooks、MCP servers、LSP servers、monitors、themes**。

### Skills

Plugins 將 skills 新增至 Claude Code，建立 `/name` 快捷方式。

**位置**：`skills/` 或 `commands/` 目錄在 plugin 根目錄，或 plugin 根目錄中的單一 `SKILL.md` 檔案

**檔案格式**：Skills 是包含 `SKILL.md` 的目錄；commands 是簡單的 markdown 檔案

**Skill 結構**：

```text
skills/
├── pdf-processor/
│   ├── SKILL.md
│   ├── reference.md (optional)
│   └── scripts/ (optional)
└── code-reviewer/
    └── SKILL.md
```

Skills 和 commands 在安裝 plugin 時自動發現。

> 如果 plugin 沒有 `skills/` 目錄且沒有 `skills` manifest 欄位，plugin 根目錄中的 `SKILL.md` 會被載入為單一 skill。
> 設定 frontmatter `name` 欄位以控制 skill 的叫用名稱。

**Plugin skills 中的布林 frontmatter 欄位**（如 `disable-model-invocation`）**接受 `yes`、`no`、`on`、`off`、`1` 和 `0`**，任何大小寫，除 `true` 和 `false` 外。v2.1.218 之前只識別 `true` 和 `false`。

完整詳細資訊見 [Skills](./04-skills.md)。

---

### Agents

Plugins 可以提供專門的 subagents，用於 Claude 在適當時自動叫用的特定任務。

**位置**：`agents/` 目錄在 plugin 根目錄

**檔案格式**：描述 agent 功能的 Markdown 檔案

**Agent 結構**：

```markdown
---
name: agent-name
description: 此 agent 的專長以及 Claude 應何時叫用它
model: sonnet
effort: medium
maxTurns: 20
disallowedTools: Write, Edit
---

詳細的系統提示，描述 agent 的角色、專業知識和行為。
```

**Plugin agents 支援** `name`、`description`、`model`、`effort`、`maxTurns`、`tools`、`disallowedTools`、`skills`、`memory`、`background` 和 `isolation` frontmatter 欄位。

唯一有效的 `isolation` 值是 `"worktree"`。

> ⚠️ 出於安全原因，plugin 提供的 agents **不支援** `hooks`、`mcpServers` 和 `permissionMode`。

Agents 出現在 [@-mention 下拉式選單](./05-subagents.md#invoke-subagents-explicitly) 中，其範圍名稱為 `my-plugin:code-reviewer`，一旦啟用 plugin。

完整詳細資訊見 [Subagents](./05-subagents.md)。

---

### Hooks

Plugins 可以提供事件處理程式，自動回應 Claude Code 事件。

**位置**：`hooks/hooks.json` 在 plugin 根目錄，或在 `plugin.json` 中內聯

**格式**：具有事件匹配器和動作的 JSON 設定

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "\"${CLAUDE_PLUGIN_ROOT}\"/scripts/format-code.sh"
          }
        ]
      }
    ]
  }
}
```

Plugin hooks 回應與 [user-defined hooks](./06-hooks.md) 相同的生命週期事件。

**Hook 類型**：
- `command`：執行 shell 命令或指令碼
- `http`：將事件 JSON 作為 POST 請求傳送到 URL
- `mcp_tool`：在已設定的 [MCP server](https://code.claude.com/docs/zh-TW/mcp) 上呼叫工具
- `prompt`：使用 LLM 評估提示
- `agent`：執行具有工具的 agentic 驗證器

完整事件表見 [Hooks 指南](./06-hooks.md#hook-生命週期)。

> 針對 plugin 自己的 [bundled MCP server](#mcp-servers) 的 Hooks 必須使用其範圍名稱。工具匹配器和 `if` 欄位採用範圍工具名稱 `mcp__plugin_<plugin>_<server>__<tool>`，而 `mcp_tool` hook 的 `server` 欄位採用 `plugin::<server>`。針對裸伺服器金鑰撰寫的匹配器永遠不會觸發。

---

### MCP servers

Plugins 可以捆綁 Model Context Protocol (MCP) servers，將 Claude Code 與外部工具和服務連接。

**位置**：`.mcp.json` 在 plugin 根目錄，或在 `plugin.json` 中內聯

**格式**：標準 MCP server 設定

```json
{
  "mcpServers": {
    "plugin-database": {
      "command": "${CLAUDE_PLUGIN_ROOT}/servers/db-server",
      "args": ["--config", "${CLAUDE_PLUGIN_ROOT}/config.json"],
      "env": {
        "DB_PATH": "${CLAUDE_PLUGIN_ROOT}/data"
      }
    },
    "plugin-api-client": {
      "command": "npx",
      "args": ["@company/mcp-server", "--plugin-mode"]
    }
  }
}
```

**整合行為**：
- 啟用 plugin 時，Plugin MCP servers **自動啟動**
- Servers 在 Claude 的工具組中顯示為標準 MCP 工具
- Server 功能與 Claude 的現有工具無縫整合
- Plugin servers 可以獨立於使用者 MCP servers 進行設定

> 如果你在 session 中途運行 [`/reload-plugins`](https://code.claude.com/docs/zh-TW/discover-plugins#apply-plugin-changes-without-restarting)，Claude Code 會**保留配置未變更**的 servers 的即時連線。

---

### LSP servers

> 想要使用 LSP plugins？從官方 marketplace 安裝它們：在 `/plugin` Discover 標籤中搜尋「lsp」。本節記錄如何為官方 marketplace 未涵蓋的語言建立 LSP plugins。

Plugins 可以提供 [Language Server Protocol](https://microsoft.github.io/language-server-protocol/) (LSP) servers，在處理程式碼庫時為 Claude 提供即時程式碼智慧。

LSP 整合提供：
- **即時診斷**：Claude 在每次編輯後立即看到錯誤和警告
- **程式碼導航**：前往定義、尋找參考和懸停資訊
- **語言感知**：程式碼符號的類型資訊和文件

**位置**：`.lsp.json` 在 plugin 根目錄，或在 `plugin.json` 中內聯

**格式**：將語言伺服器名稱對應到其設定的 JSON 設定

`.lsp.json` 檔案格式：

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

在 `plugin.json` 中內聯：

```json
{
  "name": "my-plugin",
  "lspServers": {
    "go": {
      "command": "gopls",
      "args": ["serve"],
      "extensionToLanguage": {
        ".go": "go"
      }
    }
  }
}
```

**必需欄位**：

| 欄位 | 描述 |
|:-----|:-----|
| `command` | 要執行的 LSP 二進位檔（必須在 PATH 中） |
| `extensionToLanguage` | 將檔案副檔名對應到語言識別碼 |

**選用欄位**：

| 欄位 | 描述 |
|:-----|:-----|
| `args` | LSP server 的命令列引數 |
| `transport` | 通訊傳輸：`stdio`（預設）或 `socket` |
| `env` | 啟動 server 時要設定的環境變數 |
| `initializationOptions` | 在初始化期間傳遞給 server 的選項 |
| `settings` | 透過 `workspace/didChangeConfiguration` 傳遞的設定 |
| `workspaceFolder` | server 的工作區資料夾路徑 |
| `startupTimeout` | 等待 server 啟動的最長時間（毫秒） |
| `shutdownTimeout` | 等待正常關閉的最長時間（毫秒） |
| `restartOnCrash` | server 崩潰後是否重新啟動。預設為 `true` |
| `maxRestarts` | 放棄前的最大重新啟動嘗試次數 |
| `diagnostics` | 是否在編輯後將診斷推送到 Claude 的上下文中（預設 `true`） |

> `restartOnCrash` 和 `shutdownTimeout` 需要 Claude Code v2.1.205+。
> 在 v2.1.205 之前，設定架構接受兩個選項，但設定其中任一個會導致 Claude Code 在啟動時完全跳過該 LSP server。

**相同副檔名的多個 servers**：當多個已啟用的 LSP servers 在 `extensionToLanguage` 中宣告相同的檔案副檔名時，無論 servers 來自一個 plugin 還是來自不同的 plugins，**第一個註冊的 server 會處理具有該副檔名的檔案**，其他的永遠不會啟動。`/plugin` 介面會顯示一個警告命名其 server 為作用中的 plugin。

**無法初始化的 Servers**：Claude Code 會跳過設定無效的 server，例如缺少 `command` 或 `extensionToLanguage` 的 server，其他已設定的 servers 仍會啟動。執行 `claude --debug` 以查看為什麼 server 被跳過。

> ⚠️ **您必須單獨安裝語言伺服器二進位檔**。LSP plugins 設定 Claude Code 如何連接到語言伺服器，但它們不包括伺服器本身。如果您在 `/plugin` Errors 標籤中看到 `Executable not found in $PATH`，請為您的語言安裝所需的二進位檔。

**可用的 LSP plugins**：

| Plugin | 語言伺服器 | 安裝命令 |
|:-------|:----------|:---------|
| `pyright-lsp` | Pyright (Python) | `pip install pyright` 或 `npm install -g pyright` |
| `typescript-lsp` | TypeScript Language Server | `npm install -g typescript-language-server typescript` |
| `rust-analyzer-lsp` | rust-analyzer | [rust-analyzer 安裝](https://rust-analyzer.github.io/manual.html#installation) |

---

### Monitors

Plugins 可以宣告背景 monitors，Claude Code 在 plugin 啟用時自動啟動。每個 monitor 執行一個 shell 命令，持續整個工作階段，並將每個 stdout 行傳遞給 Claude 作為通知。

> Plugin monitors 使用與 [Monitor tool](https://code.claude.com/docs/zh-TW/tools-reference#monitor-tool) 相同的機制。它們僅在互動式 CLI 工作階段中執行，並在 Monitor tool 不可用的主機上被跳過。

**位置**：`monitors/monitors.json` 在 plugin 根目錄，或在 `plugin.json` 中內聯

**格式**：monitor 項目的 JSON 陣列

```json
[
  {
    "name": "deploy-status",
    "command": "\"${CLAUDE_PLUGIN_ROOT}\"/scripts/poll-deploy.sh",
    "description": "Deployment status changes"
  },
  {
    "name": "error-log",
    "command": "tail -F ./logs/error.log",
    "description": "Application error log",
    "when": "on-skill-invoke:debug"
  }
]
```

> 若要內聯宣告 monitors，請將 `plugin.json` 中的 `experimental.monitors` 設定為相同的陣列。

**必需欄位**：

| 欄位 | 描述 |
|:-----|:-----|
| `name` | 在 plugin 中唯一的識別碼。防止 plugin 重新載入或再次叫用 skill 時出現重複程序 |
| `command` | 在工作階段工作目錄中作為持久背景程序執行的 shell 命令 |
| `description` | 正在監視的內容的簡短摘要。顯示在任務面板和通知摘要中 |

**選用欄位**：

| 欄位 | 描述 |
|:-----|:-----|
| `when` | 控制 monitor 何時啟動。`"always"`（預設）或 `"on-skill-invoke: <skill>"` |

> `command` 值支援 [path substitutions](#環境變數) `${CLAUDE_PLUGIN_ROOT}`、`${CLAUDE_PLUGIN_DATA}` 和 `${CLAUDE_PROJECT_DIR}`，加上環境中的任何 `${ENV_VAR}`。

> ⚠️ Monitor `command` **無法參考 `${user_config.*}` 值**。Monitor 程序不會接收 `CLAUDE_PLUGIN_OPTION_<KEY>` 環境變數。

---

### Themes

Plugins 可以提供顏色主題，這些主題與內建預設值和使用者的本機主題一起出現在 `/theme` 中。主題是 `themes/` 中的 JSON 檔案。

> Themes 是 [experimental component](#experimental-components)。

```json
{
  "name": "Dracula",
  "base": "dark",
  "overrides": {
    "claude": "#bd93f9",
    "error": "#ff5555",
    "success": "#50fa7b"
  }
}
```

> 選擇 plugin 主題會在使用者的設定中保留 `custom::<theme>`。Plugin 主題是唯讀的；在 `/theme` 中按 `Ctrl+E` 會將其複製到 `~/.claude/themes/`，以便使用者可以編輯副本。

---

## Plugin 安裝範圍

安裝 plugin 時，你選擇一個**範圍**，決定 plugin 的可用位置和誰可以使用它：

| 範圍 | 設定檔 | 使用案例 |
|:-----|:-------|:---------|
| `user` | `~/.claude/settings.json` | 個人 plugins 可跨所有專案使用（預設） |
| `project` | `.claude/settings.json` | 團隊 plugins 透過版本控制共享 |
| `local` | `.claude/settings.local.json` | 專案特定 plugins，gitignored |
| `managed` | [Managed settings](https://code.claude.com/docs/zh-TW/settings#settings-files) | 受管的 plugins（唯讀，僅更新） |

> Plugins 使用與其他 Claude Code 設定相同的範圍系統。

---

## Skills 目錄 Plugins

任何 skills 目錄下包含 `.claude-plugin/plugin.json` manifest 的資料夾都會在下一個工作階段中**自動**作為名為 `<name>@skills-dir` 的 plugin 載入，**無需 marketplace 和無需安裝步驟**。

使用 [`plugin init`](#plugin-init) 進行搭建。與 marketplace 安裝不同，**plugin 是在原地發現的**，而不是複製到 plugin 快取中。

### Skills 目錄樹支援三種東西

| 您擁有的內容 | 它是什麼 |
|:-------------|:---------|
| `~/.claude/skills/foo/SKILL.md`，沒有 manifest | 一個名為 `foo` 的純 [skill](./04-skills.md) |
| `~/.claude/skills/foo/.claude-plugin/plugin.json` | 一個 plugin `foo@skills-dir`，可以捆綁自己的 skills、agents、hooks 等 |
| `~/.claude/skills/bar/SKILL.md` | 一個 skill `bar`，打包在 plugin 內 |

### 選擇 plugin 載入的位置

| Skills 目錄 | 範圍 | 載入 |
|:-----------|:-----|:------|
| `~/.claude/skills/` | personal | 在每個專案中（位置只屬於您） |
| `<project>/.claude/skills/` | project | 僅在您接受該資料夾的工作區 [trust dialog](https://code.claude.com/docs/zh-TW/settings) 後 |

**專案範圍的 plugin 被簽入存放庫**，並到達克隆它的每個協作者。

> 因為該內容來自存放庫而不是來自您，它只在與 `.claude/settings.json` 相同的信任閘道後載入：
> - 它宣告的 MCP servers 會經過與專案 `.mcp.json` 相同的 [per-server approval](https://code.claude.com/docs/zh-TW/mcp)
> - LSP servers 只有在您信任工作區後才會啟動
> - [Background monitors](#monitors) **不會載入**

> 📌 **專案範圍的 `@skills-dir` plugins 只從您啟動 Claude Code 的目錄的 `.claude/skills/` 載入**。它們不會[向上走到儲存庫根目錄](https://code.claude.com/docs/zh-TW/skills#automatic-discovery-from-parent-and-nested-directories)，所以從子目錄啟動會錯過位於存放庫根目錄的 plugin。
> 從存放庫根目錄啟動，或在變更目錄後執行 `/reload-plugins`。

### 編輯、重新載入和停用 skills 目錄 plugin

- 對 skill 的 `SKILL.md` 所做的變更**會立即在目前工作階段中生效**
- 對 plugin 的其他元件（`hooks/`、`.mcp.json`、`agents/` 和 `output-styles/`）的變更**不會**。執行 `/reload-plugins` 或重新啟動 Claude Code
- 若要停止載入 skills 目錄 plugin，**刪除其資料夾**或按名稱停用它

```bash
claude plugin disable my-tool@skills-dir
```

> 沒有 `uninstall` 步驟，因為沒有從 marketplace 安裝任何內容。

---

## Plugin manifest 完整架構

`.claude-plugin/plugin.json` 檔案定義你的 plugin 的中繼資料和設定。

> Manifest 是**選用**的。如果省略，Claude Code 自動探索[預設位置](#檔案位置參考)中的元件，並從目錄名稱衍生 plugin 名稱。使用 manifest 當你需要提供中繼資料或自訂元件路徑時。

### 完整架構

```json
{
  "name": "plugin-name",
  "displayName": "Plugin Name",
  "version": "1.2.0",
  "description": "Brief plugin description",
  "author": {
    "name": "Author Name",
    "email": "author@example.com",
    "url": "https://github.com/author"
  },
  "homepage": "https://docs.example.com/plugin",
  "repository": "https://github.com/author/plugin",
  "license": "MIT",
  "keywords": ["keyword1", "keyword2"],
  "skills": "./custom/skills/",
  "commands": ["./custom/commands/special.md"],
  "agents": ["./custom/agents/reviewer.md"],
  "hooks": "./config/hooks.json",
  "mcpServers": "./mcp-config.json",
  "outputStyles": "./styles/",
  "lspServers": "./.lsp.json",
  "experimental": {
    "themes": "./themes/",
    "monitors": "./monitors.json"
  },
  "dependencies": [
    "helper-lib",
    { "name": "secrets-vault", "version": "~2.1.0" }
  ]
}
```

### 必需欄位

如果您包含 manifest，`name` 是**唯一必需的欄位**。

| 欄位 | 類型 | 描述 | 範例 |
|:-----|:-----|:-----|:-----|
| `name` | string | 唯一識別碼（kebab-case，無空格）。當 marketplace 項目以不同名稱列出 plugin 時，marketplace 項目名稱是 `enabledPlugins` 金鑰和 `/plugin` 使用的名稱 | `"deployment-tools"` |

> 此名稱用於命名空間元件。例如，名稱為 `plugin-dev` 的 plugin 中，agent `agent-creator` 在 UI 中顯示為 `plugin-dev:agent-creator`。

### 無法識別的欄位

Claude Code 忽略它無法識別的頂層欄位。**您可以在 `plugin.json` 中保留來自另一個生態系統的中繼資料**，plugin 仍會載入。這使得維護一個 manifest 作為 VS Code 或 Cursor 擴充功能 manifest、npm `package.json` 或 MCPB/DXT bundle manifest 變得實用。

> `claude plugin validate` 將無法識別的欄位報告為**警告**，不是錯誤。
> 只有無法識別欄位警告的 plugin 仍會通過驗證並在執行時載入。

類型錯誤的欄位仍會失敗。例如，`keywords` 值是字串而不是陣列是載入錯誤。

傳遞 `--strict` 以將警告視為錯誤。在 CI 中使用它來捕捉拼寫錯誤的欄位名稱。

```bash
claude plugin validate ./my-plugin --strict
```

### 中繼資料欄位

| 欄位 | 類型 | 描述 | 範例 |
|:-----|:-----|:-----|:-----|
| `$schema` | string | JSON Schema URL，用於編輯器自動完成和驗證。Claude Code 在載入時忽略 | `"https://json.schemastore.org/claude-code-plugin-manifest.json"` |
| `displayName` | string | 在 `/plugin` 選擇器中顯示的人類可讀名稱。當省略時回退到 `name`。可含空格 | `"Deployment Tools"` |
| `version` | string | 語義版本。設定此項會將 plugin 固定到該版本字串 | `"2.1.0"` |
| `description` | string | plugin 用途的簡短說明 | `"Deployment automation tools"` |
| `author` | object | 作者資訊 | `{"name": "Dev Team", "email": "dev@company.com"}` |
| `homepage` | string | 文件 URL | `"https://docs.example.com"` |
| `repository` | string | 原始程式碼 URL | `"https://github.com/user/plugin"` |
| `license` | string | 授權識別碼 | `"MIT"`、`"Apache-2.0"` |
| `keywords` | array | 探索標籤 | `["deployment", "ci-cd"]` |
| `defaultEnabled` | boolean | 當使用者未設定時，plugin 是否以啟用狀態啟動。預設為 `true` | `false` |

### 預設啟用

在 `plugin.json` 中設定 `defaultEnabled: false` 以提供**安裝時停用**的 plugin。使用者使用 `claude plugin enable <name>` 或 `/plugin` 介面將其開啟。對於新增成本或使用者應選擇加入的範圍的 plugins 使用此方法（例如連接到外部服務的 plugin）。

> 需要 Claude Code v2.1.154+。較早的版本會忽略該欄位並在安裝時啟用 plugin。

`defaultEnabled` 是當**沒有其他因素決定** plugin 狀態時的後備。兩件事優先於它：

- **使用者的設定**：在任何設定範圍的 `enabledPlugins` 中為 plugin 的項目
- **相依性要求**：當 plugin 被另一個啟用的 plugin 所需時，Claude Code 會在安裝或啟用時為其寫入 `true`

### 元件路徑欄位

| 欄位 | 類型 | 描述 | 範例 |
|:-----|:-----|:-----|:-----|
| `skills` | string\|array | 包含 `<name>/SKILL.md` 的自訂 skill 目錄。新增到預設 `skills/` 掃描 | `"./custom/skills/"` |
| `commands` | string\|array | 自訂平面 `.md` skill 檔案或目錄（取代預設 `commands/`） | `"./custom/cmd.md"` |
| `agents` | string\|array | 自訂 agent 檔案（取代預設 `agents/`） | `"./custom/agents/reviewer.md"` |
| `hooks` | string\|array\|object | Hook 設定路徑或內聯設定 | `"./my-extra-hooks.json"` |
| `mcpServers` | string\|array\|object | MCP 設定路徑或內聯設定 | `"./my-extra-mcp-config.json"` |
| `outputStyles` | string\|array | 自訂輸出樣式檔案/目錄（取代預設 `output-styles/`） | `"./styles/"` |
| `lspServers` | string\|array\|object | LSP 設定 | `"./.lsp.json"` |
| `experimental.themes` | string\|array | 色彩主題檔案/目錄（取代預設 `themes/`） | `"./themes/"` |
| `experimental.monitors` | string\|array | 背景 monitor 設定 | `"./monitors.json"` |
| `userConfig` | object | 在啟用時提示使用者的使用者可設定值 | 見下方 |
| `channels` | array | 訊息注入的頻道宣告 | 見下方 |
| `dependencies` | array | 此 plugin 需要的其他 plugins，可選擇使用 semver 版本限制 | `[{ "name": "secrets-vault", "version": "~2.1.0" }]` |

### 實驗性元件

`experimental` 金鑰下的元件 `themes` 和 `monitors` 具有在版本之間穩定時可能會變更的 manifest 架構。您宣告它們的位置是一個單獨的遷移：頂層仍然有效，`claude plugin validate` 會發出警告，未來的版本將需要 `experimental.*`。

### 使用者設定（userConfig）

`userConfig` 欄位宣告 Claude Code 在啟用 plugin 時提示使用者的值。使用此方法而不是要求使用者手動編輯 `settings.json`。

```json
{
  "userConfig": {
    "api_endpoint": {
      "type": "string",
      "title": "API endpoint",
      "description": "Your team's API endpoint"
    },
    "api_token": {
      "type": "string",
      "title": "API token",
      "description": "API authentication token",
      "sensitive": true
    }
  }
}
```

| 欄位 | 必需 | 描述 |
|:-----|:-----|:-----|
| `type` | ✅ | `string`、`number`、`boolean`、`directory` 或 `file` |
| `title` | ✅ | 設定對話方塊中顯示的標籤 |
| `description` | ✅ | 欄位下方顯示的說明文字 |
| `sensitive` | ❌ | 如果 `true`，遮罩輸入並將值儲存在安全儲存體中 |
| `required` | ❌ | 如果 `true`，當欄位為空時驗證失敗 |
| `default` | ❌ | 使用者未提供任何內容時使用的值 |
| `multiple` | ❌ | 對於 `string` 類型，允許字串陣列 |
| `min` / `max` | ❌ | `number` 類型的界限 |

每個值都可用於在 MCP 和 LSP server 設定和 hook 命令中替換為 `${user_config.KEY}`。所有值都會匯出到 hook 程序作為 `CLAUDE_PLUGIN_OPTION_<KEY>` 環境變數，其中 `<KEY>` 是選項金鑰大寫。

> ⚠️ 在 shell 中執行的欄位**拒絕 `${user_config.*}`**：將設定的值替換到 shell 命令中會讓 shell 執行該值包含的任何內容，所以元件會失敗並出現錯誤。

**敏感值儲存位置**：
- **非敏感值**：在 `settings.json` 中的 [`pluginConfigs`](https://code.claude.com/docs/zh-TW/settings#pluginconfigs) 金鑰下
- **敏感值**：macOS Keychain，或在沒有支援的 keychain 可用的平台上 `~/.claude/.credentials.json`

### 路徑行為規則

自訂路徑是否取代或擴展 plugin 的預設目錄取決於欄位：

- **取代預設值**：`commands`、`agents`、`outputStyles`、`experimental.themes`、`experimental.monitors`
- **新增到預設值**：`skills`。預設 `skills/` 目錄始終被掃描
- **自有合併規則**：[hooks](#hooks)、[MCP servers](#mcp-servers) 和 [LSP servers](#lsp-servers)

對於所有路徑欄位：
- 所有路徑必須相對於 plugin 根目錄，並以 `./` 開頭
- 來自自訂路徑的元件使用相同的命名和命名空間規則
- 可以將多個路徑指定為陣列

### 環境變數

Claude Code 提供三個變數用於參考路徑：

| 變數 | 解析為 | 用途 |
|:-----|:-------|:-----|
| `${CLAUDE_PLUGIN_ROOT}` | plugin 安裝目錄的絕對路徑 | 與 plugin 捆綁的指令碼、二進位檔和設定檔 |
| `${CLAUDE_PLUGIN_DATA}` | 持久目錄（首次參考時建立，在 plugin 更新後保留） | 已安裝的依賴項，例如 `node_modules` 或 Python 虛擬環境 |
| `${CLAUDE_PROJECT_DIR}` | 專案根目錄 | 專案本地指令碼和設定檔 |

所有三個都會匯出為環境變數到 hook 程序和 MCP 及 LSP server 子程序。

| Plugin 元件 | 佔位符解析的欄位 |
|:-----------|:-----------------|
| Skill 和 agent 內容 | 佔位符出現的任何地方 |
| Hook 和 monitor 命令 | 佔位符出現的任何地方 |
| MCP `stdio` servers | `command`、`args`、`env` |
| MCP `http`、`sse`、`ws` servers | `url`、`headers`、`headersHelper` |
| LSP servers | `command`、`args`、`env`、`workspaceFolder` |

#### 持久資料目錄

`${CLAUDE_PLUGIN_DATA}` 目錄解析為 `~/.claude/plugins/data/{id}/`，其中 `{id}` 是 plugin 識別碼，其中 `a-z`、`A-Z`、`0-9`、`_` 和 `-` 以外的字元被替換為 `-`。

> 當你從最後一個安裝 plugin 的範圍卸載 plugin 時，資料目錄會自動刪除。`/plugin` 介面顯示目錄大小並在刪除前提示。CLI 預設刪除；傳遞 [`--keep-data`](#plugin-uninstall) 以保留它。

---

## Plugin 快取與檔案解析

Plugins 可以透過以下兩種方式之一指定：

- 透過 `claude --plugin-dir` 或 `claude --plugin-url`，在工作階段期間
- 透過 marketplace，為未來的工作階段安裝

出於安全性和驗證目的，Claude Code 將 *marketplace* plugins **複製到使用者的本機 plugin 快取**（`~/.claude/plugins/cache`），而不是就地使用它們。

每個已安裝的版本是快取中的單獨目錄，按 marketplace 和 plugin 分組，並以解析的版本命名。

當你更新或卸載 plugin 時，Claude Code 會將先前的版本目錄標記為孤立，並在 **14 天後**的背景下掃描中將其移除。

> Claude Code 僅在至少安裝了一個 plugin 時才運行掃描；卸載最後一個 plugin 後，孤立目錄會保留在磁碟上，直到再次安裝 plugin。
>
> Claude 的 Glob 和 Grep 工具在搜尋期間會跳過孤立的版本目錄，因此檔案結果不包含過時的 plugin 程式碼。

### 路徑遍歷限制

> ⚠️ **已安裝的 plugins 無法參考其目錄外的檔案**。遍歷 plugin 根目錄外的路徑（例如 `../shared-utils`）在安裝後將無法運作，因為這些外部檔案不會被複製到快取中。

### 使用 Symlinks 在 Marketplace 內共享檔案

如果你的 plugin 需要與同一 marketplace 的其他部分共享檔案，你可以在 plugin 目錄內建立符號連結。當 plugin 被複製到快取時，symlink 的處理方式取決於其目標的解析位置：

- **在 plugin 自身目錄內**：symlink 在快取中被保留為相對 symlink
- **在同一 marketplace 內的其他位置**：symlink 被取消參考。目標的內容被複製到快取中以取代它
- **在 marketplace 外**：symlink **因安全考量而被跳過**

```bash
# 在 macOS/Linux 上
ln -s ../../shared-plugin/skills/foo ./skills/foo

# 在 Windows 上（從提升的命令提示字元使用 `mklink /D`）
mklink /D .\skills\foo ..\..\shared-plugin\skills\foo
```

> 對於使用 `--plugin-dir` 安裝或從本機路徑安裝的 plugins，**只有解析在 plugin 自身目錄內的 symlinks 被保留**。所有其他的都被跳過。

---

## Plugin 目錄結構

### 標準 Plugin 配置

完整的 plugin 遵循此結構：

```text
enterprise-plugin/
├── .claude-plugin/           # Metadata directory (optional)
│   └── plugin.json             # plugin manifest
├── skills/                   # Skills
│   ├── code-reviewer/
│   │   └── SKILL.md
│   └── pdf-processor/
│       ├── SKILL.md
│       └── scripts/
├── commands/                 # Skills as flat .md files
│   ├── status.md
│   └── logs.md
├── agents/                   # Subagent definitions
│   ├── security-reviewer.md
│   ├── performance-tester.md
│   └── compliance-checker.md
├── output-styles/            # Output style definitions
│   └── terse.md
├── themes/                   # Color theme definitions
│   └── dracula.json
├── monitors/                 # Background monitor configurations
│   └── monitors.json
├── hooks/                    # Hook configurations
│   ├── hooks.json           # Main hook config
│   └── security-hooks.json  # Additional hooks
├── bin/                      # Plugin executables added to PATH
│   └── my-tool               # Invokable as bare command in Bash tool
├── settings.json            # Default settings for the plugin
├── .mcp.json                # MCP server definitions
├── .lsp.json                # LSP server configurations
├── scripts/                 # Hook and utility scripts
│   ├── security-scan.sh
│   ├── format-code.py
│   └── deploy.js
├── LICENSE                  # License file
└── CHANGELOG.md             # Version history
```

> ⚠️ `.claude-plugin/` 目錄包含 `plugin.json` 檔案。**所有其他目錄**（commands/、agents/、skills/、output-styles/、themes/、monitors/、hooks/）**必須位於 plugin 根目錄，而不是在 `.claude-plugin/` 內**。

> Plugin 根目錄的 `CLAUDE.md` 檔案**不會作為專案內容載入**。Plugin 透過 skills、agents 和 hooks 貢獻內容，而不是透過 CLAUDE.md。若要提供載入到 Claude 內容中的指示，請將其放在 [skill](#skills) 中。

### 檔案位置參考

| 元件 | 預設位置 | 用途 |
|:-----|:---------|:-----|
| **Manifest** | `.claude-plugin/plugin.json` | Plugin 中繼資料和設定（選用） |
| **Skills** | `skills/` | 具有 `<name>/SKILL.md` 結構的 Skills |
| **Commands** | `commands/` | Skills 作為平面 Markdown 檔案。使用 `skills/` 用於新 plugins |
| **Agents** | `agents/` | Subagent Markdown 檔案 |
| **Output styles** | `output-styles/` | 輸出樣式定義 |
| **Themes** | `themes/` | 色彩主題定義 |
| **Hooks** | `hooks/hooks.json` | Hook 設定 |
| **MCP servers** | `.mcp.json` | MCP server 定義 |
| **LSP servers** | `.lsp.json` | 語言伺服器設定 |
| **Monitors** | `monitors/monitors.json` | 背景 monitor 設定 |
| **Executables** | `bin/` | 新增到 Bash tool 的 `PATH` 的可執行檔 |
| **Settings** | `settings.json` | 啟用 plugin 時套用的預設設定 |

---

## CLI 完整指令參考

Claude Code 提供 CLI 命令用於非互動式 plugin 管理。

### plugin init

在 `~/.claude/skills/<name>/` 搭建新 plugin。在下一個 Claude Code 工作階段中**自動**作為 `<name>@skills-dir` 載入，無需安裝步驟。

```bash
claude plugin init <name> [options]
```

| 選項 | 描述 | 預設 |
|:-----|:-----|:-----|
| `--description <desc>` | Manifest 描述 | |
| `--author <name>` | 作者名稱 | `git config user.name` |
| `--author-email <email>` | 作者電子郵件 | `git config user.email` |
| `--with <components...>` | 同時搭建元件資料夾：`skills`、`agents`、`hooks`、`mcp`、`lsp`、`output-style`、`channel` | |
| `-f, --force` | 覆寫目標的現有 `.claude-plugin/` | |
| `-h, --help` | 顯示命令說明 | |

**別名**：`new`

每個 `--with` 值都會為該元件新增一個入門檔案：

| 元件 | 它搭建什麼 |
|:-----|:---------|
| `skills` | 一個額外的命名空間 `:example` skill |
| `agents` | 一個 `agents/` subagent 定義 |
| `hooks` | 一個 `hooks/hooks.json`，包含範例事件處理程式 |
| `mcp` | 一個 `.mcp.json`，包含 HTTP 和 stdio server 範例 |
| `lsp` | 一個 `.lsp.json` 語言伺服器範例 |
| `output-style` | 一個 `output-styles/.md` |
| `channel` | 一個基於 MCP 的 channel |

**範例**：

```bash
# 搭建最小 plugin
claude plugin init my-helper

# 搭建帶 skill 和 hook 資料夾
claude plugin init my-helper --with skills hooks

# 覆寫現有搭建
claude plugin init my-helper --force
```

---

### plugin install

從可用的 marketplaces 安裝 plugin。

```bash
claude plugin install <plugin> [options]
```

**引數**：Plugin 名稱或 `plugin-name@marketplace-name` 用於特定 marketplace

| 選項 | 描述 | 預設 |
|:-----|:-----|:-----|
| `-s, --scope <scope>` | 安裝範圍：`user`、`project` 或 `local` | `user` |
| `--config <key=value>` | 設定 plugin manifest 中宣告的 `userConfig` 選項 | |
| `-y, --yes` | 接受 `command` source 的 plugin 執行的命令，無需確認提示 | |

**範例**：

```bash
claude plugin install formatter@my-marketplace
claude plugin install formatter@my-marketplace --scope project
claude plugin install formatter@my-marketplace --scope local
```

---

### plugin uninstall

移除已安裝的 plugin。

```bash
claude plugin uninstall <plugin> [options]
```

**別名**：`remove`、`rm`

| 選項 | 描述 | 預設 |
|:-----|:-----|:-----|
| `-s, --scope <scope>` | 從範圍卸載 | `user` |
| `--keep-data` | 保留 plugin 的持久資料目錄 | |
| `--prune` | 同時移除其他 plugin 不需要的自動安裝相依性 | |
| `-y, --yes` | 跳過 `--prune` 確認提示 | |

> 預設情況下，從最後一個剩餘範圍卸載**也會刪除** plugin 的 `${CLAUDE_PLUGIN_DATA}` 目錄。使用 `--keep-data` 保留它。

---

### plugin prune

移除不再被任何已安裝 plugin 所需的自動安裝 plugin 相依性。

```bash
claude plugin prune [options]
```

**別名**：`autoremove`

| 選項 | 描述 | 預設 |
|:-----|:-----|:-----|
| `-s, --scope <scope>` | 在範圍進行修剪 | `user` |
| `--dry-run` | 列出將被移除的內容而不實際移除 | |
| `-y, --yes` | 跳過確認提示 | |

> 該命令列出孤立的相依性並在移除前要求確認。
> 若要在一個步驟中移除 plugin 並清理其相依性，執行 `claude plugin uninstall --prune`。

---

### plugin enable

啟用已停用的 plugin。如果 plugin 宣告 [dependencies](#dependencies)，Claude Code 會在相同範圍內以傳遞方式啟用它們。

```bash
claude plugin enable <plugin> [options]
```

| 選項 | 描述 | 預設 |
|:-----|:-----|:-----|
| `-s, --scope <scope>` | 要啟用的範圍 | 自動偵測 |

---

### plugin disable

停用 plugin 而不卸載它。當另一個已啟用的 plugin [depends on](https://code.claude.com/docs/zh-TW/plugin-dependencies#enable-or-disable-a-plugin-with-dependencies) 目標時失敗。

```bash
claude plugin disable [plugin] [options]
```

| 選項 | 描述 | 預設 |
|:-----|:-----|:-----|
| `-a, --all` | 停用所有已啟用的 plugins | |
| `-s, --scope <scope>` | 要停用的範圍 | 自動偵測 |

---

### plugin update

將 plugin 更新到最新版本。

```bash
claude plugin update <plugin> [options]
```

| 選項 | 描述 | 預設 |
|:-----|:-----|:-----|
| `-s, --scope <scope>` | 要更新的範圍 | `user` |
| `-y, --yes` | 接受 `command` source 的命令 | |

---

### plugin list

列出已安裝的 plugins 及其版本、來源 marketplace 和啟用狀態。

```bash
claude plugin list [options]
```

| 選項 | 描述 |
|:-----|:-----|
| `--json` | 輸出為 JSON |
| `--available` | 包含來自 marketplaces 的可用 plugins。需要 `--json` |

---

### plugin details

顯示 plugin 的元件清單和預計的 token 成本。

```bash
claude plugin details <name>
```

**範例輸出**：

```
dependency-guard 1.2.0
  Dependency analysis for Claude Code sessions
  Source: dependency-guard@example-marketplace

Component inventory
  Skills (2)  scan-dependencies, review-changes
  Agents (0)
  Hooks (1)  (harness-only — no model context cost)
  MCP servers (0)
  LSP servers (0)

Projected token cost
  Always-on:   ~180 tok   added to every session

Per-component (rounded)
  component            always-on  on-invoke
  scan-dependencies        ~100      ~2400
  review-changes            ~80      ~1800
```

> **always-on** 總計是透過作用中模型的 `count_tokens` API 計算的。按元件的數字按比例從該總計縮放。
> **on-invoke** 成本在每次 skill 或 agent 觸發時支付。

---

### plugin tag

為 plugin 建立發行版 git 標籤。

```bash
claude plugin tag [path] [options]
```

| 選項 | 描述 | 預設 |
|:-----|:-----|:-----|
| `--push` | 建立標籤後將其推送到遠端 | |
| `--dry-run` | 列印將被標籤的內容而不建立標籤 | |
| `-f, --force` | 即使工作樹髒污或標籤已存在也建立標籤 | |
| `-m, --message <msg>` | 標籤註解訊息。使用 `%s` 作為版本的佔位符 | |
| `--remote <name>` | 使用 `--push` 時推送到的遠端 | `origin` |

---

## 偵錯與開發工具

### 偵錯命令

使用 `claude --debug` 看到 plugin 載入詳細資訊：

```bash
claude --debug
```

這會顯示：
- 正在載入哪些 plugins
- Plugin manifests 中的任何錯誤
- Skill、agent 和 hook 註冊
- MCP server 初始化

### 常見問題

| 問題 | 原因 | 解決方案 |
|:-----|:-----|:---------|
| Plugin 未載入 | 無效的 `plugin.json` | 執行 `claude plugin validate` 或 `/plugin validate` 檢查 |
| Skills 未出現 | 目錄結構錯誤 | 確保 `skills/` 在 plugin 根目錄，不在 `.claude-plugin/` 內 |
| Hooks 未觸發 | 指令碼不可執行 | 執行 `chmod +x script.sh` |
| MCP server 失敗 | 缺少 `${CLAUDE_PLUGIN_ROOT}` | 對所有 plugin 路徑使用變數 |
| 路徑錯誤 | 絕對路徑 | 改為相對路徑，以 `./` 開頭 |
| LSP `Executable not found in $PATH` | 語言伺服器未安裝 | 安裝二進位檔 |

### 範例錯誤訊息

**Manifest 驗證錯誤**：
- `Invalid JSON syntax: Unexpected token } in JSON at position 142`
- `Plugin has an invalid manifest file at .claude-plugin/plugin.json. Validation errors: name: Required`
- `Plugin has a corrupt manifest file at .claude-plugin/plugin.json. JSON parse error: ...`

**Plugin 載入錯誤**：
- `Warning: No commands found in plugin my-plugin custom directory: ./cmds.`
- `Plugin directory not found at path: ./plugins/my-plugin. Check that the marketplace entry has the correct path.`
- `Plugin my-plugin has conflicting manifests: both plugin.json and marketplace entry specify components.`

### Hook 疑難排解

**Hook 指令碼未執行**：
1. 檢查指令碼是否可執行：`chmod +x ./scripts/your-script.sh`
2. 驗證 shebang 行：`#!/bin/bash` 或 `#!/usr/bin/env bash`
3. 檢查路徑使用 `${CLAUDE_PLUGIN_ROOT}`
4. 手動測試：`./scripts/your-script.sh`

**Hook 未觸發**：
1. 驗證事件名稱（區分大小寫）：`PostToolUse`，不是 `postToolUse`
2. 檢查 matcher 模式：`"matcher": "Write|Edit"` 用於檔案操作
3. 確認 hook 類型有效：`command`、`http`、`mcp_tool`、`prompt` 或 `agent`

### MCP Server 疑難排解

**Server 未啟動**：
1. 檢查命令存在且可執行
2. 驗證所有路徑使用 `${CLAUDE_PLUGIN_ROOT}` 變數
3. 檢查 `claude --debug` 輸出
4. 在 Claude Code 外手動測試 server

### 目錄結構錯誤

**症狀**：Plugin 載入但元件（skills、agents、hooks）遺失。

**正確結構**：元件必須位於 plugin 根目錄，不在 `.claude-plugin/` 內。

```text
my-plugin/
├── .claude-plugin/
│   └── plugin.json      ← Only manifest here
├── commands/            ← At root level
├── agents/              ← At root level
└── hooks/               ← At root level
```

如果您的元件在 `.claude-plugin/` 內，將它們移到 plugin 根目錄。

---

## 發佈與版本控制

### 版本管理

Claude Code 使用 plugin 的版本作為快取金鑰，決定是否有可用的更新。

Claude Code 從以下**第一個設定的項目**解析 plugin 的版本：

1. Plugin 的 `plugin.json` 中的 `version` 欄位
2. Plugin 在 `marketplace.json` 中的 marketplace 項目中的 `version` 欄位
3. Plugin 來源的 git commit SHA，適用於 git 託管 marketplace 中的 `github`、`url`、`git-subdir` 和相對路徑來源
4. `unknown`，適用於 `npm` 來源或不在 git 儲存庫內的本機目錄

| 方法 | 如何操作 | 更新行為 | 最適合 |
|:-----|:---------|:---------|:-------|
| **明確版本** | 在 `plugin.json` 中設定 `"version": "2.1.0"` | 使用者只有在您提升此欄位時才會獲得更新 | 具有穩定發行週期的已發佈 plugin |
| **Commit-SHA 版本** | 從 `plugin.json` 和 marketplace 項目中省略 `version` | 使用者在每次 plugin 的 git 來源有新 commit 時都會獲得更新 | 正在積極開發中的內部或團隊 plugin |

> 如果您在 `plugin.json` 中設定 `version`，每次您想讓使用者接收變更時，都必須提升它。僅推送新的 commit 是不夠的，因為 Claude Code 會看到相同的版本字串並保留快取副本。

如果您使用明確版本，請遵循 [semantic versioning](https://semver.org)（`MAJOR.MINOR.PATCH`）：針對破壞性變更提升 MAJOR，針對新功能提升 MINOR，針對錯誤修正提升 PATCH。在 `CHANGELOG.md` 中記錄變更。

---

## 參考資源

- [Plugins 指南](./02-plugins.md)：教學和實際使用
- [Plugin marketplaces](./01-plugin-marketplaces.md)：建立和管理 marketplaces
- [Skills](./04-skills.md)：Skill 開發詳細資訊
- [Subagents](./05-subagents.md)：Agent 設定和功能
- [Hooks](./06-hooks.md)：事件處理和自動化
- [MCP](https://code.claude.com/docs/zh-TW/mcp)：外部工具整合
- [Settings](https://code.claude.com/docs/zh-TW/settings)：Plugins 的設定選項
