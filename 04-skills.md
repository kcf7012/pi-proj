# Skills 完整指南

> 📖 **系列**：Claude Code Plugin 完整學習系列 #04
> 🌐 **原文**：[code.claude.com/docs/zh-TW/skills](https://code.claude.com/docs/zh-TW/skills)
> 📅 **整理日期**：2026 / 01
> 🎯 **適用版本**：Claude Code v2.1.x

> 💡 **本系列總覽**：見 [00-claude-code-plugins-series.md](./00-claude-code-plugins-series.md)
> 📚 **上一篇**：[03-plugins-reference.md](./03-plugins-reference.md)（Plugin 技術參考）
> 📚 **下一篇**：[05-subagents.md](./05-subagents.md)（Subagents 自訂指南）

## 目錄

1. [什麼是 Skill](#什麼是-skill)
2. [Skill 的類型](#skill-的類型)
3. [快速開始：第一個 Skill](#快速開始第一個-skill)
4. [Skill 的位置與範圍](#skill-的位置與範圍)
5. [即時變更偵測](#即時變更偵測)
6. [從父目錄與巢狀目錄自動發現](#從父目錄與巢狀目錄自動發現)
7. [Skill 內容設計](#skill-內容設計)
8. [Frontmatter 完整參考](#frontmatter-完整參考)
9. [Skill 命名規則](#skill-命名規則)
10. [可用的字串替換](#可用的字串替換)
11. [新增支援檔案](#新增支援檔案)
12. [控制誰能叫用 Skill](#控制誰能叫用-skill)
13. [Skill 內容生命週期](#skill-內容生命週期)
14. [為 Skill 預先批准工具](#為-skill-預先批准工具)
15. [傳遞引數給 Skill](#傳遞引數給-skill)
16. [進階模式](#進階模式)
17. [視覺輸出範例](#視覺輸出範例)
18. [評估與改進 Skill](#評估與改進-skill)
19. [分享 Skills](#分享-skills)
20. [疑難排解](#疑難排解)

---

## 什麼是 Skill

**Skill** 是一個 `SKILL.md` 檔案，包含：

- **Frontmatter**（YAML）— 告訴 Claude 何時使用它
- **Markdown 內容** — Claude 使用時要遵循的指令

```
skills/
└── summarize-changes/
    ├── SKILL.md          ← 必需
    ├── reference.md       ← 選用：詳細參考
    └── scripts/           ← 選用：可執行腳本
        └── helper.py
```

當你或 Claude 滿足條件時，skill 會被載入到 context 中並執行。

### 為什麼用 Skill？

當你發現自己：
- 不斷把同樣的劇本、檢查清單或多步驟程序貼到聊天中
- CLAUDE.md 的某個部分已成長為程序而不是事實

→ **把這些內容做成 skill 吧**。

Skill 主體僅在使用時載入，與 CLAUDE.md 內容不同，長參考資料在你需要之前幾乎不花費任何成本。

### 自訂命令已合併到 Skills

> ⚠️ `.claude/commands/deploy.md` 和 `.claude/skills/deploy/SKILL.md` 兩種寫法都會建立 `/deploy`，以相同方式運作。
> 既有 `.claude/commands/` 檔案會繼續運作。Skills 新增了：
> - 支援檔案的目錄
> - frontmatter 控制叫用者（你或 Claude）
> - Claude 在相關時自動載入

Claude Code skills 遵循 [Agent Skills](https://agentskills.io) 開放標準。Claude Code 用額外功能擴展該標準。

---

## Skill 的類型

Skills 可以是兩種角色之一：

### 📖 參考型（Reference）

**新增 Claude 應用於你目前工作的知識**：慣例、模式、風格指南、領域知識。

```yaml
---
name: api-conventions
description: API design patterns for this codebase
---

When writing API endpoints:
- Use RESTful naming conventions
- Return consistent error formats
- Include request validation
```

### ⚡ 任務型（Action）

**為 Claude 提供特定動作的逐步說明**：部署、提交、程式碼生成等。

通常你會用 `/skill-name` 直接叫用，而不是讓 Claude 自動觸發。新增 `disable-model-invocation: true` 防止 Claude 自動觸發。

```yaml
---
name: deploy
description: Deploy the application to production
context: fork
disable-model-invocation: true
---

Deploy the application:
1. Run the test suite
2. Build the application
3. Push to the deployment target
```

---

## 快速開始：第一個 Skill

讓我們建立一個 skill，總結 git 儲存庫中未提交的變更並標記風險。

### Step 1：建立目錄

個人 skills 在所有專案中都可用：

```bash
mkdir -p ~/.claude/skills/summarize-changes
```

### Step 2：建立 SKILL.md

`~/.claude/skills/summarize-changes/SKILL.md`：

```yaml
---
description: Summarizes uncommitted changes and flags anything risky. Use when the user asks what changed, wants a commit message, or asks to review their diff.
---

## Current changes

!`git diff HEAD`

## Instructions

Summarize the changes above in two or three bullet points, then list any risks you notice such as missing error handling, hardcoded values, or tests that need updating. If the diff is empty, say there are no uncommitted changes.
```

> 💡 `` !`git diff HEAD` `` 使用了[動態上下文注入](#注入動態上下文)：Claude Code 執行該命令，並在 Claude 看到 skill 內容之前將該行替換為其輸出。

### Step 3：測試

開啟 git 專案，做一些小編輯，然後啟動 Claude Code。兩種方式測試：

**讓 Claude 自動叫用**（描述符合時）：
```
What did I change?
```

**直接叫用**：
```
/summarize-changes
```

---

## Skill 的位置與範圍

Skill 存放位置決定誰能用它：

| 位置 | 路徑 | 適用範圍 |
|:-----|:-----|:---------|
| 企業 | 受管設定 | 組織內所有使用者 |
| 個人 | `~/.claude/skills/<name>/SKILL.md` | 你的所有專案 |
| 專案 | `.claude/skills/<name>/SKILL.md` | 僅此專案 |
| 外掛 | `<plugin>/skills/<name>/SKILL.md` | 啟用 plugin 的位置 |

### 優先級規則

當 skills 在不同層級共享相同名稱時，**企業 > 個人 > 專案**。skill 也會覆蓋同名捆綁 skill。

例如，專案 `.claude/skills/code-review/SKILL.md` 會取代捆綁的 `/code-review`。

Plugin skills 用 `plugin-name:skill-name` 命名空間，所以不會與其他層級衝突。

### 巢狀目錄支援

Skills 也會從你工作目錄下方的**巢狀 `.claude/skills/`** 目錄載入 — 當 Claude 讀取或編輯子目錄的檔案時，該子目錄的 skills 變成可用。

**這讓 monorepo 套件可以提供自己的 skills** — 在處理該套件時適用，即使工作階段從儲存庫根目錄開始。

當巢狀 skill 與另一個 skill 共享名稱時，**兩者都保持可用**：
- 巢狀的出現在目錄限定的名稱下（如 `apps/web:deploy`）
- 描述會說明它適用於哪個目錄
- Claude 選擇與正在處理的檔案相符的變體

> 從父目錄往上走：專案 skills 從起始目錄 + 直到儲存庫根目錄的每個父目錄中載入，所以子目錄中啟動仍會拾取根目錄的 skills。

### 來自 `--add-dir` 目錄的 Skills

`--add-dir` 旗標和 `/add-dir` 命令[授予檔案存取權](https://code.claude.com/docs/zh-TW/permissions#additional-directories-grant-file-access-not-configuration)而不是設定發現，但 **skills 是例外**：已新增目錄中的 `.claude/skills/` 會自動載入。

> 此例外僅適用於 `--add-dir` 和 `/add-dir`。`settings.json` 中的 `permissions.additionalDirectories` 設定**僅授予檔案存取權**，不會載入 skills。

### Symlink 支援

`~/.claude/skills/<dir>/` 項目可以是磁碟上其他位置的目錄的符號連結。Claude Code 遵循 symlinks 並從目標目錄讀取 `SKILL.md`，若相同目標可從多個位置到達，會載入 skill 一次。

Plugin skills 以不同方式處理符號連結 — 見 [plugin 指南](./03-plugins-reference.md#share-files-within-a-marketplace-with-symlinks)。

### 加上 `.claude-plugin/plugin.json` 變成 Plugin

將 `.claude-plugin/plugin.json` 新增到 skill 資料夾，它會載入為名為 `name@skills-dir` 的 [plugin](./03-plugins-reference.md#skills-directory-plugins)，因此它可以捆綁 agents、hooks 和 MCP servers。

---

## 即時變更偵測

Claude Code **監視 skill 目錄**以尋找檔案變更：

- `~/.claude/skills/`、專案 `.claude/skills/`、`--add-dir` 目錄內的 `.claude/skills/`
- 新增、編輯或移除 skill **會在目前工作階段內生效**，無需重新啟動

但有兩個限制：
1. **建立工作階段開始時不存在的頂級 skills 目錄需要重新啟動** Claude Code，才能監視新目錄
2. 即時變更偵測**僅涵蓋 `SKILL.md` 文字**。對於也是 plugin 的 skill 資料夾，`hooks/`、`.mcp.json`、`agents/` 和 `output-styles/` 的變更需要 `/reload-plugins` 才能生效

---

## 從父目錄與巢狀目錄自動發現

**從父目錄往上走**：
- 專案 skills 從**起始目錄** + 直到儲存庫根目錄的每個父目錄中載入
- 在子目錄中啟動 Claude 仍會拾取根目錄的 skills

**從巢狀目錄往下走**：
- 當你在子目錄中使用檔案時，Claude Code 也會**按需從巢狀 `.claude/skills/` 目錄**發現 skills
- 例如：在 `packages/frontend/` 編輯 → 也在 `packages/frontend/.claude/skills/` 找 skills
- 支援 monorepo 設定

### 標準 Skill 目錄結構

```text
my-skill/
├── SKILL.md           # 主要說明（必需）
├── template.md        # Claude 要填入的範本
├── examples/
│   └── sample.md      # 顯示預期格式的範例輸出
└── scripts/
    └── validate.sh    # Claude 可以執行的指令碼
```

> `.claude/commands/` 中的檔案仍然有效，並支援相同的 [frontmatter](#frontmatter-完整參考)。建議使用 Skills，因為它們支援額外功能。

---

## Skill 內容設計

Skill 檔案可以包含任何說明，但思考你想如何叫用它們有助於指導要包含的內容。

### 保持內容簡潔

> 💡 一旦 skill 載入，其內容[在整個回合中保持在上下文中](#skill-內容生命週期)，因此**每一行都是一個重複的令牌成本**。陳述要做什麼，而不是敘述如何或為什麼。

應用與你對 [CLAUDE.md 內容](https://code.claude.com/docs/zh-TW/best-practices#write-an-effective-claude-md)所做的相同簡潔性測試。

### 內容類型考量

| 類型 | 適用場景 | 範例 |
|:-----|:---------|:-----|
| 參考內容 | 慣例、模式、風格指南、領域知識。Claude 在整個 session 內聯使用 | API 設計模式、命名規範 |
| 任務內容 | 特定動作的逐步說明（部署、提交、程式碼生成） | 用 `/commit` 直接觸發的工作流程 |

---

## Frontmatter 完整參考

所有欄位都是可選的。建議只使用 `description`。

```yaml
---
name: my-skill
description: What this skill does
disable-model-invocation: true
allowed-tools: Read Grep
---

Your skill instructions here...
```

| 欄位 | 必需 | 描述 |
|:-----|:-----|:-----|
| `name` | ❌ | Skill 清單中顯示的顯示名稱。預設為目錄名稱。 |
| `description` | ✅ 建議 | Skill 的功能以及何時使用它。Claude 用來決定何時應用。若省略，使用 markdown 內容的第一段。**前置關鍵使用案例**：結合的 `description` 和 `when_to_use` 文字在 skill 清單中**截斷至 1,536 個字元**。 |
| `when_to_use` | ❌ | Claude 應何時叫用的額外上下文（觸發短語、範例請求）。附加到 `description`，計入 1,536 字元上限。 |
| `argument-hint` | ❌ | 自動完成期間顯示的提示，指示預期引數。範例：`[issue-number]`、`[filename] [format]`。 |
| `arguments` | ❌ | 用於 skill 內容中 [`$name` 替換](#可用的字串替換)的具名位置引數。 |
| `disable-model-invocation` | ❌ | 設為 `true` 防止 Claude 自動載入。用於你想用 `/name` 手動觸發的工作流程。也防止該 skill 被[預載入到 subagents](https://code.claude.com/docs/zh-TW/sub-agents#preload-skills-into-subagents)。**v2.1.196+ 也防止 skill 在排程任務以該 skill 作為提示觸發時執行。** 預設：`false`。 |
| `user-invocable` | ❌ | 設為 `false` 從 `/` 功能表中隱藏。用於使用者不應直接叫用的背景知識。預設：`true`。 |
| `allowed-tools` | ❌ | 當此 skill 處於作用中時，Claude 可使用而無需詢問許可的工具。接受空格或逗號分隔字串，或 YAML 清單。 |
| `disallowed-tools` | ❌ | 當此 skill 處於作用中時從可用工具池中移除的工具。用於不應呼叫某些工具的自主 skills。 |
| `model` | ❌ | 當此 skill 處於作用中時使用的模型。覆蓋適用於目前回合的其餘部分。接受與 `/model` 相同的值，或 `inherit`。 |
| `effort` | ❌ | 努力級別：`low`、`medium`、`high`、`xhigh`、`max`。覆蓋工作階段努力級別。預設：繼承自工作階段。 |
| `context` | ❌ | 設為 `fork` 在分叉的 subagent 上下文中執行。 |
| `agent` | ❌ | 當設定 `context: fork` 時要使用的 subagent 類型。 |
| `hooks` | ❌ | 限定於此 skill 生命週期的 hooks。詳見 [Hooks 指南](./06-hooks.md#skills-和-agents-中的-hooks)。 |
| `paths` | ❌ | Glob 模式，限制何時啟動此 skill。設定時，Claude 僅在使用與模式相符的檔案時自動載入。 |
| `shell` | ❌ | 用於 skill 中 `` !`command` `` 和 ` ```! ` 區塊的 shell。`bash`（預設）或 `powershell`。 |

---

## Skill 命名規則

你輸入以叫用 skill 的命令來自 skill 檔案的位置。**Frontmatter `name` 欄位設定清單中顯示的標籤**，除了 plugin 根目錄 `SKILL.md` 外，不會改變你在 `/` 後輸入的內容。

| Skill 位置 | 命令名稱來源 | 範例 |
|:-----------|:------------|:-----|
| `~/.claude/skills/` 或 `.claude/skills/` 下的 Skill 目錄 | 目錄名稱 | `.claude/skills/deploy-staging/SKILL.md` → `/deploy-staging` |
| 巢狀 skill 目錄（與另一個 skill 衝突時） | 相對於工作目錄的子目錄路徑 | `apps/web/.claude/skills/deploy/SKILL.md` → `/apps/web:deploy` |
| `.claude/commands/` 下的檔案 | 檔案名稱（不含副檔名） | `.claude/commands/deploy.md` → `/deploy` |
| Plugin `skills/` 子目錄 | 目錄名稱，由 plugin 命名空間 | `my-plugin/skills/review/SKILL.md` → `/my-plugin:review` |
| Plugin 根目錄 `SKILL.md` | Frontmatter `name`，以 plugin 目錄名稱作為後備 | `my-plugin/SKILL.md` 搭配 `name: review` → `/my-plugin:review` |

> Plugin 根目錄情況是 `name` 設定命令名稱的**唯一**地方，因為沒有 skill 目錄可從中取得。

---

## 可用的字串替換

Skills 支援 skill 內容中動態值的字串替換：

| 變數 | 描述 |
|:-----|:-----|
| `$ARGUMENTS` | 叫用 skill 時傳遞的所有引數。若 `$ARGUMENTS` 不在內容中，引數會附加為 `ARGUMENTS: ...`。 |
| `$ARGUMENTS[N]` | 透過 0 為基礎的索引存取特定引數。`$ARGUMENTS[0]` = 第一個引數。 |
| `$N` | `$ARGUMENTS[N]` 的簡寫。`$0` = 第一個引數，`$1` = 第二個引數。 |
| `$name` | 在 [`arguments`](#frontmatter-完整參考) frontmatter 清單中宣告的具名引數。`$issue` 擴展為第一個引數等。 |
| `${CLAUDE_SESSION_ID}` | 目前的工作階段 ID。適用於記錄、建立工作階段特定檔案。 |
| `${CLAUDE_EFFORT}` | 目前的努力級別：`low`、`medium`、`high`、`xhigh`、`max`。 |
| `${CLAUDE_SKILL_DIR}` | 包含 skill 的 `SKILL.md` 檔案的目錄。對於 plugin skills，這是 plugin 中 skill 的子目錄。 |
| `${CLAUDE_PROJECT_DIR}` | 專案根目錄。與 hooks 和 MCP servers 接收的相同路徑。 |

> `$ARGUMENTS` 預留位置始終擴展為輸入的完整引數字串。

### 引數轉義

若要在數字、`ARGUMENTS` 或宣告的引數名稱之前包含字面 `$`（例如散文中的 `$1.00`），使用反斜線逸出：`\$1.00`。

- 反斜線在任何其他 `$` 之前保持不變
- 只有直接在令牌之前的單個反斜線才能逸出它
- 雙反斜線（例如 `\\$1`）會保留兩個反斜線，`$1` 仍然擴展為引數值

### 索引引數的引用

索引引數使用 shell 風格的引用，將多字值包裝在引號中以將其作為單個引數傳遞。

例如：`/my-skill "hello world" second` 使 `$0` 擴展為 `hello world`，`$1` 擴展為 `second`。

### 使用替換的範例

```yaml
---
name: session-logger
description: Log activity for this session
---

Log the following to logs/${CLAUDE_SESSION_ID}.log:

$ARGUMENTS
```

---

## 新增支援檔案

Skills 可以在其目錄中包含多個檔案：

```text
my-skill/
├── SKILL.md (必需 - 概覽與導航)
├── reference.md (詳細 API 文件 - 必要時載入)
├── examples.md (使用範例 - 必要時載入)
└── scripts/
    └── helper.py (工具腳本 - 執行而非載入)
```

從 `SKILL.md` 參考支援檔案，讓 Claude 知道每個檔案包含什麼以及何時載入：

```markdown
## Additional resources

- For complete API details, see [reference.md](reference.md)
- For usage examples, see [examples.md](examples.md)
```

> 💡 **將 `SKILL.md` 保持在 500 行以下**。將詳細的參考資料移至單獨的檔案。

---

## 控制誰能叫用 Skill

預設情況下，**你和 Claude 都可以叫用**任何 skill。你可以：
- 輸入 `/skill-name` 直接叫用
- Claude 可以在與你的對話相關時自動載入它

兩個 frontmatter 欄位讓你限制此：

### `disable-model-invocation: true`

**只有你可以叫用該 skill**。用於：
- 具有副作用的工作流程（`/commit`、`/deploy`、`/send-slack-message`）
- 你想控制時機的工作流程（不希望 Claude 因為你的程式碼看起來準備好就決定部署）

### `user-invocable: false`

**只有 Claude 可以叫用該 skill**。用於：
- 不可作為命令操作的背景知識
- 例如 `legacy-system-context` skill 解釋舊系統如何運作 — Claude 在相關時應該知道，但 `/legacy-system-context` 對使用者來說不是有意義的動作

### 行為對照表

| Frontmatter | 你可以叫用 | Claude 可以叫用 | 何時載入上下文 |
|:------------|:----|:----|:----------------------|
| （預設） | ✅ | ✅ | 描述始終在上下文中，叫用時載入完整 skill |
| `disable-model-invocation: true` | ✅ | ❌ | 描述不在上下文中，你叫用時載入完整 skill |
| `user-invocable: false` | ❌ | ✅ | 描述始終在上下文中，叫用時載入完整 skill |

### 範例：只有你能觸發的部署 Skill

```yaml
---
name: deploy
description: Deploy the application to production
disable-model-invocation: true
---

Deploy $ARGUMENTS to production:

1. Run the test suite
2. Build the application
3. Push to the deployment target
4. Verify the deployment succeeded
```

> 在常規工作階段中，skill 描述會載入上下文，以便 Claude 知道可用的內容，但完整 skill 內容僅在叫用時載入。
> **預載入 skills 的 Subagents** 的運作方式不同：完整 skill 內容在啟動時注入。

---

## Skill 內容生命週期

當你或 Claude 叫用 skill 時，呈現的 `SKILL.md` 內容作為**單一訊息**進入對話，並**在工作階段的其餘部分保持在那裡**。

> Claude Code **不會在稍後的回合中重新讀取 skill 檔案**，因此應將應該在整個任務中應用的指導寫成**常設說明**，而不是一次性步驟。

### 重複叫用的行為

當 Claude 重新叫用其呈現內容與已在上下文中的副本相同的 skill 時，**Claude Code 會新增一個簡短的註記**表示該 skill 已載入，而不是內容的第二份副本。

當呈現內容不同時（因為引數改變或[動態上下文](#注入動態上下文)命令產生了新輸出），Claude Code 會附加完整內容。

> v2.1.202 之前：每次重新叫用都會附加 skill 說明的另一份完整副本。

### Auto-Compact 後的保留

[Auto-compact](https://code.claude.com/docs/zh-TW/how-claude-code-works#when-context-fills-up) 在令牌預算內**轉發叫用的 skills**：

- 當對話被摘要以釋放上下文時，Claude Code 在摘要後**重新附加每個 skill 的最新叫用**
- 保留每個的前 5,000 個 token
- 重新附加的 skills **共享 25,000 個 token 的組合預算**
- Claude Code 從**最近叫用的 skill 開始填充**此預算

> 如果 skill 在第一個回應後似乎停止影響行為，內容通常仍然存在，模型正在選擇其他工具或方法。加強 skill 的 `description` 和說明，以便模型繼續偏好它，或使用 [hooks](./06-hooks.md) 來確定性地強制行為。

### 重新叫用來恢復

如果 skill 很大或你在它之後叫用了其他幾個，**在 compaction 後重新叫用它**以恢復完整內容。

---

## 為 Skill 預先批准工具

`allowed-tools` 欄位在 skill 處於作用中時**授予列出的工具的許可**，因此 Claude 可以使用它們而無需提示你批准。

它**不會限制哪些工具可用**：每個工具仍然可呼叫，你的[許可設定](https://code.claude.com/docs/zh-TW/permissions)仍然管理未列出的工具。

### 範例：免批准執行 Git 指令

```yaml
---
name: commit
description: Stage and commit the current changes
disable-model-invocation: true
allowed-tools: Bash(git add *) Bash(git commit *) Bash(git status *)
---
```

> 對於簽入到專案的 `.claude/skills/` 目錄的 skills，`allowed-tools` 在你接受該資料夾的工作區信任對話後生效。

### 從可用工具池中移除工具

使用 `disallowed-tools` 從 skill 的 frontmatter 列出要在 skill 處於作用中時**移除**的工具。限制在**你傳送下一則訊息時清除**。

若要在所有 skills 和提示中阻止工具，請在你的[許可設定](https://code.claude.com/docs/zh-TW/permissions)中新增拒絕規則。

---

## 傳遞引數給 Skills

你和 Claude 都可以在叫用 skill 時傳遞引數。引數可透過 `$ARGUMENTS` 預留位置取得。

### 基本範例

```yaml
---
name: fix-issue
description: Fix a GitHub issue
disable-model-invocation: true
---

Fix GitHub issue $ARGUMENTS following our coding standards.

1. Read the issue description
2. Understand the requirements
3. Implement the fix
4. Write tests
5. Create a commit
```

執行 `/fix-issue 123` 時，Claude 收到「Fix GitHub issue 123 following our coding standards...」

### 預設行為

如果你使用引數叫用 skill，但 skill **不包含 `$ARGUMENTS`**，Claude Code 會將 `ARGUMENTS: ...` **附加到 skill 內容的末尾**，以便 Claude 仍然看到你輸入的內容。

### 堆疊多個 Skills

自 v2.1.199 起，輸入 `/code-review /fix-issue 123` 會**載入兩個 skills**，並將尾部文字 `123` 作為 `$ARGUMENTS` 傳遞給**每個** skills。

- 較早版本：只有第一個 skill 載入並接收 `/fix-issue 123` 作為字面引數文字
- Claude Code 展開第一個 skill 加上最多五個堆疊在其後的 skills
- 展開在第一個不是內聯使用者可叫用 skill 的令牌處停止

### 按位置存取個別引數

使用 `$ARGUMENTS[N]` 或較短的 `$N`：

```yaml
---
name: migrate-component
description: Migrate a component from one framework to another
---

Migrate the $ARGUMENTS[0] component from $ARGUMENTS[1] to $ARGUMENTS[2].
Preserve all existing behavior and tests.
```

執行 `/migrate-component SearchBar React Vue`：
- `$ARGUMENTS[0]` → `SearchBar`
- `$ARGUMENTS[1]` → `React`
- `$ARGUMENTS[2]` → `Vue`

### 具名引數（arguments 欄位）

```yaml
---
name: pr-review
description: Review a pull request
arguments:
  - issue
  - branch
---

Review PR for issue $issue on branch $branch.
```

> 使用 `arguments: [issue, branch]` 時，`$issue` 擴展為第一個引數，`$branch` 擴展為第二個引數。名稱按順序對應到位置。

---

## 進階模式

### 注入動態上下文

`` !` ` `` 語法在將 skill 內容傳送給 Claude 之前**執行 shell 命令**。命令輸出替換預留位置。

> 這是**預處理**，不是 Claude 執行的內容。Claude 只看到最終結果。

#### 範例：PR 摘要 Skill

```yaml
---
name: pr-summary
description: Summarize changes in a pull request
context: fork
agent: Explore
allowed-tools: Bash(gh *)
---

## Pull request context
- PR diff: !`gh pr diff`
- PR comments: !`gh pr view --comments`
- Changed files: !`gh pr diff --name-only`

## Your task
Summarize this pull request...
```

當此 skill 執行時：
1. 每個 `` !` ` `` 立即執行（**在 Claude 看到任何內容之前**）
2. 輸出替換 skill 內容中的預留位置
3. Claude 收到具有實際 PR 資料的完全呈現的提示

#### 多行命令

對於多行命令，使用以 ` ```! ` 開啟的圍欄程式碼區塊：

````markdown
## Environment
```!
node --version
npm --version
git status --short
```
````

#### 限制

- 替換對原始檔案執行**一次**。命令輸出會以純文字形式插入，**不會重新掃描**以尋找進一步的 `` !` ` `` 預留位置
- 內聯形式僅在 `!` 出現在**行首**或緊接在**空白字元之後**時被識別
- 如果 `!` 跟在另一個字元之後（如 `` KEY=!`cmd` ``），預留位置會保留為字面文字

#### 停用 Shell 執行

要在 skill 執行時要求更深入的推理，請在 skill 內容中的任何位置包含 `ultrathink`。詳見 [使用 ultrathink 進行一次性深入推理](https://code.claude.com/docs/zh-TW/model-config#use-ultrathink-for-one-off-deep-reasoning)。

若要停用 shell 執行，設定 `"disableSkillShellExecution": true` 在 [設定](https://code.claude.com/docs/zh-TW/settings) 中。每個命令會被替換為 `[shell command execution disabled by policy]` 而不是被執行。捆綁和受管 skills 不受影響。

---

### 在 Subagent 中執行 Skills

當你想要 skill 在隔離中執行時，將 `context: fork` 新增到你的 frontmatter。Skill 內容變成驅動 subagent 的提示。

> ⚠️ `context: fork` 僅對具有**明確說明**的 skills 有意義。如果你的 skill 包含「使用這些 API 慣例」之類的指南而沒有任務，subagent 會收到指南但沒有可操作的提示，並返回而沒有有意義的輸出。

Skills 和 [subagents](./05-subagents.md) 以兩個方向協同運作：

| 方法 | 系統提示 | 任務 | 也載入 |
|:-----|:---------|:-----|:-------|
| 具有 `context: fork` 的 Skill | 來自代理類型 | SKILL.md 內容 | CLAUDE.md，除非代理是 Explore 或 Plan |
| 具有 `skills` 欄位的 Subagent | Subagent 的 markdown 主體 | Claude 的委派訊息 | 預載入的 skills + CLAUDE.md |

使用 `context: fork`，你在 skill 中編寫任務並選擇代理類型來執行它。內建的 Explore 和 Plan 代理[跳過 CLAUDE.md 和 git status](https://code.claude.com/docs/zh-TW/sub-agents#what-loads-at-startup)以保持其上下文較小。

#### 範例：使用 Explore 代理的研究 Skill

```yaml
---
name: deep-research
description: Research a topic thoroughly
context: fork
agent: Explore
---

Research $ARGUMENTS thoroughly:

1. Find relevant files using Glob and Grep
2. Read and analyze the code
3. Summarize findings with specific file references
```

當此 skill 執行時：
1. 建立新的隔離上下文
2. Subagent 收到 skill 內容作為其提示
3. `agent` 欄位決定執行環境（模型、工具和許可）
4. 結果會總結並返回到主要對話

`agent` 欄位選項：內建代理（`Explore`、`Plan`、`general-purpose`）或任何自訂 subagent。若省略，使用 `general-purpose`。

---

### 限制 Claude 的 Skill 存取

預設情況下，Claude 可以叫用任何沒有設定 `disable-model-invocation: true` 的 skill。

控制 Claude 可以叫用哪些 skills 的三種方式：

**1. 在 `/permissions` 中拒絕 Skill 工具來停用所有 skills**：
```text
# Add to deny rules:
Skill
```

**2. 使用[許可規則](https://code.claude.com/docs/zh-TW/permissions)允許或拒絕特定 skills**：
```text
# Allow only specific skills
Skill(commit)
Skill(review-pr *)

# Deny specific skills
Skill(deploy *)
```

許可語法：`Skill(name)` 用於精確匹配，`Skill(name *)` 用於帶有任何引數的前綴匹配。

**3. 透過將 `disable-model-invocation: true` 新增到其 frontmatter 來隱藏個別 skills**

> `user-invocable` 欄位僅控制功能表可見性，不控制 Skill 工具存取。使用 `disable-model-invocation: true` 來阻止程式化叫用。

---

### 從設定覆蓋 Skill 可見性

`skillOverrides` 設定從你的[設定](https://code.claude.com/docs/zh-TW/settings)控制 skill 可見性，而不是 skill 自己的 frontmatter。將其用於你不想編輯 SKILL.md 的 skills。

`/skills` 功能表為你編寫：突出顯示 skill 並按 `Space` 循環狀態，然後按 `Enter` 儲存到 `.claude/settings.local.json`。

每個鍵是 skill 名稱，每個值是四種狀態之一：

| 值 | 列出給 Claude | 在 `/` 功能表中 |
|:---|:----|:----|
| `"on"` | 名稱和描述 | ✅ |
| `"name-only"` | 僅名稱 | ✅ |
| `"user-invocable-only"` | 隱藏 | ✅ |
| `"off"` | 隱藏 | 隱藏 |

> 自 v2.1.199+：`"off"` 也會從廣告給 [Remote Control](https://code.claude.com/docs/zh-TW/remote-control) 用戶端和 [Agent SDK](https://code.claude.com/docs/zh-TW/agent-sdk/slash-commands) 呼叫者的命令列表中隱藏 skill。
> 透過其完整名稱叫用隱藏的 skill 仍會返回 `skillOverrides` 錯誤，而不是執行它。

```json
{
  "skillOverrides": {
    "legacy-context": "name-only",
    "deploy": "off"
  }
}
```

> ⚠️ Plugin skills 不受 `skillOverrides` 影響。透過 `/plugin` 改為管理這些。

---

## 視覺輸出範例

Skills 可以捆綁並執行任何語言的指令碼，為 Claude 提供超越單個提示可能的功能。

一個強大的模式是**生成視覺輸出**：在你的瀏覽器中開啟的互動式 HTML 檔案。

### 範例：程式碼庫視覺化工具

```bash
mkdir -p ~/.claude/skills/codebase-visualizer/scripts
```

`~/.claude/skills/codebase-visualizer/SKILL.md`：

````yaml
---
name: codebase-visualizer
description: Generate an interactive collapsible tree visualization of your codebase. Use when exploring a new repo, understanding project structure, or identifying large files.
allowed-tools: Bash(python3 *)
---

# Codebase Visualizer

Generate an interactive HTML tree view that shows your project's file structure with collapsible directories.

## Usage

Run the visualization script from your project root:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/visualize.py .
```

This creates `codebase-map.html` in the current directory and opens it in your default browser.

## What the visualization shows

- **Collapsible directories**: Click folders to expand/collapse
- **File sizes**: Displayed next to each file
- **Colors**: Different colors for different file types
- **Directory totals**: Shows aggregate size of each folder
````

`~/.claude/skills/codebase-visualizer/scripts/visualize.py`（此指令碼掃描目錄樹並生成自包含的 HTML 檔案）：

```python
#!/usr/bin/env python3
"""Generate an interactive collapsible tree visualization of a codebase."""

import json
import sys
import webbrowser
from html import escape
from pathlib import Path
from collections import Counter

IGNORE = {'.git', 'node_modules', '__pycache__', '.venv', 'venv', 'dist', 'build'}

def scan(path: Path, stats: dict) -> dict:
    result = {"name": path.name, "children": [], "size": 0}
    try:
        for item in sorted(path.iterdir()):
            if item.name in IGNORE or item.name.startswith('.'):
                continue
            if item.is_file():
                size = item.stat().st_size
                ext = item.suffix.lower() or '(no ext)'
                result["children"].append({"name": item.name, "size": size, "ext": ext})
                result["size"] += size
                stats["files"] += 1
                stats["extensions"][ext] += 1
                stats["ext_sizes"][ext] += size
            elif item.is_dir():
                stats["dirs"] += 1
                child = scan(item, stats)
                if child["children"]:
                    result["children"].append(child)
                    result["size"] += child["size"]
    except PermissionError:
        pass
    return result

def generate_html(data: dict, stats: dict, output: Path) -> None:
    ext_sizes = stats["ext_sizes"]
    total_size = sum(ext_sizes.values()) or 1
    sorted_exts = sorted(ext_sizes.items(), key=lambda x: -x[1])[:8]
    colors = {
        '.js': '#f7df1e', '.ts': '#3178c6', '.py': '#3776ab', '.go': '#00add8',
        '.rs': '#dea584', '.rb': '#cc342d', '.css': '#264de4', '.html': '#e34c26',
        '.json': '#6b7280', '.md': '#083fa1', '.yaml': '#cb171e', '.yml': '#cb171e',
        '.mdx': '#083fa1', '.tsx': '#3178c6', '.jsx': '#61dafb', '.sh': '#4eaa25',
    }
    lang_bars = "".join(
        f'<div class="bar-row"><span class="bar-label">{ext}</span>'
        f'<div class="bar" style="width:{(size/total_size)*100}%;background:{colors.get(ext,"#6b7280")}"></div>'
        f'<span class="bar-pct">{(size/total_size)*100:.1f}%</span></div>'
        for ext, size in sorted_exts
    )
    def fmt(b):
        if b < 1024: return f"{b} B"
        if b < 1048576: return f"{b/1024:.1f} KB"
        return f"{b/1048576:.1f} MB"

    html = f'''<!DOCTYPE html>
<html><head>
  <meta charset="utf-8"><title>Codebase Explorer</title>
  <style>
    body {{ font: 14px/1.5 system-ui, sans-serif; margin: 0; background: #1a1a2e; color: #eee; }}
    .container {{ display: flex; height: 100vh; }}
    .sidebar {{ width: 280px; background: #252542; padding: 20px; border-right: 1px solid #3d3d5c; overflow-y: auto; flex-shrink: 0; }}
    .main {{ flex: 1; padding: 20px; overflow-y: auto; }}
    h1 {{ margin: 0 0 10px 0; font-size: 18px; }}
    h2 {{ margin: 20px 0 10px 0; font-size: 14px; color: #888; text-transform: uppercase; }}
    .stat {{ display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #3d3d5c; }}
    .stat-value {{ font-weight: bold; }}
    .bar-row {{ display: flex; align-items: center; margin: 6px 0; }}
    .bar-label {{ width: 55px; font-size: 12px; color: #aaa; }}
    .bar {{ height: 18px; border-radius: 3px; }}
    .bar-pct {{ margin-left: 8px; font-size: 12px; color: #666; }}
    .tree {{ list-style: none; padding-left: 20px; }}
    details {{ cursor: pointer; }}
    summary {{ padding: 4px 8px; border-radius: 4px; }}
    summary:hover {{ background: #2d2d44; }}
    .folder {{ color: #ffd700; }}
    .file {{ display: flex; align-items: center; padding: 4px 8px; border-radius: 4px; }}
    .file:hover {{ background: #2d2d44; }}
    .size {{ color: #888; margin-left: auto; font-size: 12px; }}
    .dot {{ width: 8px; height: 8px; border-radius: 50%; margin-right: 8px; }}
  </style>
</head><body>
  <div class="container">
    <div class="sidebar">
      <h1>📊 Summary</h1>
      <div class="stat"><span>Files</span><span class="stat-value">{stats["files"]:,}</span></div>
      <div class="stat"><span>Directories</span><span class="stat-value">{stats["dirs"]:,}</span></div>
      <div class="stat"><span>Total size</span><span class="stat-value">{fmt(data["size"])}</span></div>
      <div class="stat"><span>File types</span><span class="stat-value">{len(stats["extensions"])}</span></div>
      <h2>By file type</h2>
      {lang_bars}
    </div>
    <div class="main">
      <h1>📁 {escape(data["name"])}</h1>
      <ul class="tree" id="root"></ul>
    </div>
  </div>
  <script>
    const data = {json.dumps(data)};
    const colors = {json.dumps(colors)};
    function fmt(b) {{ if (b < 1024) return b + ' B'; if (b < 1048576) return (b/1024).toFixed(1) + ' KB'; return (b/1048576).toFixed(1) + ' MB'; }}
    function esc(s) {{ return s.replace(/[&<>"']/g, c => ({{"&":"&amp;","<":"<",">":">",'"':""","'":"'"}}[c])); }}
    function render(node, parent) {{
      if (node.children) {{
        const det = document.createElement('details');
        det.open = parent === document.getElementById('root');
        det.innerHTML = `<summary><span class="folder">📁 ${{esc(node.name)}}</span><span class="size">${{fmt(node.size)}}</span></summary>`;
        const ul = document.createElement('ul'); ul.className = 'tree';
        node.children.sort((a,b) => (b.children?1:0)-(a.children?1:0) || a.name.localeCompare(b.name));
        node.children.forEach(c => render(c, ul));
        det.appendChild(ul);
        const li = document.createElement('li'); li.appendChild(det); parent.appendChild(li);
      }} else {{
        const li = document.createElement('li'); li.className = 'file';
        li.innerHTML = `<span class="dot" style="background:${{colors[node.ext]||'#6b7280'}}"></span>${{esc(node.name)}}<span class="size">${{fmt(node.size)}}</span>`;
        parent.appendChild(li);
      }}
    }}
    data.children.forEach(c => render(c, document.getElementById('root')));
  </script>
</body></html>'''
    output.write_text(html)

if __name__ == '__main__':
    target = Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
    stats = {"files": 0, "dirs": 0, "extensions": Counter(), "ext_sizes": Counter()}
    data = scan(target, stats)
    out = Path('codebase-map.html')
    generate_html(data, stats, out)
    print(f'Generated {out.absolute()}')
    webbrowser.open(f'file://{out.absolute()}')
```

> 此模式適用於任何視覺輸出：相依性圖表、測試涵蓋範圍報告、API 文件、資料庫架構視覺化。

---

## 評估與改進 Skill

看到 skill 觸發告訴你 Claude 找到了它，**而不是它做了你想要的**。

若要知道 skill 是否有效，分別測量兩件事：
1. Claude 是否在應該的提示上叫用它
2. 當它確實叫用時，輸出是否符合你的預期

兩者的檢查都是基準比較：

> 收集一些現實的提示，在一個**新工作階段**中執行每個提示，skill 可用，然後再次執行[停用](#從設定覆蓋-skill-可見性)它，並比較結果。
>
> 新工作階段很重要，因為編寫 skill 的剩餘上下文會掩蓋書面說明中的差距。

### 使用 skill-creator 執行 Evals

[`skill-creator` plugin](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/skill-creator) 在 Claude Code 內自動化比較迴圈：

```bash
/plugin install skill-creator@claude-plugins-official
```

然後要求 Claude 評估現有 skill：
```
evaluate my summarize-changes skill with skill-creator
```

Plugin 會引導你完成：
- **測試案例**：在 skill 目錄內的 `evals/evals.json` 中儲存提示、輸入檔案和預期行為
- **隔離執行**：為每個測試案例生成一個 [subagent](./05-subagents.md)
- **評分**：根據輸出檢查每個判斷
- **基準**：將通過率、時間和令牌聚合為有 skill 與無 skill 的 `benchmark.json`
- **版本比較**：在兩個版本的 skill 之間執行盲 A/B
- **描述調整**：生成應觸發和不應觸發的提示
- **檢查檢視器**：開啟 HTML 報告

---

## 分享 Skills

Skills 可以根據你的受眾在不同範圍內分發：

- **專案 skills**：將 `.claude/skills/` 提交到版本控制
- **外掛**：在你的[plugin](./02-plugins.md)中建立 `skills/` 目錄
- **受管**：透過[受管設定](https://code.claude.com/docs/zh-TW/settings#settings-files)部署組織範圍

---

## 疑難排解

### Skill 未觸發

如果 Claude 在預期時不使用你的 skill：

1. 檢查描述是否包含使用者會自然說出的關鍵字
2. 驗證 skill 是否出現在「What skills are available?」中
3. 嘗試**重新表述你的請求**以更密切匹配描述
4. 如果 skill 是使用者可叫用的，使用 `/skill-name` 直接叫用它

> 如果 frontmatter YAML 格式不正確，Claude Code 會載入 skill 主體且中繼資料為空，因此 `/skill-name` 仍然有效，但 Claude 沒有 `description` 可用來比對。執行 `--debug` 以查看解析錯誤。

### Skill 觸發過於頻繁

如果 Claude 在你不想要時使用你的 skill：

1. 使描述更具體
2. 如果你只想手動叫用，新增 `disable-model-invocation: true`

### Skill 描述被截斷

Claude Code 會將 skill 名稱和描述的清單載入上下文。清單始終包含每個 skill 名稱，但如果你有許多 skills，Claude Code 會**縮短描述以適應清單的字元預算**，可能會去除 Claude 需要匹配你的請求的關鍵字。

預算在**模型上下文視窗的 1% 處動態縮放**。當清單超出預算時，Claude Code 從你最少叫用的 skills 開始**捨棄描述**，因此你使用最多的 skills 會保留其完整文字。

執行 `/doctor` 以估計清單的上下文成本及其最大貢獻者。

> 提高預算：設定 [`skillListingBudgetFraction`](https://code.claude.com/docs/zh-TW/settings#available-settings) 設定（例如 `0.02` = 2%）或 `SLASH_COMMAND_TOOL_CHAR_BUDGET` 環境變數為固定字元計數。
>
> 為其他 skills 釋放預算：在 [`skillOverrides`](#從設定覆蓋-skill-可見性) 中將低優先順序項目設定為 `"name-only"`。

---

## 速查表

| 動作 | 指令/位置 |
|:-----|:---------|
| 個人 skill | `~/.claude/skills/<name>/SKILL.md` |
| 專案 skill | `.claude/skills/<name>/SKILL.md` |
| Plugin skill | `<plugin>/skills/<name>/SKILL.md` |
| 直接叫用 skill | `/skill-name` |
| 列出可用 skills | `/skills` |
| 編輯已存在 skill | 改檔案後即時生效 |
| 重新叫用 skill | 在 compaction 後再 `/skill-name` 恢復 |
| 隱藏 skill | 在 `skillOverrides` 設 `"off"` |
| 限制 Claude 叫用 | 在 frontmatter 設 `disable-model-invocation: true` |
| 限制使用者叫用 | 在 frontmatter 設 `user-invocable: false` |

### 常用 Frontmatter 模式

```yaml
# 標準 reference skill
---
description: ...
---

# 使用者專用任務 skill
---
description: ...
disable-model-invocation: true
---

# 預先批准工具
---
description: ...
allowed-tools: Bash(git *) Read Grep
---

# 帶引數的 skill
---
description: ...
argument-hint: [issue-number]
arguments: [issue]
---

# 在 subagent 中執行
---
description: ...
context: fork
agent: Explore
---
```

---

## 下一步

- 將 skill 包裝成 plugin → 閱讀 [02-plugins.md](./02-plugins.md)
- 想了解 subagent（更強的隔離執行）→ 閱讀 [05-subagents.md](./05-subagents.md)
- 想自動化事件觸發（檔案編輯後跑測試）→ 閱讀 [06-hooks.md](./06-hooks.md)
