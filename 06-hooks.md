# Hooks 自動化指南

> 📖 系列：Claude Code Plugin 完整學習系列 #06
> 🌐 原文：[code.claude.com/docs/zh-TW/hooks](https://code.claude.com/docs/zh-TW/hooks)
> 📅 整理日期：2026 / 01
> 🎯 適用版本：Claude Code v2.1.x

## 本章你會學到

從零到精通的 Hook 自動化設計

- 🧠 **Hook 基礎**：理解確定性 vs 判斷性
- ⚙️ **設定與位置**：6 個位置決定範圍
- 🔧 **5 種 Handler 類型**：從簡單到強大
- 📊 **輸入/輸出與退出碼**：資料格式與決策控制
- 📋 **重要事件詳解**：PreToolUse、PostToolUse、Stop
- 🔒 **安全性與最佳實踐**：避免踩坑
- 🐛 **疑難排解**：實戰中會遇到的狀況
- 🎯 **練習題與實戰**：鞏固所學

## Part 1: Hook 基礎概念

理解確定性 vs 判斷性

## 什麼是 Hook？

Hook 是事件驅動的自動化腳本，在特定事件發生時自動執行。

| 特性 | Hook | Skill |
|:----|:-----|:------|
| 觸發 | 事件自動 | 使用者手動或自動 |
| 用途 | 確定性操作 | 判斷性任務 |
| 範例 | 自動格式化、阻擋危險命令 | 程式碼審查、解釋程式碼 |

## Hook 生命週期：3 個節奏

| 節奏 | 說明 |
|:-----|:-----|
| Pre | 工具執行**前**（可阻擋）|
| Post | 工具執行**後**（可記錄）|
| Session | 開始/結束時 |

## Hook 解析流程

從觸發到執行的步驟：

1. 事件發生（PreToolUse 等）
2. 讀取匹配的 hook 配置
3. 準備輸入（環境變數 + JSON）
4. 執行 hook handler
5. 處理輸出（退出碼 + JSON）

## Part 2: Hook 設定與位置

6 個位置決定範圍

## Hook 設定的 6 個位置

| 位置 | 路徑 | 範圍 |
|:-----|:-----|:-----|
| User settings | `~/.claude/settings.json` | 個人 |
| Project settings | `.claude/settings.json` | 專案 |
| Local settings | `.claude/settings.local.json` | 本地（gitignored）|
| Plugin | `<plugin>/hooks/hooks.json` | Plugin |
| Skill | `<skill>/SKILL.md` frontmatter | 單一 skill |
| Subagent | `<subagent>.md` frontmatter | 單一 subagent |

## Matcher 模式詳解

`matcher` 決定 hook 在哪些工具觸發時執行：

```json
{
  "PreToolUse": [
    {
      "matcher": "Write|Edit|MultiEdit",
      "hooks": [...]
    }
  ]
}
```

| 模式 | 匹配 |
|:-----|:-----|
| `Write` | 單一工具 |
| `Write\|Edit` | 多個工具 |
| `Write.*` | 正則表達式 |
| `*` | 全部工具 |

## 常見 Matcher 範例

| Matcher | 用途 |
|:--------|:-----|
| `Bash` | 所有 bash 命令 |
| `Write\|Edit` | 檔案寫入/編輯 |
| `Read\|Glob\|Grep` | 唯讀操作 |
| `mcp__.*` | MCP 工具 |
| `WebFetch\|WebSearch` | 網路操作 |

## Part 3: 5 種 Hook Handler 類型

從簡單到強大

## Hook Handler 5 種類型

| 類型 | 用途 |
|:-----|:-----|
| `command` | 執行 shell 命令 |
| `http` | HTTP POST 請求 |
| `mcp_tool` | 呼叫 MCP 工具 |
| `prompt` | 送出 prompt 給 LLM |
| `agent` | 委派給 subagent |

## Command Hook 詳解

```json
{
  "PreToolUse": [
    {
      "matcher": "Bash",
      "hooks": [
        {
          "type": "command",
          "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/check-rm.sh",
          "timeout": 30
        }
      ]
    }
  ]
}
```

環境變數可用：
- `${CLAUDE_PROJECT_DIR}`：當前專案目錄
- `${CLAUDE_PLUGIN_ROOT}`：Plugin 根目錄
- `${TOOL_INPUT}`：工具輸入（JSON）

## HTTP、MCP Tool、Prompt Hooks

```json
{
  "hooks": [
    {
      "type": "http",
      "url": "https://api.example.com/hook",
      "headers": {"Authorization": "Bearer TOKEN"}
    },
    {
      "type": "mcp_tool",
      "tool": "notify_slack",
      "args": {"channel": "#alerts"}
    },
    {
      "type": "prompt",
      "prompt": "分析這個工具呼叫是否安全"
    }
  ]
}
```

## Part 4: Hook 輸入/輸出與退出碼

資料格式與決策控制

## Hook 輸入：JSON 格式

Hook 接收 stdin 的 JSON 輸入：

```json
{
  "session_id": "abc123",
  "transcript_path": "/path/to/transcript",
  "cwd": "/home/user/project",
  "hook_event_name": "PreToolUse",
  "tool_name": "Bash",
  "tool_input": {
    "command": "rm -rf /tmp/foo"
  }
}
```

## 退出碼語意

| 退出碼 | 語意 |
|:-------|:-----|
| `0` | 成功，繼續執行 |
| `2` | 阻擋（PreToolUse）|
| 其他 | 非阻擋錯誤，記錄警告 |

```bash
#!/bin/bash
# check-rm.sh
if [[ "$TOOL_INPUT" =~ rm\ -rf ]]; then
  echo "禁止 rm -rf" >&2
  exit 2  # 阻擋執行
fi
exit 0  # 允許
```

## JSON 決策控制

除了退出碼，hook 可用 JSON 提供更精細的控制：

```json
{
  "decision": "block",
  "reason": "禁止刪除操作",
  "continue": false,
  "stopReason": "安全性阻擋"
}
```

| 欄位 | 用途 |
|:-----|:-----|
| `decision` | `block` 或 `approve` |
| `reason` | 顯示給使用者 |
| `continue` | 是否繼續 |
| `stopReason` | 停止原因 |

## 決策優先級

決策衝突時的優先級：

1. **退出碼 2** 永遠最高（block）
2. **JSON decision: block** 次高
3. **JSON decision: approve** 最低
4. **退出碼 0** = 默認通過

## Part 5: 重要事件詳解

PreToolUse、PostToolUse、Stop

## PreToolUse：工具執行前

```json
{
  "PreToolUse": [
    {
      "matcher": "Bash",
      "hooks": [
        {
          "type": "command",
          "command": "validate-command.sh"
        }
      ]
    }
  ]
}
```

用途：
- 阻擋危險命令
- 注入環境變數
- 自動確認

## PostToolUse：工具成功後

```json
{
  "PostToolUse": [
    {
      "matcher": "Edit|Write|MultiEdit",
      "hooks": [
        {
          "type": "command",
          "command": "format-file.sh"
        }
      ]
    }
  ]
}
```

用途：
- 自動格式化
- 觸發測試
- 記錄變更

## Stop Hook：Claude 完成時

```json
{
  "Stop": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "notify-completion.sh"
        }
      ]
    }
  ]
}
```

用途：
- 發送完成通知
- 自動 commit
- 觸發下游流程

## SessionStart 與 SessionEnd

```json
{
  "SessionStart": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "setup-env.sh"
        }
      ]
    }
  ],
  "SessionEnd": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "cleanup.sh"
        }
      ]
    }
  ]
}
```

## Notification 事件：通知觸發

```json
{
  "Notification": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "send-desktop-notification.sh"
        }
      ]
    }
  ]
}
```

觸發時機：
- Claude 等待使用者輸入
- Claude 完成任務
- 錯誤發生

## 背景執行 Hooks（async）

```json
{
  "PostToolUse": [
    {
      "matcher": "Edit",
      "hooks": [
        {
          "type": "command",
          "command": "run-tests-async.sh",
          "async": true
        }
      ]
    }
  ]
}
```

> async hook 不阻擋主流程，背景執行

## 為 Claude 新增上下文

用 `hookSpecificOutput` 為 Claude 注入上下文：

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PostToolUse",
    "additionalContext": "此檔案已被自動格式化"
  }
}
```

## 發送終端通知

```bash
#!/bin/bash
# notify.sh
if command -v terminal-notifier &> /dev/null; then
  terminal-notifier -title "Claude Code" \
    -message "任務完成" -sound "default"
