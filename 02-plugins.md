# Plugin 開發指南（從零建立你的第一個 Plugin）

> 📖 **系列**：Claude Code Plugin 完整學習系列 #02
> 🌐 **原文**：[code.claude.com/docs/zh-TW/plugins](https://code.claude.com/docs/zh-TW/plugins)
> 📅 **整理日期**：2026 / 01
> 🎯 **適用版本**：Claude Code v2.1.x

> 💡 **本系列總覽**：見 [00-claude-code-plugins-series.md](./00-claude-code-plugins-series.md)
> 📚 **上一篇**：[01-plugin-marketplaces.md](./01-plugin-marketplaces.md)（Plugin Marketplaces）
> 📚 **下一篇**：[03-plugins-reference.md](./03-plugins-reference.md)（Plugin 技術參考）

## 目錄

1. [Plugin vs 獨立配置：何時該用 Plugin](#plugin-vs-獨立配置何時該用-plugin)
2. [快速開始：第一個 Plugin](#快速開始第一個-plugin)
3. [Plugin 結構概述](#plugin-結構概述)
4. [開發更複雜的 Plugin](#開發更複雜的-plugins)
5. [本地測試你的 Plugin](#本地測試你的-plugin)
6. [偵錯 Plugin 問題](#偵錯-plugin-問題)
7. [共享你的 Plugin](#共享你的-plugin)
8. [將你的 Plugin 提交到官方/社群 Marketplace](#將你的-plugin-提交到官方社群-marketplace)
9. [將現有配置轉換為 Plugin](#將現有配置轉換為-plugin)
10. [下一步](#下一步)

---

## Plugin vs 獨立配置：何時該用 Plugin

Claude Code 支援兩種方式新增自訂 skills、agents 和 hooks：

| 方法 | Skill 名稱 | 最適合 |
|:-----|:----------|:-------|
| **獨立**（`.claude/` 目錄） | `/hello` | 個人工作流程、專案特定的自訂、快速實驗 |
| **Plugins**（包含 manifest 的自包含目錄） | `/plugin-name:hello` | 與隊友共享、分發到社群、版本化發佈、跨專案重複使用 |

### 在以下情況下使用獨立配置

- 你正在為單一專案自訂 Claude Code
- 配置是個人的，不需要共享
- 你在將 skills 或 hooks 打包之前進行實驗
- 你想要簡短的 skill 名稱，例如 `/hello` 或 `/deploy`

### 在以下情況下使用 Plugins

- 你想與你的團隊或社群共享功能
- 你需要在多個專案中使用相同的 skills/agents
- 你想要版本控制和輕鬆更新你的擴展
- 你正在透過市場進行分發
- 你可以接受**命名空間化**的 skills，例如 `/my-plugin:hello`（命名空間可防止 plugins 之間的衝突）

> 💡 **建議**：在 `.claude/` 中從獨立配置開始進行快速迭代，然後在準備好共享時[轉換為 plugin](#將現有配置轉換為-plugin)。

---

## 快速開始：第一個 Plugin

這個快速入門將引導你建立具有自訂 skill 的 plugin。

### 先決條件

- Claude Code [已安裝並驗證](https://code.claude.com/docs/zh-TW/quickstart#step-1-install-claude-code)
- 如果你沒有看到 `/plugin` 命令，將 Claude Code 更新到最新版本

### 建立你的第一個 Plugin

每個 plugin 都位於其自己的目錄中。位置對於本快速入門並不重要。

#### Step 1：建立目錄

```bash
mkdir my-first-plugin
```

#### Step 2：建立 manifest

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
| `name` | 唯一識別碼和 skill 命名空間。Skills 以前綴為名（如 `/my-first-plugin:hello`） |
| `description` | 在 plugin 管理器中顯示 |
| `version` | 選用。如果設定，使用者只會在你更新此欄位時收到更新 |
| `author` | 選用。有助於歸屬 |

> 💡 **關於 `version`**：如果省略且你的 plugin 透過 git 分發，則使用 commit SHA，每個 commit 都算作新版本。詳見[版本管理](./03-plugins-reference.md#version-management)。

#### Step 3：建立 skill

每個 skill 是一個包含 `SKILL.md` 檔案的資料夾。資料夾名稱成為 skill 名稱。

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

#### Step 4：使用 `--plugin-dir` 旗標測試

```bash
claude --plugin-dir ./my-first-plugin
```

#### Step 5：嘗試你的新 skill

```bash
/my-first-plugin:hello
```

Claude 會以問候語回應。執行 `/help` 會看到你的 skill 列在 plugin 命名空間下。

> 📌 **為什麼要命名空間？** Plugin skills 始終被命名空間化（如 `/my-first-plugin:hello`），以防止多個 plugins 具有相同名稱的 skills 時發生衝突。

#### Step 6：使你的 skill 動態化

`$ARGUMENTS` 佔位符會擷取使用者在 skill 名稱後提供的任何文字。

更新 `SKILL.md`：

```markdown
---
description: Greet the user with a personalized message
---

# Hello Skill

Greet the user named "$ARGUMENTS" warmly and ask how you can help them today. Make the greeting personal and encouraging.
```

執行 `/reload-plugins` 然後測試：

```bash
/my-first-plugin:hello Alex
```

### 你已成功建立的關鍵元件

- **Plugin manifest** (`.claude-plugin/plugin.json`)：描述你的 plugin 的中繼資料
- **Skills 目錄** (`skills/`)：包含你的自訂 skills
- **Skill 引數** (`$ARGUMENTS`)：擷取使用者輸入以實現動態行為

> `--plugin-dir` 旗標對於開發和測試很有用。當你準備好與他人共享你的 plugin 時，請參見[共享你的 Plugin](#共享你的-plugin)。

---

## Plugin 結構概述

你已建立了具有 skill 的 plugin，但 plugins 可以包含更多內容。

### ⚠️ 常見錯誤

> **不要將 `commands/`、`agents/`、`skills/` 或 `hooks/` 放在 `.claude-plugin/` 目錄內。只有 `plugin.json` 應該在 `.claude-plugin/` 內。所有其他目錄必須位於 plugin 根目錄級別。**

> plugin 根目錄是個別 plugin 自己的目錄：包含 `.claude-plugin/plugin.json` 的目錄。它永遠不是 `~/.claude/`。例如，Claude Code 不會讀取放在 `~/.claude/.mcp.json` 的 `.mcp.json`。

### 完整目錄對照

| 目錄 | 位置 | 用途 |
|:-----|:-----|:-----|
| `.claude-plugin/` | Plugin 根目錄 | 包含 `plugin.json` manifest（如果元件使用預設位置，則為選用） |
| `skills/` | Plugin 根目錄 | 作為 `<name>/SKILL.md` 目錄的 Skills |
| `commands/` | Plugin 根目錄 | 作為平面 Markdown 檔案的 Skills。新 plugins 請使用 `skills/` |
| `agents/` | Plugin 根目錄 | 自訂 agent 定義 |
| `hooks/` | Plugin 根目錄 | `hooks.json` 中的事件處理程式 |
| `.mcp.json` | Plugin 根目錄 | MCP server 配置 |
| `.lsp.json` | Plugin 根目錄 | 用於程式碼智慧的 LSP server 配置 |
| `monitors/` | Plugin 根目錄 | `monitors.json` 中的背景監視器配置 |
| `bin/` | Plugin 根目錄 | 啟用 plugin 時新增到 Bash tool 的 `PATH` 的可執行檔 |
| `settings.json` | Plugin 根目錄 | 啟用 plugin 時應用的預設[設定](https://code.claude.com/docs/zh-TW/settings) |

> 只要 plugin 恰好包含一個 skill，就可以直接在 plugin 根目錄放置 `SKILL.md`，而不需要建立 `skills/` 目錄。Claude Code 會將其載入為單一 skill。

---

## 開發更複雜的 Plugins

### 將 Skills 新增到你的 Plugin

在 plugin 根目錄中新增 `skills/` 目錄：

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

> 安裝 plugin 後，執行 `/reload-plugins` 以載入 Skills。

如需完整的 Skill 編寫指南（包括漸進式揭露和工具限制），請參閱 [Skills](./04-skills.md)。

---

### 將 LSP servers 新增到你的 Plugin

> 對於 TypeScript、Python 和 Rust 等常見語言，**請從官方 marketplace 安裝預先建立的 LSP plugins**。只有在需要支援尚未涵蓋的語言時，才建立自訂 LSP plugins。

LSP（Language Server Protocol）plugins 為 Claude 提供即時程式碼智慧。

```json .lsp.json
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

> 安裝 plugin 的使用者必須在其機器上安裝語言伺服器二進位檔。

---

### 將背景監視器新增到你的 Plugin

背景監視器讓你的 plugin 在背景中監視日誌、檔案或外部狀態，並在事件到達時通知 Claude。

`monitors/monitors.json`：

```json
[
  {
    "name": "error-log",
    "command": "tail -F ./logs/error.log",
    "description": "Application error log"
  }
]
```

來自 `command` 的每個 stdout 行都會在工作階段期間作為通知傳遞給 Claude。

---

### 使用你的 Plugin 提供預設設定

Plugin 根目錄中的 `settings.json` 在啟用 plugin 時應用預設配置。**目前只支援 `agent` 和 `subagentStatusLine` 金鑰**。

設定 `agent` 會啟動 plugin 的其中一個[自訂 agents](./05-subagents.md) 作為主執行緒：

```json settings.json
{
  "agent": "security-reviewer"
}
```

> 此範例啟動在 plugin 的 `agents/` 目錄中定義的 `security-reviewer` agent。來自 `settings.json` 的設定優先於在 `plugin.json` 中宣告的 `settings`。

---

### 組織複雜的 Plugins

對於具有許多元件的 plugins，請按功能組織你的目錄結構：

```text
my-plugin/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   ├── code-review/
│   │   └── SKILL.md
│   ├── pdf-processor/
│   │   ├── SKILL.md
│   │   └── scripts/
│   └── test-runner/
│       └── SKILL.md
├── agents/
│   ├── security-reviewer.md
│   └── performance-tester.md
├── hooks/
│   ├── hooks.json
│   └── security-hooks.json
├── scripts/
│   ├── format-code.py
│   └── run-tests.sh
└── README.md
```

---

## 本地測試你的 Plugins

使用 `--plugin-dir` 旗標在開發期間測試 plugins。這會直接載入你的 plugin，無需安裝。

```bash
claude --plugin-dir ./my-plugin
```

### 測試 `.zip` 套件

該旗標也接受 plugin 目錄的 `.zip` 檔案（v2.1.128+）：

```bash
claude --plugin-dir ./my-plugin.zip
```

### 同時載入多個 Plugins

```bash
claude --plugin-dir ./plugin-one --plugin-dir ./plugin-two
```

### 測試已部署的 `.zip`（CI 建置成品）

使用 `--plugin-url` 載入託管在 URL 的 plugin（僅當前 session）：

```bash
claude --plugin-url https://example.com/my-plugin.zip
```

> ⚠️ **信任考量**：與任何 plugin 來源相同：只將此旗標指向你控制或信任的檔案。Claude Code 在啟動時擷取檔案，擷取失敗時會報告 plugin 載入錯誤並在沒有它的情況下啟動。

### 重新載入變更

當你對 plugin 進行變更時，執行 `/reload-plugins` 以取得更新，無需重新啟動：

```
/reload-plugins
```

這會重新載入 plugins、skills、agents、hooks、plugin MCP servers 和 plugin LSP servers。

### 測試你的 Plugin 元件

- **Skills**：使用 `/plugin-name:skill-name`
- **Agents**：檢查是否出現在 `/context` 中的自訂 Agents 下，或透過其範圍名稱 @-提及其中一個
- **Hooks**：驗證是否按預期工作

### 測試覆蓋已安裝 Plugin 的變更

當 `--plugin-dir` plugin 與已安裝的市場 plugin 具有相同名稱時，**本地副本在該工作階段中優先**。這讓你可以測試已安裝的 plugin 的變更，而無需先卸載它。

> 由受管設定強制啟用或強制停用的 plugins 是唯一的例外：`--plugin-dir` 無法覆蓋這些。

---

## 偵錯 Plugin 問題

如果你的 plugin 未按預期工作：

1. **檢查結構**：確保你的目錄位於 plugin 根目錄，而不是在 `.claude-plugin/` 內
2. **個別測試元件**：分別檢查每個 skill、agent 和 hook
3. **使用驗證和偵錯工具**：使用 `claude plugin validate` 或 `/plugin validate` 檢查 `plugin.json`、`hooks/hooks.json`、skill/agent/command frontmatter 的語法和 schema 錯誤

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
| Plugin 未載入 | 無效的 `plugin.json` | 執行 `claude plugin validate` 檢查 |
| Skills 未出現 | 目錄結構錯誤 | 確保 `skills/` 在 plugin 根目錄，不在 `.claude-plugin/` 內 |
| Hooks 未觸發 | 腳本不可執行 | 執行 `chmod +x script.sh` |
| MCP server 失敗 | 缺少 `${CLAUDE_PLUGIN_ROOT}` | 對所有 plugin 路徑使用變數 |
| 路徑錯誤 | 使用了絕對路徑 | 所有路徑必須是相對的，並以 `./` 開頭 |
| LSP `Executable not found in $PATH` | 語言伺服器未安裝 | 安裝二進位檔 |

---

## 共享你的 Plugins

當你的 plugin 準備好共享時：

1. **新增文件**：包含 `README.md`，包含安裝和使用說明
2. **選擇版本控制策略**：決定是否設定明確的 `version` 或依賴 git commit SHA
3. **建立或使用 marketplace**：透過 [plugin marketplaces](./01-plugin-marketplaces.md) 進行分發
4. **與他人測試**：在更廣泛的分發之前讓團隊成員測試 plugin

一旦你的 plugin 在 marketplace 中，其他人可以使用 [探索並安裝 plugins](./07-discover-plugins.md) 中的說明進行安裝。若要將 plugin 保持在你的團隊內部，請在[私人儲存庫](./01-plugin-marketplaces.md#私人儲存庫)中託管 marketplace。

---

## 將你的 Plugin 提交到官方/社群 Marketplace

Anthropic 為 Claude Code plugins 維護兩個公開 marketplace：

### 官方 Marketplace（精選）

- **`claude-plugins-official`**：由 Anthropic 維護的精選 plugins 集合
- 在你第一次以互動方式啟動 Claude Code 時自動註冊
- 在該首次啟動之前執行的非互動式指令碼必須明確新增：
  ```bash
  claude plugin marketplace add anthropics/claude-plugins-official
  ```

### 社群 Marketplace（第三方提交）

- **`claude-community`**：公開社群市場，第三方提交在審查後會進入此市場
- 使用者手動新增：
  ```bash
  /plugin marketplace add anthropics/claude-plugins-community
  ```

### 提交你的 Plugin

若要提交你的 plugin 以進行社群市場審查，使用其中一個應用內提交表單：

- **claude.ai**：[claude.ai/admin-settings/directory/submissions/plugins/new](https://claude.ai/admin-settings/directory/submissions/plugins/new)
- **Console**：[platform.claude.com/plugins/submit](https://platform.claude.com/plugins/submit)

> 📌 **claude.ai 表單**需要 Team 或 Enterprise 組織和目錄管理存取權；組織擁有者預設具有此存取權。
> 不屬於 Team 或 Enterprise 組織的個別作者可以改用 Console 表單。

### 提交前檢查清單

1. **在本地驗證**：`claude plugin validate`
2. **確保完整文件**：`README.md` 包含安裝和使用說明
3. **測試所有元件**：skills、agents、hooks、MCP servers
4. **檢查 marketplace.json**：所有 source 路徑都正確
5. **版本控制**：選擇合適的版本策略

### 審查流程

審查管道在每個提交上執行相同的檢查（與你本地 `claude plugin validate` 相同），以及自動安全篩選。

> 已批准的 plugins 會固定到 [`anthropics/claude-plugins-community`](https://github.com/anthropics/claude-plugins-community) 目錄中的特定 commit SHA。
> 公開目錄每晚從審查管道同步，批准和你的 plugin 出現在 `marketplace.json` 之間可能會有延遲。

### 官方 Marketplace

> 📌 官方 marketplace `claude-plugins-official` 是**單獨策劃**的。Anthropic 根據其自行決定決定要包含哪些 plugins。**沒有應用程序流程**，提交表單不會將 plugins 新增到官方市場。

如果 Anthropic 在官方市場中列出你的 plugin，你的 CLI 可以提示 Claude Code 使用者進行安裝。請參閱 [Recommend your plugin from your CLI](https://code.claude.com/docs/zh-TW/plugin-hints)。

---

## 將現有配置轉換為 Plugin

如果你已經在 `.claude/` 目錄中有 skills 或 hooks，你可以將它們轉換為 plugin，以便更輕鬆地共享和分發。

### 遷移步驟

#### Step 1：建立新目錄

在你的專案根目錄中建立新的 plugin 目錄，與現有的 `.claude/` 資料夾並排放置：

```bash
mkdir -p my-plugin/.claude-plugin
```

#### Step 2：建立 manifest

`my-plugin/.claude-plugin/plugin.json`：

```json
{
  "name": "my-plugin",
  "description": "Migrated from standalone configuration",
  "version": "1.0.0"
}
```

#### Step 3：複製你的配置

```bash
# Copy commands
cp -r .claude/commands my-plugin/

# Copy agents (if any)
cp -r .claude/agents my-plugin/

# Copy skills (if any)
cp -r .claude/skills my-plugin/
```

#### Step 4：處理 hooks

如果你在設定中有 hooks，建立一個 hooks 目錄：

```bash
mkdir my-plugin/hooks
```

使用你的 hooks 配置建立 `my-plugin/hooks/hooks.json`。從你的 `.claude/settings.json` 或 `settings.local.json` 複製 `hooks` 物件，因為格式相同。

命令在 stdin 上接收 hook 輸入作為 JSON，因此使用 `jq` 來提取檔案路徑：

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [{ "type": "command", "command": "jq -r '.tool_input.file_path' | xargs npm run lint:fix" }]
        }
      ]
    ]
  }
}
```

#### Step 5：驗證

載入你的 plugin 以驗證一切正常：

```bash
claude --plugin-dir ./my-plugin
```

測試每個元件：執行你的命令、檢查 agents 是否出現在 `/context` 中，並驗證 hooks 是否正確觸發。

### 遷移時的變更

| 獨立（`.claude/`） | Plugin |
|:------------------|:-------|
| 僅在一個專案中可用 | 可以透過 marketplace 共享 |
| `.claude/commands/` 中的檔案 | `plugin-name/commands/` 中的檔案 |
| `settings.json` 中的 Hooks | `hooks/hooks.json` 中的 Hooks |
| 必須手動複製以共享 | 使用 `/plugin install` 安裝 |

> ⚠️ 遷移後，從 `.claude/` 中移除原始檔案以避免重複。
> 專案和使用者 `.claude/agents/` 定義會覆蓋同名的 plugin agents。
> Plugin skills 會被命名為 `/plugin-name:skill-name`，所以原始的 `/skill-name` 和 plugin 副本都會保持可用。

---

## 下一步

現在你已了解 Claude Code 的 plugin 系統，以下是針對不同目標的建議路徑：

### 對於 plugin 使用者

- [探索和安裝 plugins](./07-discover-plugins.md)：瀏覽市場並安裝 plugins
- [配置團隊市場](./07-discover-plugins.md#配置團隊-marketplace)：為你的團隊設定儲存庫級別的 plugins

### 對於 plugin 開發人員

- [建立和分發市場](./01-plugin-marketplaces.md)：打包和共享你的 plugins
- [Plugins 參考](./03-plugins-reference.md)：完整的技術規格
- 深入探討特定的 plugin 元件：
  - [Skills](./04-skills.md)：skill 開發詳情
  - [Subagents](./05-subagents.md)：agent 配置和功能
  - [Hooks](./06-hooks.md)：事件處理和自動化
  - [MCP](https://code.claude.com/docs/zh-TW/mcp)：外部工具整合
