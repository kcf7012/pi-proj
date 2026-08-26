# Subagents 自訂指南

> 📖 系列：Claude Code Plugin 完整學習系列 #05
> 🌐 原文：[code.claude.com/docs/zh-TW/sub-agents](https://code.claude.com/docs/zh-TW/sub-agents)
> 📅 整理日期：2026 / 01
> 🎯 適用版本：Claude Code v2.1.x

## 本章你會學到

從零到精通的 Subagent 設計攻略

- 🧠 **Subagent 基礎**：核心概念與使用時機
- 🏗 **內建 Subagents**：Claude Code 內建的 4 種助手
- 🛠 **建立第一個 Subagent**：3 步驟完成
- 📋 **配置 Subagent**：frontmatter 完整欄位
- ⚡ **選擇模型與控制能力**：模型路由 + 工具限制
- 🔀 **使用 Subagents**：叫用、平行、深度、context
- 💡 **範例與常見模式**：4 個實戰範例 + 3 個核心模式

## Part 1: 什麼是 Subagent

獨立 context 的專門助手

## Subagent 核心概念

Subagent 是 Claude Code 內**獨立 context** 執行的子任務代理

- **獨立 context**：不污染主對話的 context
- **可配置模型**：用不同的模型處理不同任務
- **工具限制**：限制可用的工具，避免意外操作
- **可委派**：主對話可委派任務給 subagent

## 什麼時候該用 Subagent？

| 適合用 | 不適合用 |
|:------|:--------|
| 大量輸出（測試、日誌）| 需要即時對話 |
| 隔離 context（避免污染主對話）| 簡單任務（直接做更快）|
| 用專門模型處理（成本最佳化）| 需要跨多輪的互動 |
| 平行任務（同時執行多個）| 任務需要主對話的 context |

## Part 2: 內建 Subagents

Claude Code 內建的 4 種助手

## 4 種內建 Subagents

| 名稱 | 用途 | 工具 |
|:-----|:-----|:-----|
| `general-purpose` | 一般任務（搜尋、分析）| 全部 |
| `statusline-setup` | 設定 statusline | Bash, Read |
| `Explore` | 探索程式碼結構 | Read, Grep, Glob |
| `Plan` | 規劃複雜任務 | Read, Grep, Glob |

> 內建 subagent 隨時可用，不需建立檔案

## 限制與停用內建 Subagent

可在 `settings.json` 限制內建 subagent：

```json
{
  "permissions": {
    "deny": ["Task(Explore)"]
  }
}
```

或在 subagent frontmatter 用 `disallowedTools` 限制特定工具。

## Part 3: 建立第一個 Subagent

3 步驟：描述 → 檔案 → 叫用

## 建立 Subagent 的 3 個步驟

從概念到運作

### 1. 描述用途

決定 subagent 的角色與限制

### 2. 建立 .md 檔

放在 `.claude/agents/<name>.md`

### 3. 委派任務

主對話用 Task 工具呼叫

## 範例：code-improver subagent

```markdown
---
name: code-improver
description: 改進程式碼品質
tools: Read, Edit, Grep
model: sonnet
---

你是程式碼改進專家。閱讀檔案並：
1. 找出可改進的地方
2. 套用最佳實踐
3. 保持向後相容
4. 寫清楚修改理由
```

呼叫：`Task(code-improver, "改進 src/api/users.ts")`

## Part 4: 配置 Subagent

frontmatter 16 個欄位全解析

## 5 種 Subagent 範圍

Subagent 可放在 5 個位置：

| 位置 | 路徑 | 範圍 |
|:-----|:-----|:-----|
| User | `~/.claude/agents/` | 個人 |
| Project | `.claude/agents/` | 專案 |
| Plugin | `<plugin>/agents/` | Plugin |
| CLI | `--agents` flag | 當前 session |
| Local | `--agents-dir` | 任意目錄 |

## Frontmatter 欄位速查表

| 欄位 | 必填 | 描述 |
|:-----|:-----|:-----|
| `name` | 是 | subagent 名稱 |
| `description` | 是 | subagent 用途說明 |
| `tools` | 否 | 可用工具（如 `Read, Grep, Glob`）|
| `model` | 否 | 指定模型 |
| `permissionMode` | 否 | 權限模式 |
| `disallowedTools` | 否 | 禁止的工具 |

## Part 5: 選擇模型與控制能力

模型路由 + 工具限制

## 選擇模型：4 種方式

```markdown
---
model: sonnet  # 明確指定
# 或
model: opus
# 或
model: inherit  # 繼承主對話
# 或
model: haiku   # 用 haiku（便宜快速）
```

| 模型 | 用途 |
|:-----|:-----|
| `opus` | 複雜推理 |
| `sonnet` | 一般任務 |
| `haiku` | 簡單任務（成本低）|

## 工具限制：白名單與黑名單

```markdown
---
# 白名單（只能用這些工具）
tools: Read, Grep, Glob

# 黑名單（不能用這些工具）
disallowedTools: Bash, Write, Edit
```

## 限制可生成的 Subagent 類型

用 `disallowedTools` 限制 subagent 不能呼叫 Task：

```markdown
---
tools: Read, Grep, Glob
disallowedTools: Task
---
```

> 這防止 subagent 遞迴產生子 subagent

## 預載入 Skills 與持久記憶

```markdown
---
skills:
  - code-review
  - test-runner
memory: project
```

- `skills`：subagent 啟動時自動載入
- `memory: project`：subagent 可存取專案記憶

## Part 6: 條件式規則與 Hooks

用 PreToolUse 動態控制

## 條件式規則：唯讀 DB 查詢

```markdown
---
tools: Bash
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: |
            if [[ "$TOOL_INPUT" =~ rm|delete|drop ]]; then
              echo "禁止刪除操作"
              exit 1
            fi
```

> 用 hook 強制 subagent 只能執行唯讀操作

## Part 7: 使用 Subagents

叫用、平行、深度、context

## 3 種叫用 Subagent 的方式

```markdown
# 1. Task 工具
Task(code-improver, "改進 users.ts")

# 2. 自然語言（Claude 自動選擇 subagent）
「用 code-improver 改進 users.ts」

# 3. /<subagent-name> slash command
/code-improver 改進 users.ts
```

## 平行、深度與 Context 管理

| 場景 | 策略 |
|:-----|:-----|
| 多個獨立任務 | 平行 Task 呼叫 |
| 任務很複雜 | 增加深度（depth） |
| 需要主對話 context | 用 `context: shared` |
| 隔離的純任務 | 用 `context: fork` |

```markdown
# 平行呼叫 3 個 subagent
TaskAsync(Explore, "找 auth 相關檔案")
TaskAsync(Explore, "找 API 相關檔案")
TaskAsync(Explore, "找測試檔案")
```

## Part 8: 範例與常見模式

4 個實戰範例 + 3 個核心模式

## 4 個實戰範例 Subagent

| 範例 | 用途 | 模型 |
|:-----|:-----|:-----|
| `code-improver` | 改進程式碼 | sonnet |
| `test-runner` | 執行測試 | haiku |
| `doc-writer` | 生成文件 | sonnet |
| `security-auditor` | 安全審查 | opus |

## 3 個常見模式

| 模式 | 用途 |
|:-----|:-----|
| 探索 → 規劃 → 執行 | 複雜任務分階段 |
| 平行探索 | 同時搜尋多個面向 |
| 隔離測試 | 不污染主對話執行測試 |

## Subagent 輸出掃描

Claude Code 會在 Subagent 報告中掃描關鍵資訊：

- 完成的任務
- 發現的問題
- 建議的改進
- 遇到的錯誤

> 主對話會根據這些資訊決定下一步動作

## 疑難排解速查

| 問題 | 排查方向 |
|:-----|:---------|
| Subagent 沒被呼叫 | 檢查 name 是否正確 |
| Subagent context 空 | 檢查 `context` 設定 |
| Subagent 無法用工具 | 檢查 `tools` 白名單 |
| Subagent 結果不符預期 | 檢查 description 是否清楚 |

## 重點回顧

- Subagent 是獨立 context 的子任務代理
- 用 frontmatter 配置模型、工具、權限
- 5 種範圍：User、Project、Plugin、CLI、Local
- 用 Task 工具、自然語言、slash command 叫用
- 用 hook 強制 subagent 行為
- 平行呼叫適合獨立任務
- 4 個實戰範例 + 3 個核心模式

- 🎯 立刻：建立一個簡單的 test-runner subagent
- 📚 30 分鐘：翻完 frontmatter 16 個欄位
- 🛠 2 小時：建立團隊專用的 code-improver
- 🚀 一週：把 subagent 包裝到 plugin 分享