fi
```

## Part 6: 安全性與最佳實踐

避免踩坑

## 安全性：認真對待 Hooks

> ⚠️ Hook 自動執行，要當作 production code 對待

**原則**：
- 假設 hook 會被惡意輸入觸發
- 不要信任 stdin 內容
- 用 whitelist 而非 blacklist
- 加上 timeout 避免 hang

## Hook 除錯技巧

| 技巧 | 用途 |
|:-----|:-----|
| `claude --debug` | 啟用除錯模式 |
| `echo` 到 stderr | 記錄到 transcript |
| `exit 0` 隔離問題 | 確認是 hook 還是工具問題 |
| `set -x` shell | 顯示執行命令 |

## PowerShell on Windows

```json
{
  "hooks": [
    {
      "type": "command",
      "command": "powershell -File .claude/hooks/check.ps1"
    }
  ]
}
```

PowerShell 注意事項：
- 用 `.ps1` 副檔名
- 設定 ExecutionPolicy
- 路徑分隔符用 `\`

## 5 個常見的 Hook 模式

| 模式 | 用途 |
|:-----|:-----|
| 自動格式化 | PostToolUse + prettier |
| 阻擋危險命令 | PreToolUse + exit 2 |
| 自動測試 | PostToolUse + npm test |
| 通知完成 | Stop + 系統通知 |
| 記錄變更 | PostToolUse + git diff |

## 實戰：阻擋 rm -rf 完整實作

```bash
#!/bin/bash
# .claude/hooks/block-rm.sh
INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // ""')

