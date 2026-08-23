# Hooks 完整指南（事件驅動自動化）

> 📖 **系列**：Claude Code Plugin 完整學習系列 #06
> 🌐 **原文**：[code.claude.com/docs/en/hooks](https://code.claude.com/docs/en/hooks)
> 📅 **整理日期**：2026 / 01
> 🎯 **適用版本**：Claude Code v2.1.x

> 💡 **本系列總覽**：見 [00-claude-code-plugins-series.md](./00-claude-code-plugins-series.md)
> 📚 **上一篇**：[05-subagents.md](./05-subagents.md)（Subagents 自訂指南）
> 📚 **下一篇**：[07-discover-plugins.md](./07-discover-plugins.md)（探索並安裝 Plugins）

## 目錄

1. [什麼是 Hook](#什麼是-hook)
2. [Hook 生命週期](#hook-生命週期)
3. [Hook 解析流程](#hook-解析流程)
4. [設定配置](#設定配置)
5. [Matcher 模式](#matcher-模式)
6. [Hook Handler 類型](#hook-handler-類型)
7. [常見欄位](#常見欄位)
8. [Command Hook 詳細設定](#command-hook-詳細設定)
9. [HTTP Hook 詳細設定](#http-hook-詳細設定)
10. [MCP Tool Hook 詳細設定](#mcp-tool-hook-詳細設定)
11. [Prompt 與 Agent Hooks](#prompt-與-agent-hooks)
12. [路徑引用](#路徑引用)
13. [Skills 和 Agents 中的 Hooks](#skills-和-agents-中的-hooks)
14. [Hook 輸入與輸出](#hook-輸入與輸出)
15. [退出碼輸出](#退出碼輸出)
16. [JSON 輸出](#json-輸出)
17. [發送終端通知](#發送終端通知)
18. [為 Claude 新增上下文](#為-claude-新增上下文)
19. [決策控制](#決策控制)
20. [所有 Hook 事件詳解](#所有-hook-事件詳解)
21. [背景執行 Hooks](#背景執行-hooks)
22. [安全性考量](#安全性考量)
23. [PowerShell on Windows](#powershell-on-windows)
24. [Debug Hooks](#debug-hooks)
25. [疑難排解](#疑難排解)

---

## 什麼是 Hook

**Hook** 是使用者定義的 shell 命令、HTTP endpoint 或 LLM prompt，**在 Claude Code 生命週期的特定點自動執行**。

使用 hook 給你**確定性的控制**：特定動作一定會發生，而不是依賴 LLM 選擇執行。

| 使用場景 | 範例 |
|:---------|:-----|
| 強制專案規則 | 「永遠不要編輯 `.env`」 |
| 自動化重複任務 | 編輯後跑 formatter |
| 整合現有工具 | 編輯後跑 ESLint |
| 通知 | 完成時發 Slack 通知 |
| 阻擋危險操作 | 阻擋 `rm -rf` |

> 對於需要判斷的決策（而非確定性規則），你可以使用 [prompt-based hooks](#prompt-based-hooks) 或 [agent-based hooks](#agent-based-hooks) 用 Claude 模型評估條件。

---

## Hook 生命週期

Claude Code 在會話期間的特定點執行 hook。事件分為三個節奏：

- **每個 session 一次**：`SessionStart`、`SessionEnd`
- **每輪一次**：`UserPromptSubmit`、`Stop`、`StopFailure`
- **每次 agentic loop 內的工具呼叫**：`PreToolUse`、`PostToolUse`（除了 [`EndConversation`](https://code.claude.com/docs/en/tools-reference#endconversation-tool-behavior) 呼叫）

### 完整事件表

| Event | When it fires |
|:------|:--------------|
| `SessionStart` | 當一個 session 開始或恢復時 |
| `Setup` | 當你用 `--init-only` 啟動 Claude Code，或在 `-p` 模式下使用 `--init` 或 `--maintenance`。用於 CI 或腳本中的一次性準備 |
| `UserPromptSubmit` | 當你提交 prompt，在 Claude 處理之前 |
| `UserPromptExpansion` | 當使用者輸入的命令展開為 prompt，在到達 Claude 之前。可以阻擋展開 |
| `PreToolUse` | 在工具呼叫執行之前。可以阻擋它 |
| `PermissionRequest` | 當工具呼叫需要權限決策時 |
| `PermissionDenied` | 當 auto mode 拒絕工具呼叫時，包括沒有分類器裁決的拒絕。使用 JSON `hookSpecificOutput.retry: true` 告訴模型它可以重試被拒絕的工具呼叫。Claude Code 忽略無裁決拒絕的 `retry` |
| `PostToolUse` | 工具呼叫成功後 |
| `PostToolUseFailure` | 工具呼叫失敗後 |
| `PostToolBatch` | 整批平行工具呼叫解析後，下個模型呼叫之前 |
| `Notification` | 當 Claude Code 發送通知時 |
| `MessageDisplay` | 當助手訊息文字顯示時 |
| `SubagentStart` | 當 subagent 被生成時 |
| `SubagentStop` | 當 subagent 完成時 |
| `TaskCreated` | 當透過 `TaskCreate` 建立任務時 |
| `TaskCompleted` | 當任務被標記為完成時 |
| `Stop` | 當 Claude 完成回應時 |
| `StopFailure` | 當輪次因 API 錯誤而結束時 |
| `TeammateIdle` | 當 [agent team](https://code.claude.com/docs/en/agent-teams) teammate 即將閒置時 |
| `InstructionsLoaded` | 當 CLAUDE.md 或 `.claude/rules/*.md` 檔案載入到 context 時 |
| `ConfigChange` | 當 session 中配置檔案變更時 |
| `CwdChanged` | 當工作目錄變更時 |
| `DirectoryAdded` | 當工作目錄在 session 中途透過 `/add-dir` 或 SDK `register_repo_root` 控制請求加入時 |
| `FileChanged` | 當被監視的檔案在磁碟上變更時 |
| `WorktreeCreate` | 當透過 `--worktree`、`isolation: "worktree"` 建立 worktree 時 |
| `WorktreeRemove` | 當 worktree 在 session 退出、subagent 完成或刪除背景 session 時被移除時 |
| `PreCompact` | 在 context compaction 之前 |
| `PostCompact` | 在 context compaction 完成後 |
| `Elicitation` | 當 MCP server 在工具呼叫期間請求使用者輸入時 |
| `ElicitationResult` | 在使用者回應 MCP elicitation 之後，回應送回 server 之前 |
| `SessionEnd` | 當 session 終止時 |

---

## Hook 解析流程

看個例子：`PreToolUse` hook 阻擋破壞性的 shell 命令。

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "if": "Bash(rm *)",
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/block-rm.sh",
            "args": []
          }
        ]
      }
    ]
  }
}
```

執行步驟：

1. **`PreToolUse` 事件觸發** — Claude Code 將工具輸入作為 JSON 透過 stdin 送到 hook
2. **Matcher `"Bash"` 匹配**工具名稱
3. **`if` 條件 `"Bash(rm *)"` 匹配**因為命令以 `rm` 開頭
4. **腳本執行**，檢查 `rm -rf` 並輸出決策：
   ```json
   {
     "hookSpecificOutput": {
       "hookEventName": "PreToolUse",
       "permissionDecision": "deny",
       "permissionDecisionReason": "Destructive command blocked by hook"
     }
   }
   ```
5. **Claude Code 讀取決策**、阻擋工具呼叫、向 Claude 顯示原因

如果命令是 `npm test`，腳本會 hit `exit 0`（exit code 0 加上無輸出 = hook 無決策），工具呼叫透過正常權限流程繼續。

> 💡 這個範例假設已安裝 `jq` 來解析 JSON 輸入。如果你的 hook 腳本也解析 JSON，先安裝 `jq`。

---

## 設定配置

Hooks 在 JSON 設定檔中定義。配置有三層巢狀：

1. **選擇 [hook 事件](#hook-生命週期)** 來回應，例如 `PreToolUse` 或 `Stop`
2. **新增 [matcher group](#matcher-模式)** 來過濾觸發時機，例如「只對 Bash 工具」
3. **定義一個或多個 [hook handlers](#hook-handler-類型)** 在匹配時執行

### Hook 位置

定義 hook 的位置決定其範圍：

| 位置 | 範圍 | 可分享 |
|:-----|:-----|:-------|
| `~/.claude/settings.json` | 你所有專案 | ❌（本地） |
| `.claude/settings.json` | 單一專案 | ✅（可 commit） |
| `.claude/settings.local.json` | 單一專案 | ❌（gitignored） |
| Managed policy settings | 組織範圍 | ✅（管理員控制） |
| [Plugin](./03-plugins-reference.md) `hooks/hooks.json` | 啟用 plugin 時 | ✅（隨 plugin 打包） |
| [Skill](./04-skills.md) frontmatter | 叫用 skill 後的 session 其餘時間 | ✅（在 skill 檔案中） |
| [Subagent](./05-subagents.md) frontmatter | 該 subagent 執行期間 | ✅（在 subagent 檔案中） |

> 雲端 session（[Claude Code on the web](https://code.claude.com/docs/en/claude-code-on-the-web)）不讀取你的本地 `~/.claude/settings.json`；那裡的 hooks 來自 repo 和組織的伺服器管理設定。

**Managed-only Hooks 限制**：
- 管理員可以用 `allowManagedHooksOnly` 限制可執行的 hook
- 阻擋使用者、專案、本地和 plugin hooks
- 同時收窄 [`statusLine`](https://code.claude.com/docs/en/statusline)、[`fileSuggestion`](https://code.claude.com/docs/en/settings-reference#filesuggestion) 和 [`subagentStatusLine`](https://code.claude.com/docs/en/statusline#subagent-status-lines) 到 managed 設定
- 同時停用具有 [`command` source](https://code.claude.com/docs/en/plugin-marketplaces#command-sources) 的 plugins

**Hook 條目會跨設定層級合併**，而不是互相替換。

---

## Matcher 模式

`matcher` 欄位過濾 hook 何時觸發。如何評估取決於它包含的字元：

| Matcher 值 | 評估為 | 範例 |
|:-----------|:-------|:-----|
| `"*"`, `""`, 或省略 | 匹配所有 | 每次事件觸發都 fire |
| 只有字母、數字、`_`、`-`、空格、`,`、`\|` | 精確字串或用 `\|` 或 `,` 分隔的清單 | `Bash` 只匹配 Bash 工具；`Edit\|Write` 匹配任一工具 |
| 包含任何其他字元 | JavaScript regex，未錨定 | `^Notebook` 匹配名稱以 `Notebook` 開頭的工具 |

> 含 `-` 的精確匹配集需要 Claude Code v2.1.195+。在早期版本上，含連字號的名稱（如 `code-reviewer`）被當作未錨定 regex。
> 含 `,` 的精確匹配集需要 Claude Code v2.1.191+。

### 各事件支援的 Matcher

| Event | Matcher 過濾的內容 | 範例 matcher 值 |
|:------|:------------------|:---------------|
| `PreToolUse`、`PostToolUse`、`PostToolUseFailure`、`PermissionRequest`、`PermissionDenied` | 工具名稱 | `Bash`、`Edit\|Write`、`mcp__.*` |
| `SessionStart` | session 如何開始 | `startup`、`resume`、`clear`、`compact`、`fork` |
| `Setup` | 哪個 CLI flag 觸發 setup | `init`、`maintenance` |
| `SessionEnd` | 為什麼 session 結束 | `clear`、`resume`、`logout`、`prompt_input_exit`、`other` |
| `Notification` | 通知類型 | `permission_prompt`、`idle_prompt`、`auth_success` 等 |
| `SubagentStart` | agent 類型 | `general-purpose`、`Explore`、`Plan`、自訂名稱 |
| `PreCompact`、`PostCompact` | 什麼觸發了 compaction | `manual`、`auto` |
| `SubagentStop` | agent 類型 | 同 `SubagentStart` |
| `ConfigChange` | 配置來源 | `user_settings`、`project_settings` 等 |
| `StopFailure` | 錯誤類型 | `rate_limit`、`overloaded`、`authentication_failed` 等 |
| `FileChanged` | 要監視的檔名（見 [FileChanged](#filechanged)） | `.envrc\|.env` |
| `UserPromptExpansion` | 命令名稱 | 你的 skill 或命令名稱 |
| `Elicitation`、`ElicitationResult` | MCP server 名稱 | 你配置的 MCP server 名稱 |
| `UserPromptSubmit`、`PostToolBatch`、`Stop`、`TeammateIdle`、`TaskCreated`、`TaskCompleted`、`WorktreeCreate`、`WorktreeRemove`、`CwdChanged`、`MessageDisplay` | 無 matcher 支援 | 每次觸發都 fire |

> 若你新增不支援的 matcher 給事件，會被靜默忽略。

---

## Hook Handler 類型

每個 `hooks` 陣列中的物件是 hook handler。有**五種類型**：

| 類型 | 描述 |
|:-----|:-----|
| **[Command hooks](#command-hook-詳細設定)** (`type: "command"`) | 執行 shell 命令。腳本從 stdin 接收事件的 JSON 輸入，通過退出碼和 stdout 通訊結果。 |
| **[HTTP hooks](#http-hook-詳細設定)** (`type: "http"`) | 將事件的 JSON 輸入作為 HTTP POST 請求送到 URL。端點通過回應 body 用相同的 [JSON 輸出格式](#json-輸出)通訊。 |
| **[MCP tool hooks](#mcp-tool-詳細設定)** (`type: "mcp_tool"`) | 在已連接的 [MCP server](https://code.claude.com/docs/en/mcp) 上呼叫工具。工具的文字輸出被當作 command-hook stdout 處理。 |
| **[Prompt hooks](#prompt-與-agent-hooks)** (`type: "prompt"`) | 將 prompt 送到 Claude 模型進行單輪評估。模型以 JSON 形式返回其決策。 |
| **[Agent hooks](#prompt-與-agent-hooks)** (`type: "agent"`) | 生成可以使用 Read、Grep、Glob 等工具的 subagent，在返回決策前驗證條件。**實驗性**。 |

所有匹配的 hooks **平行執行**。如果你在多個設定檔中定義相同的 handler，它只執行一次。

Handlers 在目前目錄中以 Claude Code 的環境執行。

---

## 常見欄位

這些欄位適用於所有 hook 類型：

| 欄位 | 必需 | 描述 |
|:-----|:-----|:-----|
| `type` | ✅ | `"command"`、`"http"`、`"mcp_tool"`、`"prompt"` 或 `"agent"` |
| `if` | ❌ | 權限規則語法過濾何時執行 hook，例如 `"Bash(git *)"` 或 `"Edit(*.ts)"`。hook 命令只在工具呼叫匹配模式時執行。**僅在工具事件上評估**：`PreToolUse`、`PostToolUse`、`PostToolUseFailure`、`PermissionRequest`、`PermissionDenied`。在其他事件上，帶 `if` 的 hook 永不執行。 |
| `timeout` | ❌ | 取消前的秒數。預設：`command`、`http`、`mcp_tool` 為 600；`prompt` 為 30；`agent` 為 60。`UserPromptSubmit` 將 `command`、`http`、`mcp_tool` 預設降低到 30，`MessageDisplay` 降低到 10。`SessionEnd` hooks 共享 1.5 秒預算；若你的設定設了更長的 per-hook `timeout`，Claude Code 將預算提高以匹配，最多 60 秒。 |
| `statusMessage` | ❌ | hook 執行時顯示的自訂 spinner 訊息 |
| `once` | ❌ | 若為 `true`，每個 session 執行一次然後移除。**僅對在 [skill frontmatter](#skills-和-agents-中的-hooks) 中宣告的 hooks 生效**；在設定檔和 agent frontmatter 中被忽略 |

### `if` 欄位的 Bash 匹配

| `if` 模式 | Bash 命令 | Hook 執行？ | 原因 |
|:----------|:----------|:----|:------|
| `Bash(git *)` | `FOO=bar git push` | ✅ | 前置賦值被剝離；`git push` 匹配 |
| `Bash(git *)` | `npm test && git push` | ✅ | 每個子命令都被檢查；`git push` 匹配 |
| `Bash(rm *)` | `echo $(rm -rf /)` | ✅ | `$()` 和反引號中的命令被檢查 |
| `Bash(rm *)` | `echo $(date)` | ❌ | 沒有子命令匹配 `rm *` |
| `Bash(git push *)` | `echo $(date)` | ✅ | 指定多於命令名稱的模式仍會對 `$()`、反引號或 `$VAR` 執行 hook |

> 過濾器在 Bash 命令無法解析時也會失敗開啟（執行你的 hook）。因為 `if` 過濾器是盡力而為，使用[權限系統](https://code.claude.com/docs/en/permissions)而非 hook 來強制硬性 allow 或 deny。

---

## Command Hook 詳細設定

除了[常見欄位](#常見欄位)外，command hooks 接受這些欄位：

| 欄位 | 必需 | 描述 |
|:-----|:-----|:-----|
| `command` | ✅ | 要執行的 shell 命令。搭配 `args` 時，是要直接生成的可執行檔。見 [Exec form 和 shell form](#exec-form-和-shell-form) |
| `args` | ❌ | 引數清單。當存在時，`command` 解析為可執行檔並直接以 `args` 作為引數向量生成，沒有 shell 涉及。 |
| `async` | ❌ | 若為 `true`，在背景執行而不阻擋。見 [在背景執行 hooks](#背景執行-hooks) |
| `asyncRewake` | ❌ | 若為 `true`，在背景執行並在 exit code 2 時喚醒 Claude。隱含 `async`。hook 的 stderr（或 stdout 如果 stderr 為空）作為系統提醒顯示給 Claude |
| `shell` | ❌ | 用於此 hook 的 shell。接受 `"bash"` 或 `"powershell"`。預設 `"bash"`，或在 Windows 上未安裝 Git Bash 時預設 `"powershell"` |

### Exec form 和 Shell form

Command hook 在 `args` 設定時以 exec form 執行，在 `args` 省略時以 shell form 執行。**當 hook 引用 [路徑佔位符](#路徑引用)時總是設 `args`**，因為每個元素作為一個引數傳遞無需引號。當你需要 pipes 或 `&&` 等 shell 功能時省略 `args`。

**Exec form** 在 `args` 存在時執行。Claude Code 將 `command` 解析為 `PATH` 上的可執行檔，並直接以 `args` 作為引數向量生成。**沒有 shell**，所以每個 `args` 元素作為一個引數完全按寫入傳遞，路徑佔位符（如 `${CLAUDE_PLUGIN_ROOT}`）作為純字串替換到 `command` 和每個 `args` 元素中。

**Shell form** 在 `args` 缺席時執行。`command` 字串傳遞給 shell：`sh -c`（macOS/Linux）、Git Bash（Windows），或當 Git Bash 未安裝時的 PowerShell。shell 標記化字串、展開變數、解釋 pipes、`&&`、重定向和 globs。

> 在 Windows 上，exec form 要求 `command` 解析為真實可執行檔（如 `.exe`）。npm、npx、eslint 等工具安裝在 `node_modules/.bin` 的 `.cmd` 和 `.bat` shim **不是**可執行檔，沒有 shell 無法生成。要以 exec form 執行它們，直接用 `node` 呼叫底層腳本，例如 `"command": "node", "args": ["${CLAUDE_PLUGIN_ROOT}/node_modules/eslint/bin/eslint.js"]`。

#### 範例：Node 腳本

```json
{
  "type": "command",
  "command": "node",
  "args": ["${CLAUDE_PLUGIN_ROOT}/scripts/format.js", "--fix"]
}
```

等效的 shell form 需要引號處理含空格或特殊字元的路徑：

```json
{
  "type": "command",
  "command": "node \"${CLAUDE_PLUGIN_ROOT}\"/scripts/format.js --fix"
}
```

> Plugin hooks 額外替換 [`${user_config.*}`](https://code.claude.com/docs/en/plugins-reference#user-configuration) 值，**僅在 exec form**：值作為純字串替換到 `command` 和每個 `args` 元素，所以沒有 shell 重新解析它。
>
> 在 shell-form plugin hook 中引用 `${user_config.*}` 的 `command` 會以[錯誤](https://code.claude.com/docs/en/errors#plugin-command-references-user-config)失敗。要從 shell-form hook 使用選項值，讀取 `$CLAUDE_PLUGIN_OPTION_<KEY>` 環境變數，或設 `args` 切換到 exec form。

---

## HTTP Hook 詳細設定

除了[常見欄位](#常見欄位)外，HTTP hooks 接受這些欄位：

| 欄位 | 必需 | 描述 |
|:-----|:-----|:-----|
| `url` | ✅ | 將 POST 請求送到的 URL |
| `headers` | ❌ | 作為鍵值對的額外 HTTP headers。值支援使用 `$VAR_NAME` 或 `${VAR_NAME}` 語法的環境變數插值。**只有 `allowedEnvVars` 中列出的變數會被解析** |
| `allowedEnvVars` | ❌ | 可以插值到 header 值中的環境變數名稱清單。引用未列出的變數會被替換為空字串。需要這個才能讓任何 env var 插值運作 |

Claude Code 將 hook 的 [JSON 輸入](#hook-輸入與輸出)作為 POST 請求 body 送出，`Content-Type: application/json`。回應 body 使用與 command hooks 相同的 [JSON 輸出格式](#json-輸出)。

#### 範例：發送 PreToolUse 到本地服務

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "http",
            "url": "http://localhost:8080/hooks/pre-tool-use",
            "timeout": 30,
            "headers": {
              "Authorization": "Bearer $MY_TOKEN"
            },
            "allowedEnvVars": ["MY_TOKEN"]
          }
        ]
      }
    ]
  }
}
```

> 錯誤處理與 command hooks 不同；見 [HTTP 回應處理](#http-回應處理)。

---

## MCP Tool Hook 詳細設定

除了[常見欄位](#常見欄位)外，MCP tool hooks 接受這些欄位：

| 欄位 | 必需 | 描述 |
|:-----|:-----|:-----|
| `server` | ✅ | 已配置 MCP server 的名稱。對於 [plugin-bundled server](https://code.claude.com/docs/en/mcp#plugin-provided-mcp-servers)，這是範圍名稱 `plugin::<server>`，如 `plugin:my-plugin:db`，而不是裸 server 金鑰。server 必須已連接；hook 永遠不會觸發 OAuth 或連接流程 |
| `tool` | ✅ | 要在該 server 上呼叫的工具名稱 |
| `input` | ❌ | 傳遞給工具的引數。字串值支援從 hook 的 [JSON 輸入](#hook-輸入與輸出)進行 `${path}` 替換，如 `"${tool_input.file_path}"` |

Claude Code 讀取工具的文字內容方式與讀取 command-hook stdout 相同，遵循 [exit code 0 下的解析規則](#退出碼-0)。如果命名的 server 未連接，或工具返回 `isError: true`，hook 會產生非阻擋錯誤並繼續執行。

> MCP tool hooks 在 Claude Code 連接到你的 MCP servers 後，每個 hook 事件都可用。`SessionStart` 和 `Setup` 通常在 servers 完成連接之前觸發，所以那些事件上的 hooks 應該在第一次執行時預期「未連接」錯誤。

#### 範例：寫入後呼叫 security_scan

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "mcp_tool",
            "server": "my_server",
            "tool": "security_scan",
            "input": { "file_path": "${tool_input.file_path}" }
          }
        ]
      }
    ]
  }
}
```

---

## Prompt 與 Agent Hooks

除了[常見欄位](#常見欄位)外，prompt 和 agent hooks 接受這些欄位：

| 欄位 | 必需 | 描述 |
|:-----|:-----|:-----|
| `prompt` | ✅ | 傳送給模型的 prompt 文字。使用 `$ARGUMENTS` 作為 hook 輸入 JSON 的佔位符。用反斜線逸出以包含字面文字：`\$1.00` 渲染為 `$1.00` |
| `model` | ❌ | 用於評估的模型。預設為快速模型 |

### 支援的事件類型

支援所有五種 hook 類型（`command`、`http`、`mcp_tool`、`prompt`、`agent`）的事件：

- `PermissionDenied`、`PermissionRequest`、`PostToolBatch`、`PostToolUse`、`PostToolUseFailure`、`PreToolUse`、`Stop`、`SubagentStop`、`TaskCompleted`、`TaskCreated`、`TeammateIdle`、`UserPromptExpansion`、`UserPromptSubmit`

支援 `command`、`http`、`mcp_tool` 但**不支援** `prompt` 或 `agent` 的事件：

- `ConfigChange`、`CwdChanged`、`DirectoryAdded`、`Elicitation`、`ElicitationResult`、`FileChanged`、`InstructionsLoaded`、`MessageDisplay`、`Notification`、`PostCompact`、`PreCompact`、`SessionEnd`、`StopFailure`、`SubagentStart`、`WorktreeCreate`、`WorktreeRemove`

`SessionStart` 和 `Setup` 只支援 `command` 和 `mcp_tool` hooks。

### Prompt Hooks

#### 配置

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Evaluate if Claude should stop: $ARGUMENTS. Check if all tasks are complete."
          }
        ]
      }
    ]
  }
}
```

| 欄位 | 必需 | 描述 |
|:-----|:-----|:-----|
| `type` | ✅ | 必須是 `"prompt"` |
| `prompt` | ✅ | 傳送給 LLM 的 prompt 文字。使用 `$ARGUMENTS` 作為 hook 輸入 JSON 的佔位符 |
| `model` | ❌ | 用於評估的模型。預設為快速模型 |
| `timeout` | ❌ | 逾時秒數。預設：30 |
| `continueOnBlock` | ❌ | 在適用的事件上，`true` 將 `ok: false` 原因回饋給 Claude 並繼續，而不是結束輪次。預設：`false` |

#### 回應格式

LLM 必須以 JSON 回應：

```json
{
  "ok": true | false,
  "reason": "Explanation for the decision",
  "impossible": true | false
}
```

| 欄位 | 描述 |
|:-----|:-----|
| `ok` | `true` 允許。對於 `false`，見每事件行為 |
| `reason` | 當 `ok` 為 `false` 時必需 |
| `impossible` | 選用。模型在判斷條件永遠無法滿足時與 `ok: false` 一起返回 |

`ok: false` 的效果取決於事件：

- `Stop` 和 `SubagentStop`：原因作為下一個指令回饋給 Claude 並繼續輪次，除非回應也設 `impossible: true`
- `PreToolUse`：工具呼叫被拒絕；預設輪次結束
- `PostToolUse`：預設輪次結束
- `PostToolBatch`、`UserPromptSubmit`、`UserPromptExpansion`：輪次結束
- `TaskCreated`、`PostToolUseFailure`：原因作為工具錯誤返回給 Claude 並繼續
- `PermissionRequest`：`ok: false` 無效
- `PermissionDenied`：`ok: false` 無效

#### 範例：停止前檢查任務完成

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "prompt",
            "prompt": "You are evaluating whether Claude should stop working. Context: $ARGUMENTS\n\nAnalyze the conversation and determine if:\n1. All user-requested tasks are complete\n2. Any errors need to be addressed\n3. Follow-up work is needed\n\nRespond with JSON: {\"ok\": true} to allow stopping, or {\"ok\": false, \"reason\": \"your explanation\"} to continue working.",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

### Agent Hooks

> ⚠️ **Agent hooks 是實驗性的**。行為和配置可能在未來版本中變更。生產工作流程請用 [command hooks](#command-hook-詳細設定)。

當驗證需要檢查檔案或執行命令時，使用 `type: "agent"` hooks。與 prompt hooks 進行單次 LLM 呼叫不同，**agent hooks 會生成可以使用工具的 subagent**。

Agent hooks 使用 `"ok"` / `"reason"` 回應格式，預設逾時較長（60 秒）且最多 50 個工具使用輪次。它們不支援 prompt-hook `impossible` 欄位。

#### 範例：測試通過前不停止

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "agent",
            "prompt": "Verify that all unit tests pass. Run the test suite and check the results. $ARGUMENTS",
            "timeout": 120
          }
        ]
      }
    ]
  }
}
```

> 當 hook 輸入資料本身就足夠做決定時使用 prompt hooks。當你需要根據程式碼庫的實際狀態驗證某些事情時使用 agent hooks。

---

## 路徑引用

使用這些佔位符來引用相對於專案或 plugin 根目錄的 hook 腳本，無論 hook 執行時的工作目錄如何：

| 變數 | 解析為 | 用途 |
|:-----|:-------|:-----|
| `${CLAUDE_PROJECT_DIR}` | session 開始的專案根目錄。Claude Code 也將此變數設在 [stdio MCP servers](https://code.claude.com/docs/en/mcp#option-3-add-a-local-stdio-server) 和 plugin LSP servers 的環境中 | 專案本地腳本和配置檔案 |
| `${CLAUDE_PLUGIN_ROOT}` | plugin 的安裝目錄，用於隨 plugin 打包的腳本。在每次 plugin 更新時變更 | 隨 plugin 打包的腳本、二進位檔和配置檔案 |
| `${CLAUDE_PLUGIN_DATA}` | plugin 的[持久資料目錄](https://code.claude.com/docs/en/plugins-reference#persistent-data-directory)，用於應該在 plugin 更新後存活的依賴和狀態 | 已安裝的依賴項 |

> ⚠️ **Worktrees 不同**：如果 Claude 在 session 期間進入 [worktree](https://code.claude.com/docs/en/worktrees)，Claude Code 將 `${CLAUDE_PROJECT_DIR}` 保持在原位，並以不同方式將 worktree 路徑傳遞給你的 hooks：
> - `${CLAUDE_PROJECT_DIR}` 仍指向 session 開始的專案根目錄
> - `cwd` 欄位在 hook 的 [輸入 JSON](#common-input-fields) 中是 worktree 根目錄

對任何引用路徑佔位符的 hook 偏好 [exec form](#exec-form-和-shell-form)。在 shell form 中，將每個佔位符包裝在雙引號中。

#### 範例：PostToolUse 跑 style checker

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/check-style.sh",
            "args": []
          }
        ]
      }
    ]
  }
}
```

---

## Skills 和 Agents 中的 Hooks

除了設定檔和 plugins，hooks 還可以在 [skills](./04-skills.md) 和 [subagents](./05-subagents.md) 中直接定義 frontmatter。

**生命周期差異**：
- **Subagent hooks**：只在該 subagent 執行期間執行，在它完成時被移除
- **Skill hooks**：在叫用 skill 時註冊，並在 session 的其餘時間繼續執行

> 當 agent 作為 subagent 通過 Agent 工具或 @-mention 生成時，frontmatter hooks 會觸發。
> 當 agent 作為主 session 通過 [`--agent`](#invoke-subagents-explicitly) 或 `agent` 設定執行時也會觸發。

**所有 [hook 事件](#hook-生命週期)都支援**。

#### 範例：Skill 定義的 PreToolUse

```yaml
---
name: secure-operations
description: Perform operations with security checks
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/security-check.sh"
---
```

> Subagents 在其 YAML frontmatter 中使用相同格式。
>
> 專案 skill 的 frontmatter hooks 遵循與 settings 檔中 hooks 相同的[工作區信任規則](#工作區信任)。
>
> 專案 subagent 的 frontmatter hooks 只在**接受 agent 檔案所在資料夾的工作區信任對話**後才執行。`-p` session 不算作接受。

---

## Hook 輸入與輸出

Command hooks 通過 **stdin** 接收 JSON 數據，通過 **退出碼**、**stdout** 和 **stderr** 通訊結果。HTTP hooks 接收相同的 JSON 作為 POST 請求 body，通過 HTTP 回應 body 通訊結果。

### 常見輸入欄位

Hook 事件接收這些欄位作為 JSON，除了每個 [hook 事件](#hook-生命週期)章節中記錄的特定欄位。對 command hooks，這個 JSON 通過 stdin 送達。對 HTTP hooks，它作為 POST 請求 body 送達。

| 欄位 | 描述 |
|:-----|:-----|
| `session_id` | 目前 session 識別碼 |
| `prompt_id` | 識別目前正在處理的使用者 prompt 的 UUID。符合 [OpenTelemetry 事件](https://code.claude.com/docs/en/monitoring-usage#event-correlation-attributes)上的 `prompt.id` 屬性，所以你可以將 hook 輸出與單個 prompt 的遙測相關聯。**v2.1.196+ 才存在** |
| `transcript_path` | 對話 JSON 的路徑。轉錄檔案是非同步寫入的，可能會滯後於記憶體中的對話 |
| `cwd` | hook 叫用時的目前工作目錄 |
| `permission_mode` | 目前的[權限模式](https://code.claude.com/docs/en/permissions#permission-modes) |
| `effort` | 帶有 `level` 欄位的物件 |
| `hook_event_name` | 觸發的事件名稱 |

當使用 `--agent` 或在 subagent 內執行時，附加兩個欄位：

| 欄位 | 描述 |
|:-----|:-----|
| `agent_id` | subagent 的唯一識別碼 |
| `agent_type` | Agent 名稱（如 `"Explore"` 或 `"security-reviewer"`） |

> 只有 [`SessionStart`](#sessionstart) hooks 可以接收 `model` 欄位，且不保證存在。沒有 `$CLAUDE_MODEL` 環境變數。

#### 範例：Bash 命令的 PreToolUse 輸入

```json
{
  "session_id": "abc123",
  "prompt_id": "550e8400-e29b-41d4-a716-446655440000",
  "transcript_path": "/home/user/.claude/projects/.../transcript.jsonl",
  "cwd": "/home/user/my-project",
  "permission_mode": "default",
  "hook_event_name": "PreToolUse",
  "tool_name": "Bash",
  "tool_input": {
    "command": "npm test",
    "description": "Run test suite",
    "timeout": 120000,
    "run_in_background": false
  },
  "tool_use_id": "toolu_01ABC123..."
}
```

### 退出碼輸出

Hook 命令的退出碼告訴 Claude Code 接下來該做什麼。Claude Code 從 stdout 讀取 [JSON 輸出欄位](#json-輸出)，而不僅是退出碼為 0 的情況。

#### 退出碼 0

**Exit 0** 表示成功，是當你列印 JSON 進行結構化控制時的預期退出碼。對大多數事件，stdout 寫入 debug 日誌但不顯示在 transcript 中。例外是 `UserPromptSubmit`、`UserPromptExpansion` 和 `SessionStart`，Claude Code 將純文字 stdout 作為 context 加入。

#### 退出碼 2

**Exit 2** 表示阻塞錯誤。在[可以阻擋](#退出碼-2-行為-每事件)的事件上，exit 2 阻擋**無論**你是否列印 JSON：即使是 `permissionDecision: "allow"` 的 JSON 也無法覆蓋它。Claude Code 仍然讀取 stdout 上的任何有效 [JSON 輸出](#json-輸出)。

#### 其他退出碼

**任何其他退出碼**本身不會阻擋大多數 hook 事件。發生什麼取決於你的 stdout：

- 帶有通過 schema 驗證的解析物件，事件使用標準決策模型：Claude Code 忽略退出碼，JSON 單獨決定結果
- 帶有未通過 schema 驗證的解析物件：與 [on exit 0](#退出碼-0) 相同的非阻擋錯誤
- 帶有 Claude Code 視為純文字的 stdout，或空 stdout：非阻擋錯誤

> 對於大多數 hook 事件，**exit code 2 是唯一通過代碼本身阻擋的退出碼**。如果你的 hook 旨在強制執行策略，使用 `exit 2`。
> 例外是 `WorktreeCreate`，任何非零退出碼都會中止 worktree 創建。

#### 退出碼 2 行為（每事件）

| Hook event | Can block? | What happens on exit 2 |
|:-----------|:----|:------------------------|
| `PreToolUse` | ✅ | 阻擋工具呼叫 |
| `PermissionRequest` | ❌ | 退出碼 2 不受尊重，權限流程不變 |
| `UserPromptSubmit` | ✅ | 阻擋 prompt 處理並清除 prompt |
| `UserPromptExpansion` | ✅ | 阻擋展開 |
| `Stop` | ✅ | 防止 Claude 停止，繼續對話 |
| `SubagentStop` | ✅ | 防止 subagent 停止 |
| `TeammateIdle` | ✅ | 防止 teammate 閒置 |
| `TaskCreated` | ✅ | 回復任務建立 |
| `TaskCompleted` | ✅ | 防止任務被標記為完成 |
| `ConfigChange` | ✅ | 阻擋配置變更生效（除了 `policy_settings`） |
| `StopFailure` | ❌ | 輸出和退出碼被忽略 |
| `PostToolUse` | ❌ | 將 stderr 顯示給 Claude；工具已執行 |
| `PostToolUseFailure` | ❌ | 將 stderr 顯示給 Claude；工具已失敗 |
| `PostToolBatch` | ✅ | 在下個模型呼叫前停止 agentic loop |
| `PermissionDenied` | ❌ | 退出碼和 stderr 被忽略 |
| `Notification` | ❌ | 退出碼和 stderr 被忽略 |
| `SubagentStart` | ❌ | 將 stderr 僅顯示給使用者 |
| `SessionStart` | ❌ | 將 stderr 僅顯示給使用者 |
| `Setup` | ❌ | 將 stderr 僅顯示給使用者 |
| `SessionEnd` | ❌ | 將 stderr 僅顯示給使用者 |
| `CwdChanged` | ❌ | 將 stderr 僅顯示給使用者 |
| `DirectoryAdded` | ❌ | stderr 進入 debug 日誌 |
| `FileChanged` | ❌ | 將 stderr 僅顯示給使用者 |
| `PreCompact` | ✅ | 阻擋 compaction |
| `PostCompact` | ❌ | 將 stderr 僅顯示給使用者 |
| `Elicitation` | ✅ | 拒絕 elicitation |
| `ElicitationResult` | ✅ | 阻擋回應（操作變為 decline） |
| `WorktreeCreate` | ✅ | 任何非零退出碼都會導致 worktree 創建失敗 |
| `WorktreeRemove` | ❌ | 失敗僅在 debug 模式下記錄 |
| `InstructionsLoaded` | ❌ | 退出碼被忽略 |
| `MessageDisplay` | ❌ | 顯示原始文字 |

#### 超時

達到 [`timeout`](#常見欄位) 的 `command`、`http` 或 `mcp_tool` hook 會被取消：Claude Code 丟棄 hook 的輸出，hook 不呈現決策。在 `PreToolUse` 上，兩種 hook 系列表現不同：

- **超時的 `command`、`http` 或 `mcp_tool` hook 不會阻擋工具呼叫**。呼叫透過正常權限流程繼續
- **超時的 [Agent SDK 回調 hook](https://code.claude.com/docs/en/agent-sdk/hooks) 會[阻擋工具呼叫](#pretooluse)**

### HTTP 回應處理

HTTP hooks 使用 HTTP 狀態碼和回應 body 而不是退出碼和 stdout。下面的結果適用於大多數事件；在 [per-event table](#退出碼-2-行為-每事件) 中有自己失敗合約的事件（如 `WorktreeCreate`）對失敗的 HTTP hook 也適用該合約：

- **帶空 body 的 2xx**：成功，等同於無輸出的 exit code 0
- **帶 JSON 物件 body 的 2xx**：使用與 command hooks 相同的 [JSON 輸出](#json-輸出) schema 解析
- **帶任何其他 body 的 2xx**（如純文字）：非阻擋錯誤
- **非 2xx 狀態**：非阻擋錯誤，繼續執行
- **連接失敗**：非阻擋錯誤，繼續執行
- **超時**：hook 被取消且不呈現決策，繼續執行

> 與 command hooks 不同，HTTP hooks 無法僅通過狀態碼發出阻擋錯誤信號。要阻擋工具呼叫或拒絕權限，用 2xx 回應與適當的決策欄位。

---

## JSON 輸出

退出碼只讓你阻擋或保持沉默，但 JSON 輸出給你更細粒度的控制。**不要用 exit code 2 阻擋，退出 0 並將 JSON 物件列印到 stdout**。

> 你的 hook 的 stdout **必須只包含 JSON 物件**。如果你的 shell profile 在啟動時列印文字，它可能會干擾 JSON 解析。

Hook 輸出字串（包括 `additionalContext`、`systemMessage` 和純 stdout）**上限為 10,000 個字元**。超過此限制的輸出會儲存到檔案並以預覽和檔案路徑替換。

### 通用 JSON 欄位

| 欄位 | 預設 | 描述 |
|:-----|:-----|:-----|
| `continue` | `true` | 若為 `false`，Claude 在 hook 執行後完全停止處理。優先於任何事件特定決策欄位 |
| `stopReason` | 無 | 當 `continue` 為 `false` 時顯示給使用者的訊息 |
| `systemMessage` | 無 | 顯示給使用者的警告訊息 |
| `terminalSequence` | 無 | Claude Code 代表你發出的終端跳脫序列，如桌面通知、視窗標題或鈴聲。限制為 OSC `0`/`1`/`2`/`9`/`99`/`777` 和 BEL |

> `suppressOutput` 欄位沒有效果 — Claude Code 接受此欄位但不執行操作。成功 hook 的 stdout 永遠不會顯示在 transcript 中。

#### 範例：完全停止 Claude

```json
{ "continue": false, "stopReason": "Build failed, fix errors before continuing" }
```

### 發送終端通知

Hooks 在沒有控制終端的情況下執行，所以直接向 `/dev/tty` 寫入跳脫序列會失敗。改為在 `terminalSequence` 欄位返回跳脫序列，Claude Code 通過其自己的終端寫入路徑為你發出它。

該欄位接受一字串或多個允許的跳脫序列：

- OSC `0`、`1`、`2`：視窗和圖示標題
- OSC `9`：iTerm2、ConEmu、Windows Terminal 和 WezTerm 通知
- OSC `99`：Kitty 通知
- OSC `777`：urxvt、Ghostty 和 Warp 通知
- Bare BEL

> Claude Code 只在**互動式 session** 中寫入序列，且僅在其介面在螢幕上時。在非互動式模式（`-p` flag）和 Agent SDK 中，它會忽略此欄位。

#### 範例：從 Notification hook 觸發桌面通知

```bash
#!/bin/bash
# Notification hook: 當 Claude Code 需要注意時 ping 桌面
input=$(cat)
title="Claude Code"
body=$(jq -r '.message // "Needs your attention"' <<<"$input")
seq=$(printf '\033]777;notify;%s;%s\007' "$title" "$body")
jq -nc --arg seq "$seq" '{terminalSequence: $seq}'
```

### 為 Claude 新增上下文

`additionalContext` 欄位將字串從你的 hook 傳遞到 Claude 的 context 視窗。Claude Code 將字串包裝在系統提醒中並將其插入到觸發 hook 的對話中。

> 在 `hookSpecificOutput` 內返回 `additionalContext`，連同事件名稱一起：

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PostToolUse",
    "additionalContext": "This file is generated. Edit src/schema.ts and run `bun generate` instead."
  }
}
```

提醒出現的位置取決於事件：

- `SessionStart`、`Setup`、`SubagentStart`：在對話開始，第一個 prompt 之前
- `UserPromptSubmit` 和 `UserPromptExpansion`：與提交的 prompt 並列
- `PreToolUse`、`PostToolUse`、`PostToolUseFailure`、`PostToolBatch`：在工具結果旁
- `Stop` 和 `SubagentStop`：在輪次末尾

> 將文字寫成事實陳述而不是祈使句系統指令。諸如「部署目標是生產」之類的措辭讀起來像專案資訊。以頻外系統命令為框架的文字可能會觸發 Claude 的 prompt-injection 防禦。

### 決策控制

不是每個事件都支援通過 JSON 阻擋或控制行為。能這樣做的事件各自使用一組不同的欄位來表達該決策：

| Events | 決策模式 | 關鍵欄位 |
|:-------|:--------|:--------|
| `UserPromptSubmit`、`UserPromptExpansion`、`PostToolUse`、`PostToolUseFailure`、`PostToolBatch`、`Stop`、`SubagentStop`、`ConfigChange`、`PreCompact` | 頂層 `decision` | `decision: "block"`、`reason` |
| `TeammateIdle`、`TaskCompleted` | 退出碼或 `continue: false` | Exit code 2 阻擋動作 |
| `TaskCreated` | 退出碼或頂層 `decision` | Exit code 2 或 `decision: "block"` |
| `PreToolUse` | `hookSpecificOutput` | `permissionDecision`（allow/deny/ask/defer） |
| `PermissionRequest` | `hookSpecificOutput` | `decision.behavior`（allow/deny） |
| `PermissionDenied` | `hookSpecificOutput` | `retry: true` |
| `WorktreeCreate` | 路徑返回 | 命令 hook 在 stdout 列出路徑；HTTP hook 返回 `hookSpecificOutput.worktreePath` |
| `Elicitation` | `hookSpecificOutput` | `action`（accept/decline/cancel） |
| `ElicitationResult` | `hookSpecificOutput` | `action`（accept/decline/cancel） |
| `MessageDisplay` | `hookSpecificOutput` | `displayContent` 替換螢幕上顯示的文字 |
| `SessionStart`、`Setup`、`SubagentStart` | 僅 context | `hookSpecificOutput.additionalContext` |
| `WorktreeRemove`、`Notification`、`SessionEnd`、`PostCompact`、`InstructionsLoaded`、`StopFailure`、`CwdChanged`、`DirectoryAdded`、`FileChanged` | 無 | 沒有決策控制。用於日誌記錄或清理等副作用 |

> 少數事件也可以重寫內容而不僅僅是允許或阻擋：
> - `PreToolUse`：`updatedInput` 直接在 `hookSpecificOutput` 下替換工具的引數
> - `PermissionRequest`：`updatedInput` 在 `decision` 物件內
> - `PostToolUse`：`updatedToolOutput` 替換工具的結果
> - `UserPromptSubmit`：不能替換 prompt；只能注入 `additionalContext`

---

## 所有 Hook 事件詳解

### SessionStart

當 Claude Code 啟動新 session 或恢復現有 session 時執行。用於載入開發 context，如現有問題或程式碼庫的最近變更，或設定環境變數。對於不需要腳本的靜態 context，使用 [CLAUDE.md](https://code.claude.com/docs/zh-TW/memory)。

> SessionStart 在每個 session 都執行，所以讓這些 hooks 保持快速。只支援 `type: "command"` 和 `type: "mcp_tool"` hooks。

| Matcher | When it fires |
|:--------|:--------------|
| `startup` | 新 session |
| `resume` | `--resume`、`--continue` 或 `/resume` |
| `clear` | `/clear` |
| `compact` | 自動或手動 compaction |
| `fork` | 從現有 session 分叉的新 session |

**決策控制** — 你可以返回這些事件特定欄位：

| 欄位 | 描述 |
|:-----|:-----|
| `additionalContext` | 在對話開始時新增到 Claude context 的字串，在第一個 prompt 之前 |
| `initialUserMessage` | 用作 session 第一個使用者訊息的字串 |
| `sessionTitle` | 設定 session 標題，與 `/rename` 效果相同 |
| `watchPaths` | 在此 session 期間要監視 [FileChanged](#filechanged) 事件的絕對路徑陣列 |
| `reloadSkills` | Boolean。當為 `true` 時，Claude Code 在 SessionStart hooks 完成後重新掃描 skill 目錄 |

#### 範例：設置 session 標題

```json
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "Current branch: feat/auth-refactor\nUncommitted changes: src/auth.ts, src/login.tsx\nActive issue: #4211 Migrate to OAuth2",
    "sessionTitle": "auth-refactor"
  }
}
```

#### 持久化環境變數

SessionStart hooks 可以訪問 `CLAUDE_ENV_FILE` 環境變數，它提供一個檔案路徑，你可以在其中持久化環境變數供後續 Bash 命令使用。

```bash
#!/bin/bash

if [ -n "$CLAUDE_ENV_FILE" ]; then
  echo 'export NODE_ENV=production' >> "$CLAUDE_ENV_FILE"
  echo 'export DEBUG_LOG=true' >> "$CLAUDE_ENV_FILE"
fi

exit 0
```

### PreToolUse

在 Claude 創建工具參數後、處理工具呼叫前執行。匹配工具名稱：`Bash`、`PowerShell`、`Edit`、`Write`、`Read`、`Glob`、`Grep`、`Agent`、`WebFetch`、`WebSearch`、`AskUserQuestion`、`ExitPlanMode`、和任何 [MCP 工具名稱](#match-mcp-tools)。

> ⚠️ `PreToolUse` 只在 Claude 呼叫工具時執行。檔案用 `@` 在 prompt 中引用是**不**通過任何工具呼叫新增的：Claude Code 在構建 prompt 時插入它們的內容，所以 PreToolUse hook 不會為它們觸發，包括匹配 `Read` 的 hooks。

> `PreToolUse` 也不會為 [`EndConversation`](https://code.claude.com/docs/en/tools-reference#endconversation-tool-behavior) 觸發。

#### 決策控制

| 欄位 | 描述 |
|:-----|:-----|
| `permissionDecision` | `"allow"` 跳過權限提示；`"deny"` 防止工具呼叫；`"ask"` 提示使用者確認；`"defer"` 在非互動模式優雅退出 |
| `permissionDecisionReason` | 對 `"allow"` 和 `"ask"` 顯示給使用者但不給 Claude；對 `"deny"` 顯示給 Claude；對 `"defer"` 忽略 |
| `updatedInput` | 在執行前修改工具的輸入參數。替換整個輸入物件 |
| `additionalContext` | 與工具結果並列新增到 Claude context 的字串。當 `permissionDecision` 為 `"defer"` 時被忽略 |

當多個 PreToolUse hooks 返回不同決策時，優先級是 `deny` > `defer` > `ask` > `allow`。

#### 延後工具呼叫以供稍後使用

`"defer"` 適用於將 `claude -p` 作為子進程執行並讀取其 JSON 輸出的整合，例如 Agent SDK app 或構建在 Claude Code 之上的自訂 UI。它讓該調用進程在工具呼叫處暫停 Claude，通過其自己的介面收集輸入，並從離開的地方恢復。

> `"defer"` 只在 Claude 在該輪次進行**單個工具呼叫**時有效。如果 Claude 一次進行多個工具呼叫，`"defer"` 會被帶警告忽略並且工具透過正常權限流程繼續。

### PermissionRequest

當 Claude Code 即將要求你權限時執行。在無法顯示提示的 session 中（如非互動模式中的背景 subagents），Claude Code 仍然執行這些 hooks，如果沒有 hook 返回決策，會拒絕工具呼叫。

匹配工具名稱，值與 PreToolUse 相同。

**決策控制** — 你的 hook 腳本可以返回帶有這些事件特定欄位的 `decision` 物件：

| 欄位 | 描述 |
|:-----|:-----|
| `behavior` | `"allow"` 授予權限，`"deny"` 拒絕 |
| `updatedInput` | 僅對 `"allow"`：在執行前修改工具的輸入參數 |
| `updatedPermissions` | 僅對 `"allow"`：要套用的[權限更新條目](#permission-update-entries)陣列 |
| `message` | 僅對 `"deny"`：告訴 Claude 為什麼權限被拒絕 |
| `interrupt` | 僅對 `"deny"`：若為 `true`，停止 Claude |

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PermissionRequest",
    "decision": {
      "behavior": "allow",
      "updatedInput": {
        "command": "npm run lint"
      }
    }
  }
}
```

### PostToolUse

在工具成功完成後立即執行。

> 匹配更廣泛時，當工具名稱不是正確的過濾器：
> - 若要在任何工具成功完成後執行 hook，省略 `matcher` 或將其設為 `"*"`
> - 若要在特定檔案在磁碟上變更時執行 hook，無論是什麼寫入，使用 [FileChanged](#filechanged)

#### 決策控制

| 欄位 | 描述 |
|:-----|:-----|
| `decision` | `"block"` 將 `reason` 新增到工具結果旁邊。Claude 仍然看到原始輸出；要替換它，使用 `updatedToolOutput` |
| `reason` | 當 `decision` 為 `"block"` 時顯示給 Claude 的解釋 |
| `additionalContext` | 與工具結果並列新增到 Claude context 的字串 |
| `classifierContext` | 對 [auto mode](https://code.claude.com/docs/en/permission-modes#eliminate-prompts-with-auto-mode) 分類器的簡短註解 |
| `updatedToolOutput` | 在發送給 Claude 之前替換工具的輸出。值必須匹配工具的輸出形狀 |

> `updatedToolOutput` 只改變 Claude 看到的內容。hook 觸發時工具已經執行，所以任何寫入的檔案、執行的命令或發送的網路請求都已生效。

### Stop

當主要的 Claude Code agent 完成回應時執行。如果由於使用者中斷而停止則不執行。API 錯誤觸發 [StopFailure](#stopfailure)。

> [`/goal`](https://code.claude.com/docs/en/goal) 命令是會話範圍的基於 prompt 的 Stop hook 的內建快捷方式。

#### 輸入

除了常見輸入欄位外，Stop hooks 接收 `stop_hook_active`、`last_assistant_message`、`background_tasks` 和 `session_crons` 欄位。

`stop_hook_active` 欄位在 Claude Code 已作為 stop hook 結果繼續時為 `true`。檢查此值或處理 transcript 以避免在永遠不會解決的條件上阻擋。Claude Code 在連續 8 次阻擋後覆寫 hook 並結束輪次。

#### 決策控制

| 欄位 | 描述 |
|:-----|:-----|
| `decision` | `"block"` 防止 Claude 停止 |
| `reason` | 當 `decision` 為 `"block"` 時必需。告訴 Claude 為什麼應該繼續 |
| `hookSpecificOutput.additionalContext` | 給 Claude 的非錯誤反饋。對話繼續以便 Claude 可以對其採取行動，但與 `decision: "block"` 不同，它在 transcript 中顯示為 hook feedback 而不是 hook error |

```json
{
  "decision": "block",
  "reason": "Must be provided when Claude is blocked from stopping"
}
```

### Notification

當 Claude Code 發送通知時執行。匹配通知類型。

| Matcher | 當什麼時候觸發 |
|:--------|:--------------|
| `permission_prompt` | Claude 需要你批准工具使用且提示已等待約 6 秒 |
| `idle_prompt` | Claude 約 60 秒前完成回應且你尚未輸入 |
| `auth_success` | 認證完成 |
| `elicitation_dialog` | MCP server 打開 elicitation 表格 |
| `elicitation_url_dialog` | MCP server 要求你打開瀏覽器 URL |
| `elicitation_complete` | MCP elicitation 表格已提交或關閉 |
| `elicitation_response` | MCP elicitation 回應已發回 server |
| `agent_needs_input` | 背景 session 開始等待你的輸入 |
| `agent_completed` | 背景 session 完成或失敗 |

> Notification hooks **無法阻擋或修改通知**。Claude Code 丟棄其 `systemMessage` 和 `continue` 欄位，但仍發出 [`terminalSequence`](#發送終端通知)。Notification hooks 旨在用於轉發通知到外部服務等副作用。

### SubagentStart / SubagentStop

SubagentStart 觸發時機：通過 Agent 工具生成 Claude Code subagent 時。支援 matchers 按 agent 類型名稱過濾。

SubagentStop 觸發時機：Claude Code subagent 已完成回應時。匹配 agent 類型，值與 SubagentStart 相同。

> SubagentStop hooks 使用與 [Stop hooks](#stop) 相同的決策控制格式。

### WorktreeCreate / WorktreeRemove

WorktreeCreate 從 `claude --worktree`、從使用 `isolation: "worktree"` 的 subagent，或為 Claude Code 隔離在自己 worktree 中的背景 session 建立 worktree 時執行。配置 WorktreeCreate hook 會**替換預設的 git 行為**。

> 因為 hook 完全替換預設行為，[`.worktreeinclude`](https://code.claude.com/docs/en/worktrees#copy-gitignored-files-into-worktrees) 不被處理。如果你需要將本地配置檔案（如 `.env`）複製到新 worktree，請在 hook 腳本中執行。

**hook 必須返回已建立 worktree 目錄的路徑**。Claude Code 將此路徑用作隔離 session 的工作目錄。

- **Command hooks** (`type: "command"`)：將路徑作為 stdout 最後一個非空行列印
- **HTTP hooks** (`type: "http"`)：回應 body 返回 `{ "hookSpecificOutput": { "hookEventName": "WorktreeCreate", "worktreePath": "/absolute/path" } }`

### FileChanged

當被監視的檔案在磁碟上變更時執行。Claude Code 使用檔案系統監視器偵測變更，所以**無論是什麼更改了檔案都會執行 hook**：`Edit` 或 `Write` 工具呼叫、Claude 用 `Bash` 執行的腳本，或完全是 Claude Code 外部的進程。常見用途是在專案配置檔案變更時重新載入環境變數。

該事件的 `matcher` 有兩個作用：
- **建立監視清單**：值按 `|` 分割，每個段作為工作目錄中的字面檔名註冊，所以 `".envrc|.env"` 監視正好那兩個檔案
- **過濾哪些 hooks 執行**：當被監視的檔案變更時，相同的值使用標準 [matcher 規則](#matcher-模式)根據變更檔案的 basename 過濾哪些 hook 組執行

> 要監視無法提前命名的檔案，從 hook 返回 [`watchPaths`](#filechanged-output) 以動態更新監視清單。

#### 範例：規範化 data.csv 的行尾

```json
{
  "hooks": {
    "FileChanged": [
      {
        "matcher": "data.csv",
        "hooks": [
          {
            "type": "command",
            "command": "/path/to/normalize-line-endings.sh"
          }
        ]
      }
    ]
  }
}
```

`/path/to/normalize-line-endings.sh`：

```bash
#!/bin/bash
FILE=$(jq -r .file_path)
if grep -q $'\r$' "$FILE"; then
  perl -pi -e 's/\r$//' "$FILE"
fi
```

### Elicitation

當 MCP server 在任務中途請求使用者輸入時執行。預設情況下，Claude Code 顯示互動式對話框供使用者回應。Hooks 可以**攔截此請求並以程式化方式回應**，完全跳過對話框。

matcher 欄位匹配 MCP server 名稱。

#### 輸出

要以程式化方式回應而不顯示對話框，返回帶有 `hookSpecificOutput` 的 JSON 物件：

```json
{
  "hookSpecificOutput": {
    "hookEventName": "Elicitation",
    "action": "accept",
    "content": {
      "username": "alice"
    }
  }
}
```

| 欄位 | 值 | 描述 |
|:-----|:---|:-----|
| `action` | `accept`、`decline`、`cancel` | 是否接受、拒絕或取消請求 |
| `content` | 物件 | 要提交的表格欄位值。僅在 `action` 為 `accept` 時使用 |

Exit code 2 拒絕 elicitation。Claude Code 不會在任何地方顯示你的 stderr 訊息。

---

## 背景執行 Hooks

預設情況下，hooks 阻擋 Claude 的執行直到它們完成。對於長時間運行的任務（如部署、測試套件或外部 API 呼叫），設定 `"async": true` 以在背景執行 hook 而 Claude 繼續工作。

> Async hooks **無法阻擋或控制** Claude 的行為：回應欄位如 `decision`、`permissionDecision` 和 `continue` 沒有效果，因為它們會控制的動作已經完成。

### 配置 Async Hook

新增 `"async": true` 到 command hook 的配置以在背景執行而不阻擋 Claude。此欄位僅在 `type: "command"` hooks 上可用。

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "/path/to/run-tests.sh",
            "async": true,
            "timeout": 120
          }
        ]
      }
    ]
  }
}
```

`timeout` 欄位設置背景進程的最大時間（以秒為單位）。如果未指定，async hooks 使用與 sync hooks 相同的 10 分鐘預設。

> Claude Code 只在 session 執行期間遞送 async hook 的結果：
> - 在帶有 `-p` flag 的[非互動模式](https://code.claude.com/docs/en/headless)中，Claude Code 在 teardown 時終止任何仍在運行的 async hook
> - 如果你的 hook 的工作必須在 `claude -p` session 之外存活，請從中啟動完全分離的進程

### 範例：檔案變更後跑測試

`.claude/hooks/run-tests-async.sh`：

```bash
#!/bin/bash
# run-tests-async.sh

# 從 stdin 讀取 hook 輸入
INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

# 只對原始檔案跑測試
if [[ "$FILE_PATH" != *.ts && "$FILE_PATH" != *.js ]]; then
  exit 0
fi

# 跑測試並通過 additionalContext 向 Claude 報告結果
RESULT=$(npm test 2>&1)
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
  MSG="Tests passed after editing $FILE_PATH"
else
  MSG="Tests failed after editing $FILE_PATH: $RESULT"
fi
jq -nc --arg msg "$MSG" '{hookSpecificOutput: {hookEventName: "PostToolUse", additionalContext: $msg}}'
```

`.claude/settings.json`：

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/run-tests-async.sh",
            "args": [],
            "async": true,
            "timeout": 300
          }
        ]
      }
    ]
  }
}
```

### 限制

- Hook 輸出在下個對話輪次遞送
- 每個執行創建一個獨立的背景進程。多次觸發相同 async hook 沒有去重

---

## 安全性考量

### 免責聲明

> ⚠️ **Command hooks 以你的完整使用者權限執行 shell 命令**。它們可以修改、刪除或訪問你的使用者帳戶可訪問的任何檔案。在將 hook 命令新增到配置之前，**審查並測試所有 hook 命令**。

### 工作區信任

Claude Code 在執行任何來自設定檔的 hook 之前檢查工作區信任。信任取決於 session 類型：

- **互動式 session**：Claude Code 從**每個**設定檔（包括你自己的 `~/.claude/settings.json`）擱置 hook，直到你接受該資料夾的[工作區信任對話](https://code.claude.com/docs/en/permissions#project-allow-rules-and-workspace-trust)
- **`-p` 或 SDK session**：Claude Code 永遠不顯示對話框，將資料夾視為已信任，所以 hooks 從 repo 的 `.claude/settings.json` 提交時在從未信任的資料夾中執行

> 在對從未編寫的 repo 透過 `claude -p` 編寫腳本之前，**審查其 `.claude/` 設定檔**，從 [`--bare`](https://code.claude.com/docs/en/headless#start-faster-with-bare-mode) 開始，或用 `--settings '{"disableAllHooks": true}'` 為該次執行關閉 hooks。

### 安全性最佳實踐

撰寫 hooks 時牢記這些做法：

- **驗證和清理輸入**：永遠不要盲目信任輸入數據
- **始終引用 shell 變數**：使用 `"$VAR"` 而非 `$VAR`
- **阻擋路徑遍歷**：檢查 `..` 在檔案路徑中
- **使用絕對路徑**：為腳本指定完整路徑
- **跳過敏感檔案**：避免 `.env`、`.git/`、金鑰等

---

## PowerShell on Windows

在 Windows 上，你可以透過在 command hook 上設定 `"shell": "powershell"` 在 PowerShell 中執行個別 hook。Claude Code 自動偵測 `pwsh.exe`（PowerShell 7 及更高版本的可執行檔），並對 Windows PowerShell 5.1 回退到 `powershell.exe`。

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "shell": "powershell",
            "command": "Write-Host 'File written'"
          }
        ]
      }
    ]
  }
}
```

要從 PowerShell shell-form 命令引用專案根目錄，寫 `${CLAUDE_PROJECT_DIR}` 或 `$env:CLAUDE_PROJECT_DIR`。

> ⚠️ 不要在 PowerShell hook 中寫裸 `$CLAUDE_PROJECT_DIR` 拼寫。PowerShell 將其解析為未定義的本地變數並解析為 `$null`，這會讓腳本路徑沒有專案根前綴。

#### 範例

```json
{
  "type": "command",
  "shell": "powershell",
  "command": "& \"$env:CLAUDE_PROJECT_DIR\\.claude\\hooks\\check.ps1\""
}
```

---

## Debug Hooks

Hook 執行詳情（包括哪些 hook 匹配、它們的退出碼以及完整的 stdout 和 stderr）寫入 debug 日誌檔案。用 `claude --debug-file <路徑>` 將日誌寫入已知位置，或運行 `claude --debug` 並讀取 `~/.claude/debug/<session-id>.txt` 中的日誌。`--debug` flag 不會列印到終端。

對於更細粒度的 hook 匹配詳情，設定 `CLAUDE_CODE_DEBUG_LOG_LEVEL=verbose` 以查看額外的日誌行，如 hook matcher 計數和查詢匹配。

---

## 疑難排解

### Hook 未觸發

**症狀**：Hook 已配置但從不執行。

- 執行 `/hooks` 並確認 hook 出現在正確的事件下
- 檢查 matcher 模式精確匹配工具名稱（區分大小寫）
- 驗證你觸發了正確的事件類型：`PreToolUse` 在工具執行前觸發，`PostToolUse` 在之後

### Hook 輸出錯誤

**症狀**：你在 transcript 中看到「PreToolUse hook error: ...」訊息。

- 你的腳本意外地退出了非零代碼。透過管道傳送範例 JSON 手動測試：
  ```bash
  echo '{"tool_name":"Bash","tool_input":{"command":"ls"}}' | ./my-hook.sh
  echo $?
  ```
- 如果看到「command not found」，使用絕對路徑或 `${CLAUDE_PROJECT_DIR}` 引用腳本
- 如果看到「jq: command not found」，安裝 `jq` 或使用 Python/Node.js 進行 JSON 解析
- 如果腳本根本沒有運行，使其可執行：`chmod +x ./my-hook.sh`

### `/hooks` 顯示未配置 hook

**症狀**：你編輯了設定檔但 hook 沒有出現在功能表中。

- 檔案編輯通常自動被檔案監視器拾取。如果幾秒後仍未出現，檔案監視器可能漏掉了該變更：重啟你的 session 以強制重新載入
- 驗證你的 JSON 有效：不允許尾隨逗號和註解
- 確認設定檔位於正確位置：`.claude/settings.json` 用於專案 hooks，`~/.claude/settings.json` 用於全域 hooks

### Stop Hook 達到阻擋上限

**症狀**：Claude 繼續工作而不是停止，然後以 Stop hook 阻擋太多次的警告結束輪次。

Claude Code 在連續 8 次阻擋而沒有進展後覆寫 Stop hook。你的 hook 腳本需要檢查它是否已經觸發了延續。從 JSON 輸入解析 `stop_hook_active` 欄位，如果為 `true` 則提前退出：

```bash
#!/bin/bash
INPUT=$(cat)
if [ "$(echo "$INPUT" | jq -r '.stop_hook_active')" = "true" ]; then
  exit 0  # 允許 Claude 停止
fi
# ... 你其餘的 hook 邏輯
```

如果你的 hook 合法地需要超過八次迭代才能收斂，使用 [`CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`](https://code.claude.com/docs/en/env-vars) 提高上限。

### Hook JSON 沒有效果

**症狀**：你的 hook 列印有效的 JSON，但決策沒有生效，transcript 中也沒有錯誤。

當 Claude Code 運行 shell-form command hook（沒有 `args`）時，它在 macOS 和 Linux 上生成 `sh -c`，在 Windows 上生成 Git Bash，如果預設情況下未安裝 Git Bash 則為 PowerShell。這個 shell 是非互動式的，但 Git Bash 和某些配置（如 `BASH_ENV` 指向 `~/.bashrc`）仍會 source 你的 profile。如果該 profile 包含無條件的 `echo` 語句，輸出會被前置到你的 hook 的 JSON：

```text
Shell ready on arm64
{"decision": "block", "reason": "Not allowed"}
```

合併後的輸出不再以 `{` 開頭，所以 Claude Code 將所有 stdout 視為純文字並忽略 JSON。要修復，在你的 shell profile 中包裝 echo 語句，使其只在互動式 shell 中運行：

```bash
# In ~/.zshrc or ~/.bashrc
if [[ $- == *i* ]]; then
  echo "Shell ready"
fi
```

`$-` 變數包含 shell flags，`i` 表示互動式。Hooks 在非互動式 shell 中運行，所以 echo 會被跳過。

### 除錯技巧

按 **Ctrl+O** 打開 transcript 視圖以檢查 hook 執行的結果：

- **成功運行**：你什麼也看不到，除非 hook 的 JSON 呈現某些東西，如 `systemMessage` 或 Stop hook feedback
- **阻塞錯誤**：在大多數事件上你看到 hook 的反饋
- **非阻塞錯誤**：動作繼續，你看到 `hook error` 通知

---

## 速查表

### Hook 設定位置

| 用途 | 位置 |
|:-----|:-----|
| 全域個人 hooks | `~/.claude/settings.json` |
| 專案共享 hooks | `.claude/settings.json` |
| 專案本地 hooks | `.claude/settings.local.json` |
| Plugin hooks | `<plugin>/hooks/hooks.json` |
| Skill hooks | 在 `SKILL.md` frontmatter |
| Subagent hooks | 在 agent 檔案 frontmatter |

### 常用 Hook 模式

```json
// 編輯後自動格式化
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [{"type": "command", "command": "prettier --write $FILE"}]
      }
    ]
  }
}

// 阻擋危險命令
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{"type": "command", "command": "./block-rm.sh"}]
      }
    ]
  }
}

// Session 開始時載入 context
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup",
        "hooks": [{"type": "command", "command": "echo 'Loading project context...'"}]
      }
    ]
  }
}

// 桌面通知
{
  "hooks": {
    "Notification": [
      {
        "matcher": "",
        "hooks": [{"type": "command", "command": "osascript -e 'display notification \"Need attention\"'"}]
      }
    ]
  }
}
```

### 退出碼速查

| 退出碼 | 意義 |
|:-------|:-----|
| `0` | 成功，無決策（或透過 stdout JSON 表達決策） |
| `2` | 阻塞錯誤（適用於大多數事件） |
| 其他 | 取決於 stdout — 純文字 = 非阻塞錯誤；有效 JSON = 該事件使用 JSON 決策 |

---

## 下一步

- 想學寫 subagent（隔離執行的代理）→ 閱讀 [05-subagents.md](./05-subagents.md)
- 學習如何打包成 plugin → 閱讀 [02-plugins.md](./02-plugins.md)
- 想從別人的 marketplace 安裝 hooks → 閱讀 [07-discover-plugins.md](./07-discover-plugins.md)
