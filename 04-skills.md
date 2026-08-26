# Skills 完整指南

> 📖 系列：Claude Code Plugin 完整學習系列 #04
> 🌐 原文：[code.claude.com/docs/zh-TW/skills](https://code.claude.com/docs/zh-TW/skills)
> 📅 整理日期：2026 / 01
> 🎯 適用版本：Claude Code v2.1.x

## 本章你會學到

從零到精通的 Skill 設計攻略

- 🧠 **基礎概念**：理解 skill 是什麼、4 個位置
- 📋 **Frontmatter**：所有可用欄位與動態內容
- ⚡ **進階功能**：工具權限、Subagent、視覺輸出
- 🎯 **下一步**：把所學變成實戰

## Part 1: Skill 基礎概念

理解 skill 是什麼

## 什麼是 Skill？

Skill 是一個 SKILL.md 檔案，包含：

- **YAML frontmatter**：描述 skill 的 metadata
- **Markdown 內容**：skill 的指示與說明
- **支援檔案**（選用）：範例、腳本、模板

```markdown
---
description: 程式碼審查清單
---

審查程式碼時檢查：
1. 程式碼組織
2. 錯誤處理
3. 安全性
```

## Skill 的兩種角色

| 角色 | 觸發方式 | 用途 |
|:-----|:---------|:-----|
| User-invocable | `/skill-name` | 使用者手動觸發 |
| Model-invocable | Claude 自動選擇 | 任務相關自動呼叫 |

| Frontmatter | user-invocable | model-invocable |
|:------------|:--------------|:----------------|
| 預設 | ✅ | ✅ |
| `disable-model-invocation: true` | ✅ | ❌ |
| `user-invocable: false` | ❌ | ✅ |

## 快速開始：建立你的第一個 Skill

建立步驟：

```bash
mkdir -p ~/.claude/skills/code-review
```

在 `~/.claude/skills/code-review/SKILL.md`：

```markdown
---
description: 程式碼審查清單
---

審查程式碼時檢查：
1. 程式碼組織
2. 錯誤處理
3. 安全性
```

呼叫：`/code-review`

## Part 2: Skill 位置與範圍

4 個層級與優先級規則

## Skill 的 4 個位置

Skill 可放在 4 個位置，優先級由高到低：

| 位置 | 路徑 | 用途 |
|:-----|:-----|:-----|
| Enterprise | `/etc/claude-code/skills/` | 組織級部署 |
| Personal | `~/.claude/skills/` | 個人使用 |
| Project | `.claude/skills/` | 專案共享 |
| Plugin | `<plugin>/skills/` | Plugin 內附 |

> 較高優先級的 skill 會覆蓋較低優先級的同名 skill

## 即時變更偵測

修改 skill 檔案後**無需重啟 Claude Code**，會自動偵測變更。

可用 `/reload-plugins` 手動重新載入（如果是 Plugin 內的 skill）。

## Part 3: Frontmatter 完整語法

所有可用欄位

## Frontmatter 完整欄位（上）

基本欄位

| 欄位 | 必填 | 類型 | 描述 |
|:-----|:-----|:-----|:-----|
| `description` | 是 | string | skill 簡短描述（Claude 自動決定呼叫時用）|
| `name` | 否 | string | skill 顯示名稱 |
| `allowed-tools` | 否 | string | 允許使用的工具（如 `Read, Grep`）|

## Frontmatter 完整欄位（下）

進階欄位

| 欄位 | 必填 | 類型 | 描述 |
|:-----|:-----|:-----|:-----|
| `user-invocable` | 否 | boolean | 是否可手動觸發（預設 true）|
| `disable-model-invocation` | 否 | boolean | 是否禁止 Claude 自動觸發 |
| `model` | 否 | string | 指定模型（如 `sonnet`）|
| `context` | 否 | string | 執行環境（`fork` 為 Subagent）|

## Frontmatter 實戰範例

```markdown
---
description: 完整程式碼審查，包含安全性與效能分析
allowed-tools: Read, Grep, Glob, Bash
disable-model-invocation: true
model: sonnet
---

審查以下程式碼並提供詳細報告：
1. 安全性漏洞
2. 效能瓶頸
3. 可讀性改進
4. 測試覆蓋率
```

## Part 4: 字串替換與動態內容

`$ARGUMENTS` 與 `` !`command` ``

## 可用的字串替換

| 字串 | 取代為 | 用途 |
|:-----|:-------|:-----|
| `$ARGUMENTS` | 使用者輸入 | 動態內容 |
| `${CLAUDE_SESSION_ID}` | session ID | 追蹤 |
| `$FILE_PATH` | 當前檔案 | 上下文 |

```markdown
---
description: 解釋選取的程式碼
---

解釋以下檔案的內容：
$ARGUMENTS
```

呼叫：`/explain src/main.py` → `$ARGUMENTS` = `src/main.py`

## 傳遞引數給 Skill

執行 skill 時可在名稱後加引數：

```bash
/explain src/main.py
/explain src/api/users.ts --verbose
```

skill 內用 `$ARGUMENTS` 接收所有引數。

## 動態上下文注入：!`command`

`` !`command` `` 在 skill 載入時執行 shell 命令，並將輸出插入 skill 內容：

```markdown
---
description: 總結當前變更
---

!`git diff HEAD`

請總結以上變更並標記風險。
```

> Claude Code 會在 skill 載入時執行 `git diff HEAD` 並將輸出替換到 `` !`command` `` 位置

## Part 5: 支援檔案與目錄結構

建立可維護的 skill

## 新增支援檔案

Skill 目錄可以包含支援檔案：

```
my-skill/
├── SKILL.md
├── examples/
│   └── sample.md
├── scripts/
│   └── validate.sh
└── templates/
    └── template.md
```

在 SKILL.md 內引用：

```markdown
參考 `examples/sample.md` 的格式。
執行 `scripts/validate.sh` 驗證。
```

## Part 6: 控制誰能叫用 Skill

user-invocable 與 disable-model-invocation

## 控制誰能叫用 Skill

| Frontmatter | 行為 |
|:------------|:-----|
| `user-invocable: true`（預設）| 使用者可手動 `/skill-name` 觸發 |
| `user-invocable: false` | 只能由 Claude 自動觸發 |
| `disable-model-invocation: true` | 禁止 Claude 自動觸發 |

```markdown
---
description: 部署到正式環境
user-invocable: true
disable-model-invocation: true
---

執行部署流程：
1. 確認所有測試通過
2. 確認 staging 環境無錯誤
3. 執行部署命令
```

> 部署類 skill 應該 `disable-model-invocation: true`，避免 Claude 自動觸發

## 隱藏與覆寫 Skill 可見性

Skill 名稱衝突時的優先級：

1. Plugin 內 skill 會覆蓋同名的 Personal skill
2. Project skill 會覆蓋 Personal skill
3. Enterprise skill 永遠最高優先級

> 隱藏：將 skill 加上 `user-invocable: false`

## Part 7: 進階功能

工具權限、Subagent、視覺輸出

## 為 Skill 預先批准工具

用 `allowed-tools` 預先批准工具，skill 執行時不需要再次詢問：

```markdown
---
description: 程式碼搜尋
allowed-tools: Read, Grep, Glob
---

搜尋程式碼：
$ARGUMENTS
```

可用的工具：
- `Read` - 讀取檔案
- `Write` - 寫入檔案
- `Edit` - 編輯檔案
- `Bash` - 執行命令
- `Grep` - 搜尋內容
- `Glob` - 檔案匹配

## 在 Subagent 中執行 Skill

用 `context: fork` 讓 skill 在 Subagent 隔離環境執行：

```markdown
---
description: 大量測試輸出（隔離 context）
context: fork
model: sonnet
---

執行所有測試並回報結果：
$ARGUMENTS
```

> 適合產生大量輸出的 skill（如測試執行、文件生成）

## 視覺輸出：生成互動式 HTML

Skill 可以生成 HTML 並開啟在瀏覽器：

```markdown
---
description: 生成互動式視覺化
allowed-tools: Write, Bash
---

生成 HTML 視覺化並開啟瀏覽器。
```

skill 內可以寫入 `.html` 檔案，Claude Code 會自動偵測並提示開啟。

## Part 8: 技能生命週期與評估

如何知道 skill 有效？

## Skill 內容生命週期

| 階段 | 動作 |
|:-----|:-----|
| 建立 | 寫 SKILL.md 並測試 |
| 使用 | 在 Claude Code 中呼叫 |
| 評估 | 檢查輸出是否符合預期 |
| 改進 | 根據使用經驗調整 |
| 分享 | 透過 Plugin 發布 |

## 評估與改進 Skill

**評估指標**：
- 呼叫頻率（使用次數 / 時間）
- 成功率（呼叫後是否達到預期結果）
- 使用者滿意度（呼叫後是否需要修正）

**改進技巧**：
- description 要精準（決定 Claude 何時自動觸發）
- 加入範例（讓 Claude 知道如何呼叫）
- 限制工具（減少意外操作）

## 疑難排解

| 問題 | 排查方向 |
|:-----|:---------|
| Skill 沒出現 | 檢查 SKILL.md 位置與 frontmatter |
| Claude 不自動呼叫 | 檢查 `disable-model-invocation` |
| `$ARGUMENTS` 空 | 檢查引數是否正確傳遞 |
| `` !`command` `` 沒執行 | 檢查命令權限 |

## 分享 Skills 給其他人

三種分享方式：

1. **Git repo**：把 skill 目錄 push 到 Git，分享連結
2. **Plugin**：包裝成 plugin，透過 marketplace 發布
3. **直接複製**：把 skill 目錄複製到對方的 `~/.claude/skills/`

## 常用 Frontmatter 模式速查

| 模式 | Frontmatter |
|:-----|:-------------|
| 純手動觸發 | `disable-model-invocation: true` |
| 純自動觸發 | `user-invocable: false` |
| 隔離執行 | `context: fork` |
| 限制工具 | `allowed-tools: Read, Grep` |

## Skills vs 其他元件

| 元件 | 觸發 | 用途 |
|:-----|:-----|:-----|
| Skill | `/skill-name` 或自動 | 可重用的知識 |
| Agent | 委派任務 | 隔離的子任務 |
| Hook | 事件觸發 | 自動化腳本 |
| Command | `/command-name` | 命令模板 |

## 實戰：30 分鐘建立你的第一個實用 Skill

30 分鐘建立一個 git commit 檢查 skill：

```bash
mkdir -p ~/.claude/skills/git-check
```

`~/.claude/skills/git-check/SKILL.md`：

```markdown
---
description: 檢查 git commit 是否符合規範
allowed-tools: Bash
---

執行以下檢查：
1. 確認 commit message 有 50 字以內摘要
2. 確認有詳細說明 body
3. 確認所有測試通過
```

## 實戰：建立團隊多 Skill Plugin

把多個 skill 包裝成 plugin：

```
team-plugin/
├── .claude-plugin/plugin.json
└── skills/
    ├── code-review/
    ├── test-runner/
    └── deploy-check/
```

`plugin.json`：

```json
{
  "name": "team-plugin",
  "version": "1.0.0"
}
```

## Part 9: 下一步行動

把所學變成實戰

## 練習題：5 個實作挑戰

1. **基本 skill**：建立一個 `/format` skill 格式化選取的程式碼
2. **帶引數**：建立 `/explain <file>` skill 解釋檔案
3. **動態內容**：建立 `` !`git status` `` skill 總結 git 狀態
4. **Subagent**：建立 `context: fork` skill 執行大量測試
5. **Plugin 包裝**：把 3 個 skill 包裝成 plugin

## 重點回顧

- Skill 是可重用的 SKILL.md 檔案
- 4 個位置：Enterprise、Personal、Project、Plugin
- Frontmatter 決定 skill 行為
- `$ARGUMENTS` 接收引數
- `` !`command` `` 動態執行命令
- `allowed-tools` 預先批准工具
- `context: fork` 隔離執行
- 用 Plugin 分享給團隊

## Skills 是 Plugin 的核心

Skills 是 Plugin 最常用的元件

- **可重用**：寫一次，到處用
- **可組合**：多個 skill 組合成強大工作流
- **可分享**：透過 Plugin 發布
- **可評估**：追蹤使用情況改進

## Skills 大師之路 ✨

從初學者到專家的里程碑

- 🌱 **初學者**：建立 3 個個人 skill
- 🌿 **進階**：建立 1 個含 5 個 skill 的 plugin
- 🌳 **專家**：貢獻 skill 到團隊 marketplace
- 🏆 **大師**：建立 skill 設計指南並訓練團隊
