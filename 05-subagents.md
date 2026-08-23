# Subagents 自訂指南

> 📖 **系列**：Claude Code Plugin 完整學習系列 #05
> 🌐 **原文**：[code.claude.com/docs/en/sub-agents](https://code.claude.com/docs/en/sub-agents)
> 📅 **整理日期**：2026 / 01
> 🎯 **適用版本**：Claude Code v2.1.x

> 💡 **本系列總覽**：見 [00-claude-code-plugins-series.md](./00-claude-code-plugins-series.md)
> 📚 **上一篇**：[04-skills.md](./04-skills.md)（Skills 完整指南）
> 📚 **下一篇**：[06-hooks.md](./06-hooks.md)（Hooks 自動化指南）

## 目錄

1. [什麼是 Subagent](#什麼是-subagent)
2. [內建 Subagents](#內建-subagents)
3. [快速開始：第一個 Subagent](#快速開始第一個-subagent)
4. [配置 Subagents](#配置-subagents)
5. [選擇模型](#選擇模型)
6. [控制 Subagent 能力](#控制-subagent-能力)
7. [可用工具](#可用工具)
8. [範例 Subagents](#範例-subagents)
9. [使用 Subagents](#使用-subagents)
10. [讓 Subagents 生成自己的 Subagents](#讓-subagents-生成自己的-subagents)
11. [並行 Subagent 限制](#並行-subagent-限制)
12. [管理 Subagent Context](#管理-subagent-context)
13. [Subagent 輸出掃描](#subagent-輸出掃描)
14. [常見模式](#常見模式)
15. [下一歩](#下一歩)

---

## 什麼是 Subagent

**Subagents** 是專門的 AI 助手，處理特定類型的任務。

> 💡 **使用時機**：當一個**旁支任務**會用搜尋結果、日誌或檔案內容淹沒你的主對話，而你不會再參考它們時：用 subagent 在**自己的 context 中**做那個工作，只返回摘要。

每個 subagent 都在自己的 context 視窗中執行，具有自訂系統提示、特定的工具存取和獨立的權限。當 Claude 遇到符合 subagent 描述的任務時，它會委派給該 subagent，subagent 獨立工作並返回結果。

### Subagents 幫你做到

- ✅ **保留 context**：將探索和實作保留在主對話之外
- ✅ **強制約束**：限制 subagent 可以使用哪些工具
- ✅ **跨專案重用配置**：使用者層級 subagents
- ✅ **專門化行為**：針對特定領域的專注系統提示
- ✅ **控制成本**：將任務路由到更快、更便宜的模型如 Haiku

Claude 使用每個 subagent 的描述來決定何時委派任務。建立 subagent 時，**寫一個清晰的描述**，讓 Claude 知道何時使用它。

> Subagents 在單個 session 內工作。要平行運行多個獨立 session 並從一個地方監視，請參見 [background agents](https://code.claude.com/docs/en/agent-view)。對於相互傳遞訊息的單獨 session，請參見 [cross-session messaging](https://code.claude.com/docs/en/cross-session-messaging)。

---

## 內建 Subagents

Claude Code 包含內建 subagents，Claude 在適當時自動使用。每個繼承父對話的權限；大多數以受限的工具集執行。

> Explore 和 Plan **跳過**你的 CLAUDE.md 檔案和父 session 的 git status，以保持研究快速且便宜。**其他每個內建和自訂 subagent** 載入兩者。

### Explore

一個快速的、**唯讀**的代理，針對搜尋和分析程式碼庫進行了最佳化。

- **Model**：從主對話繼承，在 Claude API 上限為 Opus
- **Tools**：唯讀工具；Write 和 Edit 被拒絕
- **Purpose**：檔案探索、程式碼搜尋、程式碼庫探索

> 自 v2.1.198：Explore 繼承主對話的模型，而不是總是在 Haiku 上運行。在 Claude API 上，繼承的模型**上限為 Opus**。

Claude 在需要**搜尋或理解程式碼庫而不進行更改**時委派給 Explore。這讓探索結果保持在主對話 context 之外。

當叫用 Explore 時，Claude 指定一個**徹底性等級**：
- **quick** — 目標查詢
- **medium** — 平衡探索
- **very thorough** — 全面分析

### Plan

在 [plan mode](https://code.claude.com/docs/en/permission-modes#analyze-before-you-edit-with-plan-mode) 期間使用的**研究代理**，在呈現計劃前收集 context。

- **Model**：從主對話繼承
- **Tools**：唯讀工具
- **Purpose**：用於計劃的程式碼庫研究

當你在 plan mode 中且 Claude 需要理解你的程式碼庫時，它會委派研究給 Plan subagent，這樣探索輸出會保留在單獨的 context 視窗中，而主對話保持唯讀。

### general-purpose

一個能勝任複雜、多步驟任務的代理，需要探索和操作。

- **Model**：從主對話繼承
- **Tools**：每個 [subagent 可用的工具](#可用工具)
- **Purpose**：複雜研究、多步驟操作、程式碼修改

當任務需要探索和修改、複雜推理以解釋結果或多個依賴步驟時，Claude 委派給 general-purpose。

### 其他助手 Agents

| Agent | Model | 當 Claude 使用它時 |
|:------|:------|:-----------------|
| `claude` | Inherits | 當任務不適合更專門的代理時 |
| `statusline-setup` | Sonnet | 當你執行 `/statusline` 配置狀態列時 |
| `claude-code-guide` | Haiku | 當你詢問 Claude Code 功能的問題時 |

**限制內建 subagents**：

- 要阻擋特定內建類型，將其新增到 `permissions.deny`，如[停用特定 subagents](#disable-specific-subagents)
- 要防止 Claude 委派給任何 subagent，用 [`permissions.deny`](https://code.claude.com/docs/en/permissions#tool-specific-permission-rules) 拒絕 `Agent` 工具本身
- 要僅移除內建 `Explore` 和 `Plan` subagents，設定 [`CLAUDE_CODE_DISABLE_EXPLORE_PLAN_AGENTS=1`](https://code.claude.com/docs/en/env-vars)（v2.1.198+）
- 在 [non-interactive mode](https://code.claude.com/docs/en/headless) 和 [Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview) 中，設定 [`CLAUDE_AGENT_SDK_DISABLE_BUILTIN_AGENTS=1`](https://code.claude.com/docs/en/env-vars) 移除所有內建類型

> 省略 `subagent_type` 的 Agent 工具呼叫在 session 沒有 `general-purpose` subagent 作為後備時會失敗，錯誤為 [`subagent_type is required`](https://code.claude.com/docs/en/errors#subagent-type-is-required)。

---

## 快速開始：第一個 Subagent

Subagents 是帶有 YAML frontmatter 的 Markdown 檔案。

> 自 v2.1.198，`/agents` 命令**不再打開**互動式建立精靈；運行它會列印提醒，要求向 Claude 詢問或直接編輯 `.claude/agents/`。

這個演練建立一個**使用者層級**的 subagent，審查程式碼並建議改進。

### Step 1：向 Claude 描述

在 Claude Code 中，描述你想要的 subagent 以及儲存位置：

```
Create a personal code-improver subagent in ~/.claude/agents/ that scans
files and suggests improvements for readability, performance, and best
practices. It should explain each issue, show the current code, and
provide an improved version. Make it read-only and have it use Sonnet.
```

Claude 寫入帶有 `name`、`description`、`tools` 清單、`model` 和系統提示的檔案。

### Step 2：檢查檔案

`~/.claude/agents/code-improver.md`：

```markdown
---
name: code-improver
description: Scans files and suggests improvements for readability, performance, and best practices. Use after writing or modifying code.
tools: Read, Grep, Glob
model: sonnet
---

You are a code improvement specialist. For each issue you find, explain
the problem, show the current code, and provide an improved version.
```

> 因為檔案在 `~/.claude/agents/`，subagent 在你機器上的每個專案中都可用。
> 若要將其範圍限制為一個專案，將其移到該專案的 `.claude/agents/` 目錄。

### Step 3：叫用新的 Subagent

```
Use the code-improver agent to suggest improvements in this project
```

Claude 委派給你的新 subagent，它掃描程式碼庫並返回改進建議。

> 如果 Claude 找不到新的 subagent，重新啟動 Claude Code 後再試一次。這只會在 `~/.claude/agents/` 在 session 開始前不存在時發生，因為執行中的 session 不會偵測新建立的 `agents` 目錄。

---

## 配置 Subagents

Subagent 的檔案位置決定它的可用範圍，frontmatter 決定它能做什麼。本節涵蓋 subagent 檔案存放在哪裡以及它們支援的每個欄位。

### 選擇 Subagent 範圍

| 位置 | 範圍 | 優先級 | 如何建立 |
|:-----|:-----|:-------|:---------|
| Managed settings | 組織範圍 | 1 (最高) | 透過 [managed settings](https://code.claude.com/docs/zh-TW/settings) 部署 |
| `--agents` CLI flag | 目前 session | 2 | 啟動 Claude Code 時傳遞 JSON |
| `.claude/agents/` | 目前專案 | 3 | 向 Claude 詢問，或手動建立檔案 |
| `~/.claude/agents/` | 所有你的專案 | 4 | 向 Claude 詢問，或手動建立檔案 |
| Plugin 的 `agents/` 目錄 | Plugin 啟用的地方 | 5 (最低) | 隨 [plugins](./02-plugins.md) 安裝 |

**專案 subagents**（`.claude/agents/`）適合特定於程式碼庫的 subagents。將它們簽入版本控制，以便你的團隊可以協作使用和改進。

> 專案 subagents 是從目前工作目錄向上走發現的，所以目前工作目錄和儲存庫根目錄之間的每個 `.claude/agents/` 都會被掃描。
> 自 v2.1.178，當這些巢狀目錄中的一個以上定義相同的 `name` 時，Claude Code 使用**最接近工作目錄**的定義。

**使用者 subagents**（`~/.claude/agents/`）是個人 subagents，在你所有專案中可用。

> Claude Code **遞迴掃描** `.claude/agents/` 和 `~/.claude/agents/`，所以你可以將定義組織到子資料夾中，如 `agents/review/` 或 `agents/research/`。子目錄路徑不影響 subagent 的識別或叫用方式，因為身份僅來自 `name` frontmatter 欄位。

**CLI 定義的 subagents** 從 JSON 傳遞：

```bash
claude --agents '{
  "code-reviewer": {
    "description": "Expert code reviewer. Use proactively after code changes.",
    "prompt": "You are a senior code reviewer. Focus on code quality, security, and best practices.",
    "tools": ["Read", "Grep", "Glob", "Bash"],
    "model": "sonnet"
  },
  "debugger": {
    "description": "Debugging specialist for errors and test failures.",
    "prompt": "You are an expert debugger. Analyze errors, identify root causes, and provide fixes."
  }
}'
```

`--agents` flag 接受帶有 `prompt` 欄位的 JSON，加上這些 [frontmatter](#支援的-frontmatter-欄位) 欄位：`description`、`tools`、`disallowedTools`、`model`、`permissionMode`、`mcpServers`、`hooks`、`maxTurns`、`skills`、`initialPrompt`、`memory`、`effort`、`background` 和 `isolation`。

> ⚠️ **Plugin 限制**：出於安全原因，plugin subagents **不支援** `hooks`、`mcpServers` 或 `permissionMode` frontmatter 欄位。

### 撰寫 Subagent 檔案

Subagent 檔案使用 YAML frontmatter 進行配置，後跟 Markdown 中的系統提示：

```markdown .claude/agents/code-reviewer.md
---
name: code-reviewer
description: Reviews code for quality and best practices
tools: Read, Glob, Grep
model: sonnet
---

You are a code reviewer. When invoked, analyze the code and provide
specific, actionable feedback on quality, security, and best practices.
```

> Frontmatter 定義 subagent 的元資料和配置。**主體成為引導 subagent 行為的系統提示**。
> Subagents 只接收此系統提示加上基本環境詳細資訊（如工作目錄），**不是完整的 Claude Code 系統提示**。

> Claude Code 監視 `~/.claude/agents/` 和 `.claude/agents/`。當你在磁碟上新增或編輯 subagent 檔案時，Claude Code 在**幾秒內**偵測變更，下次委派使用更新的定義，無需重啟。

### 支援的 Frontmatter 欄位

以下欄位可用於 YAML frontmatter。只有 `name` 和 `description` 是必需的。

| 欄位 | 必需 | 描述 |
|:-----|:-----|:-----|
| `name` | ✅ | 唯一識別碼使用小寫字母和連字號。Hooks 接收此值作為 `agent_type`。檔名不必匹配。名稱不能包含 `:` |
| `description` | ✅ | Claude 應何時委派給此 subagent |
| `tools` | ❌ | Subagent 可以使用的工具。若省略，繼承每個 subagent 可用的工具 |
| `disallowedTools` | ❌ | 拒絕的工具，從繼承或指定清單中移除 |
| `model` | ❌ | 使用的模型：`sonnet`、`opus`、`haiku`、`fable`、完整模型 ID 或 `inherit`。預設 `inherit` |
| `permissionMode` | ❌ | 權限模式：`default`、`acceptEdits`、`auto`、`dontAsk`、`bypassPermissions`、`plan` |
| `maxTurns` | ❌ | Subagent 停止前的最大代理輪次 |
| `skills` | ❌ | 在啟動時預載入 subagent context 的 skills |
| `mcpServers` | ❌ | 此 subagent 可用的 MCP servers |
| `hooks` | ❌ | 限定於此 subagent 的生命週期 hooks |
| `memory` | ❌ | 持久記憶範圍：`user`、`project` 或 `local` |
| `background` | ❌ | 設為 `true` 即使 Claude 要求前台運行也將此 subagent 保留在背景 |
| `effort` | ❌ | 此 subagent 處於活動狀態時的努力級別 |
| `isolation` | ❌ | 設為 `worktree` 在臨時 git worktree 中運行 subagent |
| `color` | ❌ | 在任務清單和 transcript 中的顯示顏色 |
| `initialPrompt` | ❌ | 當此代理作為主 session 代理運行時自動提交為第一個使用者輪次 |

---

## 選擇模型

`model` 欄位控制 subagent 使用哪個 AI 模型：

- **Model 別名**：使用其中一個可用別名：`sonnet`、`opus`、`haiku` 或 `fable`
- **完整模型 ID**：使用完整模型 ID 如 `claude-opus-5` 或 `claude-sonnet-5`
- **inherit**：使用與主對話相同的模型
- **Omitted**：預設為 `inherit`

當 Claude 叫用 subagent 時，它也可以為該次特定叫用傳遞 `model` 參數。Claude Code 按此順序解析 subagent 的模型：

1. 環境變數 [`CLAUDE_CODE_SUBAGENT_MODEL`](https://code.claude.com/docs/en/model-config#environment-variables)
2. 每次叫用的 `model` 參數
3. Subagent 定義的 `model` frontmatter
4. 主對話的模型

> 自 v2.1.198，subagents **也繼承**主對話的[擴展思考](https://code.claude.com/docs/en/model-config#extended-thinking)配置。

---

## 控制 Subagent 能力

你可以透過**工具存取**、**權限模式**和**條件式規則**來控制 subagent 可以做什麼。

### 限制可生成的 Subagent 類型

當代理作為主執行緒使用 `claude --agent` 運行時，它可以使用 Agent 工具生成 subagents。要限制它可以生成哪些 subagent 類型，使用 `Agent(agent_type)` 語法在 `tools` 欄位中。

```yaml
---
name: coordinator
description: Coordinates work across specialized agents
tools: Agent(worker, researcher), Read, Bash
---
```

這是一個**白名單**：只有 `worker` 和 `researcher` subagents 可以被生成。

要允許無限制地生成任何 subagent，使用 `Agent` 沒有括號：

```yaml
tools: Agent, Read, Bash
```

> `Agent(agent_type)` 白名單語法**僅適用於**使用 `claude --agent` 作為主執行緒的代理。

### 範圍 MCP Servers 到 Subagent

使用 `mcpServers` 欄位給 subagent 訪問主對話中不可用的 [MCP](https://code.claude.com/docs/en/mcp) servers。Inline servers 在這裡定義在 subagent 啟動時連接（受 agent 檔案所在資料夾的[信任規則](https://code.claude.com/docs/en/permissions#project-allow-rules-and-workspace-trust)約束），在 subagent 完成時斷開連接。

```yaml
---
name: browser-tester
description: Tests features in a real browser using Playwright
mcpServers:
  # Inline 定義：僅限此 subagent
  - playwright:
      type: stdio
      command: npx
      args: ["-y", "@playwright/mcp@latest"]
  # 按名稱引用：重用已配置的 server
  - github
---

Use the Playwright tools to navigate, screenshot, and interact with pages.
```

> 若要將 MCP server 完全保留在主對話之外並避免其工具描述消耗那裡的 context，**在這裡 inline 定義**而不是在 `.mcp.json` 中。

### 預載入 Skills 到 Subagents

使用 `skills` 欄位在啟動時將 skill 內容注入到 subagent 的 context 中。

```yaml
---
name: api-developer
description: Implement API endpoints following team conventions
skills:
  - api-conventions
  - error-handling-patterns
---

Implement API endpoints. Follow the conventions and patterns from the preloaded skills.
```

> 列出的每個 skill 的**完整內容**在啟動時注入到 subagent 的 context 中。
> 此欄位控制哪些 skills 被預載入，**不是** subagent 可以訪問哪些 skills：沒有它，subagent 仍然可以通過執行期間的 Skill 工具發現和叫用專案、使用者和 plugin skills。

> 你**無法預載入**設定 [`disable-model-invocation: true`](./04-skills.md#控制誰能叫用-skill) 的 skills，因為預載入從與 Claude 可以叫用的同一組 skills 中提取。

### 啟用持久記憶

`memory` 欄位給 subagent 一個**跨對話存活**的持久目錄。Subagent 使用此目錄隨時間建立知識，例如程式碼庫模式、除錯見解和架構決策。

```yaml
---
name: code-reviewer
description: Reviews code for quality and best practices
memory: user
---

You are a code reviewer. As you review code, update your agent memory with
patterns, conventions, and recurring issues you discover.
```

選擇基於記憶應該應用多廣的範圍：

| 範圍 | 位置 | 使用時機 |
|:-----|:-----|:---------|
| `user` | `~/.claude/agent-memory/<name>/` | subagent 應該跨所有專案記住學習內容 |
| `project` | `.claude/agent-memory/<name>/` | subagent 的知識是專案特定的且可透過版本控制共享 |
| `local` | `.claude/agent-memory-local/<name>/` | subagent 的知識是專案特定的但不應簽入版本控制 |

> Subagent 記憶是 [auto memory](https://code.claude.com/docs/zh-TW/memory#auto-memory) 的一部分：如果你關閉 auto memory，則 `memory` 欄位無效，subagent 啟動時不包含記憶指令或下面描述的記憶工具存取。

當記憶啟用時：
- Subagent 的系統提示包括讀寫記憶目錄的指令
- Subagent 的系統提示還包括記憶目錄中 `MEMORY.md` 的**前 200 行或 25KB**，以先到者為準
- **Read、Write 和 Edit 工具**自動啟用，以便 subagent 可以管理其記憶檔案

### 條件式規則與 Hooks

對於工具使用的**更動態控制**，使用 `PreToolUse` hooks 在操作執行前驗證它們。

此範例建立一個**只允許唯讀資料庫查詢**的 subagent。`PreToolUse` hook 在每個 Bash 命令執行前執行 `command` 中指定的腳本：

```yaml
---
name: db-reader
description: Execute read-only database queries
tools: Bash
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate-readonly-query.sh"
---
```

驗證腳本讀取 JSON 輸入，提取 Bash 命令，並以代碼 2 退出以阻止寫入操作：

```bash
#!/bin/bash
# ./scripts/validate-readonly-query.sh

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

# 阻擋 SQL 寫入操作（不區分大小寫）
if echo "$COMMAND" | grep -iE '\b(INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|TRUNCATE)\b' > /dev/null; then
  echo "Blocked: Only SELECT queries are allowed" >&2
  exit 2
fi

exit 0
```

> 在 macOS 和 Linux 上，**使腳本可執行**，否則 hook 會失敗而不是阻止任何東西：
> ```bash
> chmod +x ./scripts/validate-readonly-query.sh
> ```

要測試規則，要求 subagent 運行 `UPDATE` 語句：腳本退出代碼 2，Claude Code 阻止命令，subagent 看到 `Blocked: Only SELECT queries are allowed` 訊息。

---

## 可用工具

Subagents 繼承主對話中可用的[內建工具](https://code.claude.com/docs/zh-TW/tools-reference)和 MCP 工具，由**兩個過濾器**縮窄。

### 第一過濾器：從每個 Subagent 移除

即使在 `tools` 欄位中列出，這些工具也會被移除：

- `Agent`，當 subagent 在[深度限制](#讓-subagents-生成自己的-subagents)時
- `AskUserQuestion`
- `EndConversation`，只能結束主對話
- `EnterPlanMode`
- `ExitPlanMode`，除非 subagent 的 [`permissionMode`](#permission-modes) 是 `plan`
- `ScheduleWakeup`
- `TaskOutput`
- `WaitForMcpServers`
- `Workflow`

### 第二過濾器：背景 Subagents

在背景運行的 subagents 保留每個 MCP 工具，但只有這些內建工具：`Read`、`Grep`、`Glob`、`Bash`、`PowerShell`、`Edit`、`Write`、`NotebookEdit`、`WebFetch`、`WebSearch`、`TodoWrite`、`Skill`、`ToolSearch`、`EnterWorktree`、`ExitWorktree`、`Monitor`、`TaskStop`、`SendMessage` 和 `Artifact`。

### 限制工具

要限制工具，使用 `tools` 欄位作為**白名單**或 `disallowedTools` 欄位作為**黑名單**。

```yaml
---
name: safe-researcher
description: Research agent with restricted capabilities
tools: Read, Grep, Glob, Bash
---
```

```yaml
---
name: no-writes
description: Inherits the available tools except file writes
disallowedTools: Write, Edit
---
```

> 如果兩者都設定，`disallowedTools` **首先套用**，然後 `tools` 對剩餘池解析。
> 當 `tools` 清單中沒有任何項目解析為工具時，Claude Code **通常拒絕啟動** subagent。

兩個欄位都接受 MCP server 級別模式，除了精確工具名稱：`mcp__<server>` 或 `mcp__<server>__*` 授予或移除來自命名 server 的每個工具。在 `disallowedTools` 中，`mcp__*` 也從任何 server 移除每個 MCP 工具。

```yaml
---
name: local-only
description: Inherits every tool except those from the github MCP server
disallowedTools: mcp__github
---
```

---

## 範例 Subagents

### Code Reviewer

一個**唯讀**的 subagent，審查程式碼而不修改它。

```markdown
---
name: code-reviewer
description: Expert code review specialist. Proactively reviews code for quality, security, and maintainability. Use immediately after writing or modifying code.
tools: Read, Grep, Glob, Bash
model: inherit
---

You are a senior code reviewer ensuring high standards of code quality and security.

When invoked:
1. Run git diff to see recent changes
2. Focus on modified files
3. Begin review immediately

Review checklist:
- Code is clear and readable
- Functions and variables are well-named
- No duplicated code
- Proper error handling
- No exposed secrets or API keys
- Input validation implemented
- Good test coverage
- Performance considerations addressed

Provide feedback organized by priority:
- Critical issues (must fix)
- Warnings (should fix)
- Suggestions (consider improving)

Include specific examples of how to fix issues.
```

### Debugger

可以**分析和修復問題**的 subagent。Prompt 提供從診斷到驗證的清晰工作流。

```markdown
---
name: debugger
description: Debugging specialist for errors, test failures, and unexpected behavior. Use proactively when encountering any issues.
tools: Read, Edit, Bash, Grep, Glob
---

You are an expert debugger specializing in root cause analysis.

When invoked:
1. Capture error message and stack trace
2. Identify reproduction steps
3. Isolate the failure location
4. Implement minimal fix
5. Verify solution works

Debugging process:
- Analyze error messages and logs
- Check recent code changes
- Form and test hypotheses
- Add strategic debug logging
- Inspect variable states

For each issue, provide:
- Root cause explanation
- Evidence supporting the diagnosis
- Specific code fix
- Testing approach
- Prevention recommendations

Focus on fixing the underlying issue, not the symptoms.
```

### Data Scientist

用於資料分析工作的**特定領域** subagent。明確設定 `model: sonnet` 以獲得更有能力的分析。

```markdown
---
name: data-scientist
description: Data analysis expert for SQL queries, BigQuery operations, and data insights. Use proactively for data analysis tasks and queries.
tools: Bash, Read, Write
model: sonnet
---

You are a data scientist specializing in SQL and BigQuery analysis.

When invoked:
1. Understand the data analysis requirement
2. Write efficient SQL queries
3. Use BigQuery command line tools (bq) when appropriate
4. Analyze and summarize results
5. Present findings clearly

Key practices:
- Write optimized SQL queries with proper filters
- Use appropriate aggregations and joins
- Include comments explaining complex logic
- Format results for readability
- Provide data-driven recommendations

For each analysis:
- Explain the query approach
- Document any assumptions
- Highlight key findings
- Suggest next steps based on data

Always ensure queries are efficient and cost-effective.
```

### Database Query Validator

允許 Bash 存取但**驗證命令**以僅允許**唯讀 SQL 查詢**的 subagent。

```markdown
---
name: db-reader
description: Execute read-only database queries. Use when analyzing data or generating reports.
tools: Bash
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate-readonly-query.sh"
---

You are a database analyst with read-only access. Execute SELECT queries to answer questions about the data.

When asked to analyze data:
1. Identify which tables contain the relevant data
2. Write efficient SELECT queries with appropriate filters
3. Present results clearly with context

You cannot modify data. If asked to INSERT, UPDATE, DELETE, or modify schema, explain that you only have read access.
```

驗證腳本（見上方 [條件式規則與 Hooks](#條件式規則與-hooks) 章節）。

---

## 使用 Subagents

### 理解自動委派

Claude 根據你請求中的**任務描述**、subagent 配置中的 `description` 欄位和**目前 context** 自動委派任務。要鼓勵主動委派，在你的 subagent 的 description 欄位中包含像 "use proactively" 這樣的短語。

### 明確叫用 Subagents

當自動委派不夠時，你可以自己請求一個 subagent。三種模式從一次性建議升級到 session 範圍預設：

**1. 自然語言**：在你的 prompt 中命名 subagent；Claude 決定是否委派

```
Use the test-runner subagent to fix failing tests
Have the code-reviewer subagent look at my recent changes
```

**2. @-mention**：保證 subagent 為一個任務運行

```
@"code-reviewer (agent)" look at the auth changes
```

輸入 `@` 並從 typeahead 中選擇 subagent（與 @-mention 檔案的方式相同）。你的完整訊息仍然發給 Claude，它根據你問的內容撰寫 subagent 的任務 prompt。@-mention 控制 Claude 叫用哪個 subagent，**不是**它接收什麼 prompt。

> Plugin 提供的 subagents 在 typeahead 中以**範圍名稱**出現，例如 `my-plugin:code-reviewer` 或 `my-plugin:review:security`（當 plugin [將 agents 組織到子資料夾中](#選擇-subagent-範圍)時）。

**3. Session 範圍**：整個 session 使用該 subagent 的系統提示、工具限制和模型

```bash
claude --agent code-reviewer
```

Subagent 的系統提示**完全替換**預設的 Claude Code 系統提示，就像 [`--system-prompt`](https://code.claude.com/docs/en/cli-reference) 一樣。`CLAUDE.md` 檔案和專案記憶仍通過正常訊息流載入。

> 對於 plugin 提供的 subagent，你只能傳遞 agent 名稱，Claude Code 會找到它：
> ```bash
> claude --agent security-reviewer
> ```

要為專案中的每個 session 設定它為預設，在 `.claude/settings.json` 中設定 `agent`：

```json
{
  "agent": "code-reviewer"
}
```

CLI flag 如果兩者都存在則覆蓋設定。

---

### 在前台或背景運行 Subagents

Subagents 可以在**前台或背景**運行：

- **前台 subagents** 阻擋主對話直到完成
- **背景 subagents** 在你繼續工作時**並行**運行

對 Claude 用 Agent 工具生成的每個 subagent，Claude Code 按以下順序決定前台或背景：

1. 如果 in-process [agent team](https://code.claude.com/docs/en/agent-teams#limitations) teammate 生成了 subagent，Claude Code 在**前台**運行它
2. 如果你將 [`CLAUDE_CODE_DISABLE_BACKGROUND_TASKS`](https://code.claude.com/docs/en/env-vars) 設為 `1`，Claude Code 在前台運行 subagent
3. 在 [fork mode](#turn-fork-mode-on-or-off) 開啟時（互動式 session 中預設），Claude Code 在背景運行 subagent

> 背景 subagents 以比前台 subagents **更小的內建工具集**運行，除了對話 fork。
> 當你用超出該單一工具呼叫的選擇回答其中一個提示時，Claude Code 將你的答案套用於整個 session。

### Subagent 命名

Claude 可以通過在 Agent 工具呼叫上傳遞 `name` 參數給 subagent 一個名稱，並且可能**自己這樣做**，不先問你。名稱使 subagent 可定址：Claude 可以在它完成後[通過名稱訊息或恢復它](#resume-subagents)。

### API 錯誤

> 自 v2.1.199，**以 API 錯誤結束的 subagent**（如使用限制或重複的伺服器錯誤）將該失敗**報告回 Claude**，而不是將錯誤文字作為 subagent 的發現返回。Claude 接收什麼取決於 subagent 運行的位置：
> - **前台**：如果速率限制、過載或伺服器錯誤切斷已產生文字輸出的 subagent，Agent 工具返回該部分輸出以及 subagent 被切斷且未完成任務的註釋
> - **背景**：subagent 被標記為失敗，Claude 在它結束時接收的訊息命名 API 錯誤並包含 subagent 的最後輸出

一旦底層 API 錯誤清除，要求 Claude 重試任務或[恢復 subagent](#resume-subagents)。

---

## 讓 Subagents 生成自己的 Subagents

預設情況下，subagent 可以生成自己的 subagents，**最多在主對話下方三層**。在深度限制時，Claude Code 從每個 subagent 扣留 `Agent` 工具，除了 [fork](#fork-the-current-conversation)，所以在限制處的 subagent 自己做其委派工作並返回一個摘要。

巢狀 subagents 適合**自身拆分為平行子任務**的委派任務，例如分派驗證器給每個發現的 reviewer subagent，所以中間輸出永遠不會到達你的主對話。只有頂層 subagent 的摘要返回給你。

要更改限制，設定 [`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`](https://code.claude.com/docs/en/env-vars) 為你希望在主對話下方的 subagent 層數。

```json
{
  "env": {
    "CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH": "2"
  }
}
```

> 較早版本使用不同的預設值：
> - **v2.1.172 到 v2.1.216**：subagents 預設可以巢狀，最多 5 層深，且限制無法更改
> - **v2.1.217 到 v2.1.218**：限制預設為 1，所以除非你提高，subagent 無法生成自己的
> - **v2.1.219+**：預設提高到 3

---

## 並行 Subagent 限制

兩個限制控制 subagent 使用，每個都有自己的變數：這個限制在太多 subagent 運行時停止 Claude 生成更多 subagent，而[深度限制](#讓-subagents-生成自己的-subagents)限制 subagent 巢狀多深。**對 session 期間 Claude 可以生成的 subagent 總數沒有限制**。

預設情況下，**當 20 個 subagents 在 session 中運行時**，用 Agent 工具生成另一個會失敗，並出現 `Concurrent subagent limit reached`，錯誤告訴 Claude 不要重試。

要更改限制，設定 [`CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`](https://code.claude.com/docs/en/env-vars) 為任何正整數。帶有 [ultracode](https://code.claude.com/docs/en/model-config#adjust-effort-level) 活動的 session 是**豁免的**：該限制不在那裡強制。

> 該限制僅阻擋 Claude 用 Agent 工具生成的 subagents，但其他運行佔用相同的 slot：
> - 用 [`/subtask`](#fork-the-current-conversation) 啟動的 in-session fork 在其運行時佔用 slot 且永遠不會被限制阻擋
> - [恢復已完成的 subagent](#resume-subagents) 佔用新 slot 而不檢查限制，所以恢復可以將運行計數推過它

---

## 管理 Subagent Context

### 啟動時載入什麼

每個 subagent 從**全新的隔離 context 視窗**開始。它**看不到**你的對話歷史、已叫用的 skills 或 Claude 已讀的檔案。Claude 撰寫總結任務的委派訊息，subagent 從那裡工作。例外是 [fork](#fork-the-current-conversation)，它繼承父對話。

非 fork subagent 的初始 context 包含：

- **System prompt**：代理自己的 prompt 加上 Claude Code 附加的環境詳細資訊，**不是**完整的 Claude Code 系統提示
- **Task message**：Claude 在移交工作時撰寫的委派 prompt
- **CLAUDE.md 檔案**：主對話載入的**每個層級**的 CLAUDE.md 層次結構
- **Git status**：在父 session 開始時拍攝的快照
- **Preloaded skills**：任何在代理的 [`skills` 欄位](#預載入-skills-到-subagents)中命名的 skill 的**完整內容**
- **Sibling roster**：列出 `main` 和 session 中每個其他命名代理的系統提醒

> Explore 和 Plan 是**唯一省略** CLAUDE.md 和 git status 的 subagents。

一些主對話狀態**永遠不會到達**非 fork subagent：

- **Output style**：subagent 運行自己的系統提示
- **Auto memory**：主對話的 [auto memory](https://code.claude.com/docs/zh-TW/memory#auto-memory) **未載入**
- **Context window size**：subagent 的 context window 由其自己的模型決定

### 恢復 Subagents

每個 subagent 叫用創建一個新實例。要繼續現有 subagent 的工作而不是從頭開始，要求 Claude 恢復它。

> 恢復的 subagents 保留其完整的對話歷史，包括所有先前的工具呼叫、結果和推理。subagent **從停止的地方準確地接著**。

當 subagent 完成時，Claude 接收其代理 ID。內建 Explore 和 Plan 代理是**一次性**的，不返回代理 ID，所以**無法恢復**；當你需要繼續工作時使用 `general-purpose` 或自訂 subagent。

要恢復 subagent，要求 Claude 繼續之前的工作：

```
Use the code-reviewer subagent to review the authentication module
[Agent completes]

Continue that code review and now analyze the authorization logic
[Claude resumes the subagent with full context from previous conversation]
```

> 自 v2.1.191，你自己停止的 subagent（用 `/tasks` 中的 `x` 或 SDK `stop_task` 請求）**不會自動恢復**。`SendMessage` 呼叫返回一個拒絕，告訴 Claude 代理已取消。

---

## Subagent 輸出掃描

Claude Code 在 Claude 讀取之前**掃描每個 subagent 的最終報告**。

> Subagent 可能已讀取你從未審查的檔案、網頁或命令輸出，並且來自那些來源的文字可以**帶有針對主對話的指令**。掃描永遠不會刪除或重新措辭任何內容；它做出你可能在報告中注意到的兩種變更：
>
> - **反斜線插入**：掃描將反斜線插入到模仿 Claude Code 自己輸出的文字中，例如 `<tool_use>` 標籤或以 `Human:` 或 `Assistant:` 開頭的行
> - **Marker line**：當報告模仿 `<tool_use>` 標籤或提到權限設定（如 `bypassPermissions` 或 `--dangerously-skip-permissions`）時，掃描在前面加上一行

> Subagent 輸出掃描需要 Claude Code v2.1.210+。

---

## 常見模式

### 隔離高容量操作

subagent 最有效的用途之一是**隔離產生大量輸出**的操作。執行測試、獲取文件或處理日誌檔案可能會消耗大量 context。通過委派給 subagent，詳細的輸出**保留在 subagent 的 context 中**，而只有相關的摘要返回到你的主對話。

```
Use a subagent to run the test suite and report only the failing tests with their error messages
```

### 平行運行研究

對於獨立調查，**生成多個 subagents 同時工作**：

```
Research the authentication, database, and API modules in parallel using separate subagents
```

每個 subagent 獨立探索其區域，然後 Claude 綜合發現。**當研究路徑不互相依賴時效果最好**。

> 當 subagents 完成時，**它們的結果返回到你的主對話**。運行許多 subagents 每個返回詳細結果可能會消耗大量 context。
> 對於需要持續並行或超出 context window 的任務，[agent teams](https://code.claude.com/docs/en/agent-teams) 為每個工作者提供自己獨立的 context。

### 鏈接 Subagents

對於多步驟工作流，要求 Claude **按順序使用 subagents**。每個 subagent 完成其任務並將結果返回給 Claude，然後 Claude 將相關 context 傳遞給下一個 subagent。

```
Use the code-reviewer subagent to find performance issues, then use the optimizer subagent to fix them
```

### 選擇 Subagents vs 主對話

使用**主對話**當：
- 任務需要**頻繁的來回**或迭代改進
- 多個階段**共享重要 context**（如計劃、實作和測試）
- 你正在進行快速、有針對性的更改
- **延遲很重要**（非 fork subagent 從頭開始，可能需要時間收集 context）

使用 **subagents** 當：
- 任務**產生你不需要在主 context 中的詳細輸出**
- 你想強制執行**特定工具限制或權限**
- 工作是**自包含的**並且可以返回摘要

考慮 [Skills](./04-skills.md) 當你想要在**主對話 context** 中運行的可重用 prompts 或工作流，而不是隔離的 subagent context。

---

## 下一歩

現在你已了解 subagents，探索這些相關功能：

- [用 plugins 分發 subagents](./02-plugins.md)：跨團隊或專案共享 subagents
- [以程式化方式運行 Claude Code](https://code.claude.com/docs/en/headless)：用於 CI/CD 和自動化的 Agent SDK
- [使用 MCP servers](https://code.claude.com/docs/en/mcp)：給 subagents 訪問外部工具和數據