if echo "$COMMAND" | grep -E "rm\s+(-[a-z]*r[a-z]*f|--recursive)" > /dev/null; then
  echo "🚫 禁止 rm -rf 操作：$COMMAND" >&2
  exit 2
fi
exit 0
```

## 實戰：編輯後背景跑測試

```bash
#!/bin/bash
# .claude/hooks/run-tests.sh
INPUT=$(cat)
FILE=$(echo "$INPUT" | jq -r '.tool_input.file_path // ""')

if [[ "$FILE" =~ \.(py|js|ts)$ ]]; then
  npm test -- --findRelatedTests "$FILE" &
  exit 0
fi
exit 0
```

## Hooks 在 Skill 和 Subagent 中

可在 SKILL.md frontmatter 定義 skill 專用 hook：

```markdown
---
name: deploy-check
description: 部署前檢查
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: ".claude/hooks/check-deploy.sh"
---
```

## Part 7: 常見問題與疑難排解

實戰中會遇到的狀況

## 疑難排解速查表

| 問題 | 排查方向 |
|:-----|:---------|
| Hook 沒觸發 | 檢查 matcher 與事件名稱 |
| Hook 阻擋所有操作 | 檢查退出碼（不要總是 exit 2）|
| Timeout | 增加 timeout 或優化 script |
| 環境變數空 | 檢查 `${CLAUDE_PROJECT_DIR}` 路徑 |
| JSON 解析失敗 | 用 `jq` 驗證 stdin |

## 除錯工作流

1. **確認觸發**：用 `echo` 到 stderr 記錄
2. **隔離問題**：簡化 hook 到 `exit 0`
3. **驗證 stdin**：`cat | jq` 確認輸入格式
4. **檢查退出碼**：手動執行看輸出
5. **啟用 debug**：`claude --debug` 詳細輸出

## 退出碼 + JSON 速查表

| 情境 | 退出碼 | JSON |
|:-----|:-------|:-----|
| 允許 | `0` | `{}` 或 `{"continue": true}` |
| 阻擋 | `2` | `{"decision": "block", "reason": "..."}` |
| 警告 | `1` | `{}` |
| 注入 context | `0` | `{"hookSpecificOutput": {...}}` |

## Part 8: 練習題與實戰

鞏固所學

## 練習題：5 個實作挑戰

1. **自動格式化**：建立 PostToolUse hook 在每次編輯後跑 prettier
2. **阻擋危險命令**：建立 PreToolUse hook 阻擋 `rm -rf`、`sudo`、`chmod 777`
3. **自動測試**：建立 async hook 在 .py 檔變更後跑 pytest
4. **完成通知**：建立 Stop hook 在 Claude 完成時發送桌面通知
5. **Skill 專用 hook**：在 SKILL.md frontmatter 內定義 skill 專用 hook

## Hooks 與其他元件的組合

| 組合 | 用途 |
|:-----|:-----|
| Hook + Skill | Skill 觸發後自動執行 hook |
| Hook + Subagent | Subagent 任務完成後執行 hook |
| Hook + Plugin | Plugin 載入時設定 hook |

## Hook 設計模式總結

| 模式 | 關鍵 |
|:-----|:-----|
| 觀察者 | 只記錄不阻擋（exit 0）|
| 守門員 | 阻擋危險操作（exit 2）|
| 自動化 | 自動執行任務（async）|
| 通知 | 觸發外部通知 |
| 注入 | 為 Claude 提供 context |

## Hook 對決策的精細控制

| 控制層級 | 工具 |
|:---------|:-----|
| 退出碼 | 簡單 block / pass |
| JSON decision | 含 reason 的 block |
| JSON hookSpecificOutput | 注入 context |
| JSON continue | 控制流程 |

## 完整 Hook 速查表

```json
{
  "PreToolUse": [
    {
      "matcher": "Bash",
      "hooks": [
        {
          "type": "command",
          "command": "check.sh",
          "timeout": 30
        }
      ]
    }
  ],
  "PostToolUse": [
    {
      "matcher": "Edit|Write",
      "hooks": [
        {
          "type": "command",
          "command": "format.sh",
          "async": true
        }
      ]
    }
  ],
  "Stop": [
    {
      "hooks": [
        {"type": "command", "command": "notify.sh"}
      ]
    }
  ]
}
```

## Hook 開發最佳實踐

1. **冪等性**：多次執行結果相同
2. **Timeout**：總是設定 timeout
3. **錯誤處理**：用 `set -e` 在 shell 開頭
4. **Log 到 stderr**：不要污染 stdout
5. **測試先**：用簡單測試驗證後再用

## 重點回顧

- Hook 是事件驅動的自動化腳本
- 6 個設定位置（User、Project、Plugin、Skill、Subagent、CLI）
- 5 種 Handler 類型：command、http、mcp_tool、prompt、agent
- 退出碼 + JSON 兩種控制方式
- PreToolUse 可阻擋、PostToolUse 自動執行
- async 模式不阻擋主流程
- 安全性：當作 production code

## 系列回顧：你已完成的學習

從 00 到 06 你已經學會：

- 00：系列總覽 + 7 個元件
- 01：Plugin Marketplace 完整攻略
- 02：Plugin 開發從零到發布
- 03：Plugin 技術參考完整規格
- 04：Skills 從基礎到精通
- 05：Subagents 自訂與管理
- 06：Hooks 自動化（本章）

## Hooks 大師之路 🎣

從初學者到專家的里程碑

- 🌱 **初學者**：建立 3 個簡單 hook（自動格式化、阻擋 rm -rf、完成通知）
- 🌿 **進階**：建立 5 種 handler 類型組合
- 🌳 **專家**：建立可重用的 hook library 並文件化
- 🏆 **大師**：貢獻 hook 設計指南並訓練團隊
