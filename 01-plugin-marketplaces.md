# 建立並分發 Plugin Marketplace

> 📖 **系列**：Claude Code Plugin 完整學習系列 #01
> 🌐 **原文**：[code.claude.com/docs/zh-TW/plugin-marketplaces](https://code.claude.com/docs/zh-TW/plugin-marketplaces)
> 📅 **整理日期**：2026 / 01
> 🎯 **適用版本**：Claude Code v2.1.x

> 💡 **本系列總覽**：見 [00-claude-code-plugins-series.md](./00-claude-code-plugins-series.md)
> 📚 **上一篇**：—（系列首篇）
> 📚 **下一篇**：[02-plugins.md](./02-plugins.md)（Plugin 開發指南）

---

## 目錄

1. [什麼是 Plugin Marketplace](#什麼是-plugin-marketplace)
2. [整體流程概述](#整體流程概述)
3. [快速入門：建立本機 Marketplace](#快速入門建立本機-marketplace)
4. [Marketplace 檔案結構](#marketplace-檔案結構)
5. [Marketplace 架構（Schema）](#marketplace-架構schema)
6. [Plugin 項目欄位](#plugin-項目欄位)
7. [Plugin 來源（Sources）](#plugin-來源sources)
8. [Strict Mode 嚴格模式](#strict-mode-嚴格模式)
9. [託管並分發 Marketplace](#託管並分發-marketplace)
10. [為團隊預先配置 Marketplace](#為團隊預先配置-marketplace)
11. [為容器預先填充 Plugin](#為容器預先填充-plugin)
12. [受管 Marketplace 限制](#受管-marketplace-限制)
13. [版本解析與發行通道](#版本解析與發行通道)
14. [重新命名或移除 Plugin](#重新命名或移除-plugin)
15. [驗證與測試](#驗證與測試)
16. [CLI 指令參考](#cli-指令參考)
17. [疑難排解](#疑難排解)
18. [相關文件](#相關文件)

---

## 什麼是 Plugin Marketplace

**Plugin Marketplace** 是一個目錄，用來把 plugin 分發給其他人。它提供：

- ✅ **集中式探索**（讓人容易找到）
- ✅ **版本追蹤**（清楚知道用的是哪一版）
- ✅ **自動更新**（推送後使用者能拉新版本）
- ✅ **多種來源支援**（git 儲存庫、本機路徑、npm…）

一句話：Marketplace = 別人加入來源、安裝你寫的 plugin 的入口。

---

## 整體流程概述

建立並分發 marketplace 涉及 4 步：

```
1. 建立 plugin
   ↓
2. 建立 marketplace 檔案（marketplace.json）
   ↓
3. 託管 marketplace（推送到 GitHub / GitLab…）
   ↓
4. 與使用者分享
```

> 假設你已經有要分發的 plugin。如果還沒，請參考 [建立 plugin](https://code.claude.com/docs/zh-TW/plugins)。

**使用者端指令**：

| 指令 | 作用 |
|------|------|
| `/plugin marketplace add <source>` | 新增 marketplace 來源 |
| `/plugin install <plugin>@<marketplace>` | 安裝特定 plugin |
| `/plugin marketplace update` | 重新整理本機副本 |

---

## 快速入門：建立本機 Marketplace

> 範例：建立一個包含 `quality-review` skill（用於程式碼審查）的 marketplace。

### Step 1：建立目錄結構

```bash
mkdir -p my-marketplace/.claude-plugin
mkdir -p my-marketplace/plugins/quality-review-plugin/.claude-plugin
mkdir -p my-marketplace/plugins/quality-review-plugin/skills/quality-review
```

### Step 2：建立 SKILL.md

`my-marketplace/plugins/quality-review-plugin/skills/quality-review/SKILL.md`

```markdown
---
description: 檢查程式碼中的錯誤、安全性和效能問題
---

檢查我選擇的程式碼或最近的變更，查找：
- 潛在的錯誤或邊界情況
- 安全性問題
- 效能問題
- 可讀性改進

簡潔且可行動。
```

### Step 3：建立 plugin manifest

`my-marketplace/plugins/quality-review-plugin/.claude-plugin/plugin.json`

```json
{
  "name": "quality-review-plugin",
  "description": "新增 quality-review skill 以進行快速程式碼審查",
  "version": "1.0.0"
}
```

> 💡 `version` 設了之後，使用者只會在你改這個欄位時收到更新。每次發行都要提升版本。如果省略 `version`（且用 git 託管），則每次 commit 都會被視為新版本。

### Step 4：建立 marketplace 目錄

`my-marketplace/.claude-plugin/marketplace.json`

```json
{
  "name": "my-plugins",
  "owner": {
    "name": "Your Name"
  },
  "plugins": [
    {
      "name": "quality-review-plugin",
      "source": "./plugins/quality-review-plugin",
      "description": "新增 quality-review skill 以進行快速程式碼審查"
    }
  ]
}
```

### Step 5：新增並安裝

```bash
/plugin marketplace add ./my-marketplace
/plugin install quality-review-plugin@my-plugins
```

### Step 6：使用 skill

選取一些程式碼後執行：

```bash
/quality-review-plugin:quality-review
```

> 📌 Plugin skills 使用 plugin 名稱做命名空間。

---

## Marketplace 檔案結構

在儲存庫根目錄建立 `.claude-plugin/marketplace.json`，此檔案定義：

- marketplace 名稱
- 擁有者資訊
- 包含的 plugin 清單（與來源）

每個 plugin 至少需要 `name` 與 `source`。

### 完整範例

```json
{
  "name": "company-tools",
  "owner": {
    "name": "DevTools Team",
    "email": "devtools@example.com"
  },
  "plugins": [
    {
      "name": "code-formatter",
      "source": "./plugins/formatter",
      "description": "在保存時自動格式化程式碼",
      "version": "2.1.0",
      "author": {
        "name": "DevTools Team"
      }
    },
    {
      "name": "deployment-tools",
      "source": {
        "source": "github",
        "repo": "company/deploy-plugin"
      },
      "description": "部署自動化工具"
    }
  ]
}
```

---

## Marketplace 架構（Schema）

### 必需欄位

| 欄位 | 類型 | 描述 | 範例 |
|:--------|:-----|:---|:---|
| `name` | string | Marketplace 識別碼（kebab-case、無空格）。每個使用者只能為每個名稱註冊一個 marketplace。 | `"acme-tools"` |
| `owner` | object | Marketplace 維護者資訊 | — |
| `plugins` | array | 可用 plugin 的清單 | — |

#### ⚠️ 保留名稱（不可使用）

以下名稱保留給 Anthropic 官方：

```
claude-code-marketplace, claude-code-plugins, claude-plugins-official,
claude-plugins-community, claude-community, anthropic-marketplace,
anthropic-plugins, agent-skills, anthropic-agent-skills,
knowledge-work-plugins, life-sciences, claude-for-legal,
claude-for-financial-services, financial-services-plugins,
first-party-plugins, healthcare
```

> 模仿官方名稱（如 `official-claude-plugins`）也會被擋。

### owner 欄位

| 欄位 | 類型 | 必需 | 描述 |
|:------|:-----|:---|:---|
| `name` | string | ✅ | 維護者或團隊名稱 |
| `email` | string | ❌ | 聯絡電子郵件 |

### 選用欄位

| 欄位 | 類型 | 描述 |
|:---|:---|:---|
| `$schema` | string | JSON Schema URL，僅用於編輯器自動完成。Claude Code 載入時會忽略。 |
| `description` | string | 簡短描述 |
| `version` | string | Marketplace 版本 |
| `metadata.pluginRoot` | string | 相對路徑的基底，例如 `"./plugins"` |
| `allowCrossMarketplaceDependenciesOn` | array | 允許依賴的其他 marketplace 名單 |
| `renames` | object | 舊名稱 → 新名稱（或 `null`）對應，用於自動遷移 |

---

## Plugin 項目欄位

### 必需

| 欄位 | 類型 | 描述 |
|:---|:---|:---|
| `name` | string | Plugin 識別碼（kebab-case、無空格） |
| `source` | string\|object | 從何處取得 plugin（見下節） |

### 標準中繼資料（選用）

| 欄位 | 類型 | 描述 |
|:---|:---|:---|
| `displayName` | string | UI 顯示用名稱（可含空格）。需 v2.1.143+ |
| `description` | string | 簡短描述 |
| `version` | string | Plugin 版本。設了之後 plugin 會固定。 |
| `author` | object | `{ name, email? }` |
| `homepage` | string | 文件 URL |
| `repository` | string | 原始碼 URL |
| `license` | string | SPDX 識別碼（`MIT`、`Apache-2.0`） |
| `keywords` | array | 分類標籤 |
| `category` | string | 類別 |
| `tags` | array | 可搜尋標籤 |
| `strict` | boolean | 控制 `plugin.json` 是否為元件定義的權威（預設 `true`） |
| `relevance` | object | 建議 plugin 的訊號（管理員設定用） |
| `defaultEnabled` | boolean | 安裝後是否啟用（預設 `true`） |

### 元件配置（選用）

| 欄位 | 類型 | 描述 |
|:---|:---|:---|
| `skills` | string\|array | skill 目錄的自訂路徑 |
| `commands` | string\|array | 命令檔案或目錄的自訂路徑 |
| `agents` | string\|array | agent 檔案路徑 |
| `hooks` | string\|object | hooks 配置或檔案路徑 |
| `mcpServers` | string\|object | MCP server 配置或路徑 |
| `lspServers` | string\|object | LSP server 配置或路徑 |

### 進階 plugin 項目範例

```json
{
  "name": "enterprise-tools",
  "source": {
    "source": "github",
    "repo": "company/enterprise-plugin"
  },
  "description": "企業工作流程自動化工具",
  "version": "2.1.0",
  "author": {
    "name": "Enterprise Team",
    "email": "enterprise@example.com"
  },
  "homepage": "https://docs.example.com/plugins/enterprise-tools",
  "repository": "https://github.com/company/enterprise-plugin",
  "license": "MIT",
  "keywords": ["enterprise", "workflow", "automation"],
  "category": "productivity",
  "commands": [
    "./commands/core/",
    "./commands/enterprise/",
    "./commands/experimental/preview.md"
  ],
  "agents": ["./agents/security-reviewer.md", "./agents/compliance-checker.md"],
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/scripts/validate.sh"
          }
        ]
      }
    ]
  },
  "mcpServers": {
    "enterprise-db": {
      "command": "${CLAUDE_PLUGIN_ROOT}/servers/db-server",
      "args": ["--config", "${CLAUDE_PLUGIN_ROOT}/config.json"]
    }
  },
  "strict": false
}
```

#### 重點提醒

- **`commands` / `agents`**：可指定多個目錄或檔案，路徑相對於 plugin 根目錄。
- **`${CLAUDE_PLUGIN_ROOT}`**：在 hooks 與 MCP 配置中用來參考 plugin 安裝目錄。
  - 想保留 plugin 更新後的狀態，改用 `${CLAUDE_PLUGIN_DATA}`。
- **`strict: false`**：marketplace 項目就是完整定義，plugin 不需要 `plugin.json`。

### Skills 載入規則

預設從 plugin `source` 下的 `skills/` 載入 skills。`skills` 欄位的路徑會「加入」掃描：

```json
"skills": ["./skills/", "./extra-skills/"]
```

若多個 plugin 共享根目錄的 `skills/`，要列特定子目錄避免誤載：

```json
{
  "source": "./",
  "skills": ["./skills/code-review", "./skills/docs"]
}
```

---

## Plugin 來源（Sources）

`source` 欄位告訴 Claude Code plugin 從哪裡取得。本機路徑解析的副本會放在 `~/.claude/plugins/cache`。

| 來源 | 類型 | 欄位 | 備註 |
|:---|:---|:---|:---|
| **相對路徑** | string（`"./my-plugin"`） | — | marketplace 儲存庫內的本機目錄 |
| **GitHub** | object | `repo`、`ref?`、`sha?` |  |
| **Git URL** | object | `url`、`ref?`、`sha?` | 通用 git 來源 |
| **Git 子目錄** | object | `url`、`path`、`ref?`、`sha?` | monorepo 用，稀疏複製 |
| **npm** | object | `package`、`version?`、`registry?` | 透過 `npm install` |

> 📌 同時設 `ref` + `sha` 時，`sha` 是有效的固定。即使上游分支被刪，只要 commit 還能取得就會成功。

### 1. 相對路徑

```json
{ "name": "my-plugin", "source": "./plugins/my-plugin" }
```

- 必須以 `./` 開頭
- 相對於 **marketplace 根目錄**（包含 `.claude-plugin/` 的那層）解析
- 不能用 `../` 跳出根目錄

> ⚠️ 相對路徑是針對 marketplace 的本機副本解析。如果是「直接 URL 到 `marketplace.json`」，相對路徑會失效（只下載那個檔案）。此種情況請改用 GitHub、npm、git URL 來源。

### 2. GitHub

```json
{
  "name": "github-plugin",
  "source": {
    "source": "github",
    "repo": "owner/plugin-repo"
  }
}
```

固定到特定版本：

```json
{
  "source": {
    "source": "github",
    "repo": "owner/plugin-repo",
    "ref": "v2.0.0",
    "sha": "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0"
  }
}
```

| 欄位 | 必需 | 描述 |
|:---|:---|:---|
| `repo` | ✅ | `owner/repo` 格式 |
| `ref` | ❌ | 分支或標籤（預設為預設分支） |
| `sha` | ❌ | 完整 40 字元 SHA |

### 3. Git URL（任意 git 主機）

```json
{
  "name": "git-plugin",
  "source": {
    "source": "url",
    "url": "https://gitlab.com/team/plugin.git",
    "ref": "main",
    "sha": "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0"
  }
}
```

| 欄位 | 必需 | 描述 |
|:---|:---|:---|
| `url` | ✅ | 完整 git URL（`https://` 或 `git@`）。`.git` 後綴可有可無。 |
| `ref` | ❌ | 分支或標籤 |
| `sha` | ❌ | 完整 SHA |

### 4. Git 子目錄（monorepo 適用）

```json
{
  "name": "my-plugin",
  "source": {
    "source": "git-subdir",
    "url": "https://github.com/acme-corp/monorepo.git",
    "path": "tools/claude-plugin",
    "ref": "v2.0.0",
    "sha": "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0"
  }
}
```

| 欄位 | 必需 | 描述 |
|:---|:---|:---|
| `url` | ✅ | 完整 URL、`owner/repo` 簡寫或 SSH URL |
| `path` | ✅ | 儲存庫內子目錄路徑 |
| `ref` | ❌ | 分支或標籤 |
| `sha` | ❌ | 完整 SHA |

### 5. npm 套件

```json
{
  "name": "my-npm-plugin",
  "source": {
    "source": "npm",
    "package": "@acme/claude-plugin",
    "version": "^2.0.0",
    "registry": "https://npm.example.com"
  }
}
```

| 欄位 | 必需 | 描述 |
|:---|:---|:---|
| `package` | ✅ | 套件名稱（含 scope） |
| `version` | ❌ | 版本或範圍（`2.1.0`、`^2.0.0`、`~1.5.0`） |
| `registry` | ❌ | 自訂 registry（預設 npmjs.org） |

---

## Strict Mode 嚴格模式

`strict` 欄位控制 `plugin.json` 是否為元件定義（skills、agents、hooks、MCP servers、輸出樣式）的權威。

| 值 | 行為 |
|:---|:---|
| `true`（預設） | `plugin.json` 為權威。marketplace 項目可補充元件，兩者合併。 |
| `false` | marketplace 項目是完整定義。若 plugin 也有 `plugin.json` 宣告元件 → 衝突，無法載入。 |

### 何時用哪個？

- **`strict: true`**：plugin 有自己的 `plugin.json` 並自行管理元件（大多數情境）。
- **`strict: false`**：marketplace 運營商要完全控制（重組或策劃 plugin 的元件）。

---

## 託管並分發 Marketplace

### 1. GitHub（推薦）

1. 建立新儲存庫
2. 加上 `.claude-plugin/marketplace.json`
3. 分享：
   ```bash
   /plugin marketplace add owner/repo
   ```

### 2. 其他 Git 主機

```bash
/plugin marketplace add https://gitlab.com/company/plugins.git
```

### 3. 私人儲存庫

Claude Code 支援私人 repo，會用你現有的 git 認證助手：

- HTTPS：用 `gh auth login`、macOS Keychain、`git-credential-store`
- SSH：需在 `known_hosts` 內且金鑰在 `ssh-agent` 中

#### 背景自動更新的挑戰

預設情況下，背景重新整理會對 `git pull` 停用 git 認證助手 → 私人 repo 的 HTTPS 認證會失敗。

**解決方案**：

1. `CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE=1`：pull 失敗時保留現有副本
2. 配置 git 認證助手（如 `gh auth setup-git`）
3. 全域 git URL 重寫（在 URL 嵌入 token）：

```bash
# GitHub 範例
git config --global url."https://x-access-token:YOUR_TOKEN@github.com/acme-corp/plugins".insteadOf "https://github.com/acme-corp/plugins"
```

| 提供者 | 寫法 |
|:---|:---|
| GitHub | `https://x-access-token:YOUR_TOKEN@github.com/acme-corp/plugins` |
| GitLab | `https://oauth2:YOUR_TOKEN@gitlab.com/acme-corp/plugins` |
| Bitbucket | `https://x-token-auth:YOUR_TOKEN@bitbucket.org/acme-corp/plugins` |

> ⚠️ 重寫會以純文字儲存在 gitconfig，請用**唯讀** token。

> **CI/CD 環境**：在 GitHub Actions 匯出 `GH_TOKEN` 然後 `gh auth setup-git`。預設 workflow token 只能讀自己 repo，要讀別的私人 repo 需要 PAT。

### 4. 本機測試

```bash
/plugin marketplace add ./my-marketplace
/plugin install quality-review-plugin@my-plugins
```

---

## 為團隊預先配置 Marketplace

把 marketplace 加到 `.claude/settings.json`，團隊成員信任專案資料夾時會自動被提示安裝：

```json
{
  "extraKnownMarketplaces": {
    "company-tools": {
      "source": {
        "source": "github",
        "repo": "your-org/claude-plugins"
      }
    }
  }
}
```

也可指定預設啟用哪些 plugin：

```json
{
  "enabledPlugins": {
    "code-formatter@company-tools": true,
    "deployment-tools@company-tools": true
  }
}
```

> 📌 Marketplace 狀態存於 `~/.claude/plugins/known_marketplaces.json`（每個使用者一份），不是每專案一份。

---

## 為容器預先填充 Plugin

容器映像 / CI 環境用：建置時預先填好 plugin 目錄，啟動時直接可用。

設定 `CLAUDE_CODE_PLUGIN_SEED_DIR` 環境變數指向該目錄。

### 目錄結構

```
$CLAUDE_CODE_PLUGIN_SEED_DIR/
  known_marketplaces.json
  marketplaces/<name>/...
  cache/<marketplace>/<plugin>/<version>/...
```

### 兩種建置方式

**方式 A：建置時跑 Claude Code 安裝後複製**

```bash
# 在映像建置中執行
claude plugin marketplace add your-org/plugins
claude plugin install my-tool@your-plugins
# 然後把 ~/.claude/plugins 複製到映像，設 SEED_DIR 指向它
```

**方式 B：直接安裝到目標路徑（跳過複製）**

```bash
CLAUDE_CODE_PLUGIN_CACHE_DIR=/opt/claude-seed claude plugin marketplace add your-org/plugins
CLAUDE_CODE_PLUGIN_CACHE_DIR=/opt/claude-seed claude plugin install my-tool@your-plugins
```

然後在 runtime 設：

```bash
CLAUDE_CODE_PLUGIN_SEED_DIR=/opt/claude-seed
```

### 行為細節

- **唯讀**：種子目錄永遠不會被寫入；自動更新被停用
- **種子優先**：種子宣告的 marketplace 會覆寫使用者配置
- **路徑解析**：執行時透過探測 `$SEED_DIR/marketplaces/<name>/` 定位
- **變更被擋**：`/plugin marketplace remove` 或 `update` 會失敗
- **與設定組合**：若 `extraKnownMarketplaces` / `enabledPlugins` 也宣告了，會用種子副本

---

## 受管 Marketplace 限制

管理員用 `strictKnownMarketplaces` 限制使用者能新增的 marketplace 來源。

| 值 | 行為 |
|:---|:---|
| 未定義（預設） | 無限制 |
| 空陣列 `[]` | 完全鎖定 |
| 來源清單 | 只允許白名單內的 |

### 常見配置

#### 完全鎖定

```json
{ "strictKnownMarketplaces": [] }
```

#### 只允許特定 marketplace

```json
{
  "strictKnownMarketplaces": [
    { "source": "github", "repo": "acme-corp/approved-plugins" },
    { "source": "github", "repo": "acme-corp/security-tools", "ref": "v2.0" },
    { "source": "url", "url": "https://plugins.example.com/marketplace.json" }
  ]
}
```

#### 內部 git 伺服器（用 hostPattern）

```json
{
  "strictKnownMarketplaces": [
    { "source": "hostPattern", "hostPattern": "^github\\.example\\.com$" }
  ]
}
```

#### 檔案系統路徑（用 pathPattern）

```json
{
  "strictKnownMarketplaces": [
    { "source": "pathPattern", "pathPattern": "^/opt/approved/" }
  ]
}
```

> 想允許任何檔案路徑但仍控管網路來源，可用 `".*"` 作 `pathPattern`。

### 限制如何運作

- 限制在 marketplace 新增以及 plugin 安裝、更新、重新整理、**自動更新**時檢查
- 在任何網路或檔案系統操作之前檢查
- 大多數來源類型用**精確匹配**（URL 結尾的 `/`、`.git` 後綴、`ssh://` vs `https://` 視為不同）
- 若要支援多 URL 形式，優先用 `hostPattern` 項目
- 因為在受管設定中，**使用者與專案配置無法覆蓋**

> 💡 `strictKnownMarketplaces` 只限制能新增的內容，不會自動註冊。搭配 `extraKnownMarketplaces` 才能自動供應。

### 搭配 `disableSideloadFlags` 與 `pluginSuggestionMarketplaces`

- **`disableSideloadFlags`**：拒絕 CLI 旗標側載 plugin、agent、MCP 伺服器
- **`pluginSuggestionMarketplaces`**：允許清單化哪些 marketplace 的 plugin 可作為內容相關安裝建議

---

## 版本解析與發行通道

### 版本解析優先順序

Claude Code 依序檢查：

```
1. plugin.json 的 version
2. marketplace 項目的 version
3. plugin 來源的 git commit SHA
```

> 同時設 `plugin.json` 和 `marketplace.json` 的 `version` 時，**前者優先**（且會靜默使用）— 避免在兩處同時設。

### 設定固定版本

- 設 `version` → plugin 固定，使用者**只在版本變更時**收到更新
- 省略 → 每個新 commit 都是新版本（內部 / 積極開發適用）

### 發行通道範例

「穩定」與「最新」可分別指向不同 ref：

```json
// stable-tools marketplace
{
  "name": "stable-tools",
  "plugins": [
    {
      "name": "code-formatter",
      "source": { "source": "github", "repo": "acme-corp/code-formatter", "ref": "stable" }
    }
  ]
}
```

```json
// latest-tools marketplace
{
  "name": "latest-tools",
  "plugins": [
    {
      "name": "code-formatter",
      "source": { "source": "github", "repo": "acme-corp/code-formatter", "ref": "latest" }
    }
  ]
}
```

> ⚠️ 每個通道必須解析為不同版本。若用 `version`，`plugin.json` 在每個 ref 都要不同；若省略 `version`，不同 SHA 即可區分。

### 指派給使用者群組

```json
// 穩定群組
{ "extraKnownMarketplaces": { "stable-tools": { "source": { "source": "github", "repo": "acme-corp/stable-tools" } } } }

// 早期存取群組
{ "extraKnownMarketplaces": { "latest-tools": { "source": { "source": "github", "repo": "acme-corp/latest-tools" } } } }
```

### 固定依賴版本

Plugin 可用 semver 範圍限制依賴。慣例為 `{plugin-name}--v{version}` git 標籤。

---

## 重新命名或移除 Plugin

Plugin 的 `name` 是穩定識別碼，更動會破壞現有安裝。

- 想改 UI 顯示但保留識別 → 設 `displayName`、保持 `name` 不變
- 真的必須改 `name` 或從 `plugins` 移除 → 用頂層 `renames` 自動遷移

### 範例：重新命名 + 移除

```json
{
  "name": "acme-tools",
  "owner": { "name": "Acme" },
  "plugins": [
    { "name": "code-formatter", "source": "./plugins/code-formatter" }
  ],
  "renames": {
    "formatter": "code-formatter",
    "legacy-linter": null
  }
}
```

### 行為

- 指向新名稱 → 在新名稱下載入，並重寫 `enabledPlugins` / `pluginConfigs` 內的舊金鑰
- 指向 `null` → 刪除舊金鑰，通知 plugin 已從 marketplace 移除
- 用遠端來源 → 重新命名後會回報 `plugin-cache-miss`，使用者要跑一次 `/plugin install`

### 注意事項

- 把 `renames` 視為**僅附加歷史**：即使所有人都遷移完也保持舊項目
- Claude Code 會跟隨鏈：再次重命名時**新增**項目而不是編輯
- 受管設定是**唯讀**，不會自動重寫 → 通知會重複出現直到管理員更新
- 早期版本（v2.1.193 之前）會忽略 `renames`，舊名稱會出現 `plugin-not-found`
- 跑 `claude plugin validate .` 驗證，避免鏈形成循環

---

## 驗證與測試

### 驗證 JSON 語法

```bash
claude plugin validate .
```

或從 Claude Code 內：

```bash
/plugin validate .
```

> 指向 marketplace 目錄時，會檢查：
> - `marketplace.json` 架構錯誤
> - 重複的 plugin 名稱
> - 來源路徑遍歷
> - 每個 plugin 的 `plugin.json`
> - 項目 `version` 與 `plugin.json` 版本是否一致

### 常見驗證錯誤

| 錯誤 | 原因 | 解決 |
|:---|:---|:---|
| `File not found: .claude-plugin/marketplace.json` | 缺少 manifest | 建立必需欄位的檔案 |
| `Invalid JSON syntax: Unexpected token...` | JSON 語法錯誤 | 檢查逗號、引號 |
| `Duplicate plugin name "x" found in marketplace` | plugin 名稱重複 | 給每個 plugin 唯一名稱 |
| `plugins[0].source: Path contains ".."` | 來源路徑含 `..` | 用相對根目錄的路徑，不含 `..` |
| `YAML frontmatter failed to parse: ...` | skill / agent / command 的 frontmatter 無效 | 修正 YAML 語法 |
| `Invalid JSON syntax: ...`（hooks.json） | `hooks/hooks.json` 格式錯誤 | 修正 JSON；此錯誤會阻止整個 plugin 載入 |

### 警告（非阻擋）

- `Marketplace has no plugins defined`：未定義任何 plugin
- `No marketplace description provided`：未提供頂層 `description`
- `Plugin name "x" is not kebab-case`：名稱含大寫、空格、特殊字元

### 驗證個別 plugin

```bash
claude plugin validate ./plugins/my-plugin
```

### 本機測試完整流程

```bash
# 1. 新增本機 marketplace
/plugin marketplace add ./path/to/marketplace

# 2. 安裝測試 plugin
/plugin install test-plugin@marketplace-name

# 3. 確認功能
```

---

## CLI 指令參考

非互動式指令（用於腳本 / 自動化），等同於互動式 `/plugin marketplace` 指令。

### `claude plugin marketplace add`

```bash
claude plugin marketplace add <source> [options]
```

**引數**：GitHub `owner/repo`、git URL、`marketplace.json` 遠端 URL、或本機路徑。
- GitHub 簡寫可加 `@ref`：`acme-corp/repo@v2.0`
- git URL 可加 `#ref`：`https://.../repo.git#main`

> ⚠️ 自 v2.1.196 起，未帶協議的主機（如 `gitlab.example.com/team/plugins`）會被拒絕為無效的 `owner/repo`。

**選項**：

| 選項 | 描述 | 預設 |
|:---|:---|:---|
| `--scope <user\|project\|local>` | marketplace 位置 | `user` |
| `--sparse <paths...>` | 限制 git sparse-checkout 目錄 | — |

**範例**：

```bash
# GitHub 簡寫
claude plugin marketplace add acme-corp/claude-plugins

# 固定到 tag
claude plugin marketplace add acme-corp/claude-plugins@v2.0

# 非 GitHub git URL
claude plugin marketplace add https://gitlab.example.com/team/plugins.git

# 遠端 marketplace.json
claude plugin marketplace add https://example.com/marketplace.json

# 本機路徑
claude plugin marketplace add ./my-marketplace

# 專案範圍（團隊共享）
claude plugin marketplace add acme-corp/claude-plugins --scope project

# Monorepo sparse checkout
claude plugin marketplace add acme-corp/monorepo --sparse .claude-plugin plugins
```

### `claude plugin marketplace list`

```bash
claude plugin marketplace list [--json]
```

- 加上 `--json` 輸出 JSON，每項含 `name`、`source`、來源特定欄位（GitHub 的 `repo`、git/URL 的 `url`、本機的 `path`、固定的 `ref`）

### `claude plugin marketplace remove`

別名：`rm`

```bash
claude plugin marketplace remove <name> [options]
```

**引數**：marketplace 名稱（`marketplace.json` 的 `name`）

**選項**：

| 選項 | 描述 | 預設 |
|:---|:---|:---|
| `--scope <user\|project\|local>` | 限制移除範圍 | 所有範圍 |

> 從最後範圍移除時也會卸載從中安裝的 plugin。想保留 plugin 改用 `update`。

### `claude plugin marketplace update`

```bash
claude plugin marketplace update [name]
```

- 不指定 → 更新所有
- 種子管理的 marketplace → 會失敗（唯讀）

---

## 疑難排解

### 1. Marketplace 未載入

**症狀**：無法新增或看不到 plugin

**排查**：
- 驗證 URL 可存取
- 檢查 `.claude-plugin/marketplace.json` 存在
- 跑 `claude plugin validate` 確認 JSON 有效
- 私人 repo：確認有存取權

### 2. Marketplace 驗證錯誤

跑 `claude plugin validate .` 取得具體錯誤（見上方錯誤對照表）

### 3. Plugin 安裝失敗

- 驗證 plugin 來源 URL 可存取
- 確認 plugin 目錄含必需檔案
- GitHub 來源：確認 repo 公開或有權限
- 手動複製 / 下載測試來源
- 確認 `sha` 固定指向仍存在的 commit

### 4. 私人儲存庫驗證失敗

**手動安裝 / 更新**：
- 確認已登入：`gh auth status`
- 確認 credential helper：`git config --global credential.helper`
- 手動 clone 試試

**背景自動更新**：
- 預設情況下 background refresh 對 `git pull` 停用認證助手
- SSH（金鑰在 `ssh-agent`）不受影響
- 失敗時會重新複製，可能在大 repo 逾時
- 設定 `CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE=1` 保留副本
- 用 `gh auth setup-git` 配置助手
- 用 `CLAUDE_CODE_PLUGIN_GIT_TIMEOUT_MS` 提高逾時
- 用範圍限定的 git URL 重寫

### 5. 離線環境更新失敗

**症狀**：`git pull` 背景失敗，反覆重新複製也失敗

**解法**：

```bash
# 保留最後已知狀態
export CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE=1

# 完全離線：用 seed 目錄在建置時預填
export CLAUDE_CODE_PLUGIN_SEED_DIR=/opt/claude-seed
```

### 6. Git 操作逾時

預設 120 秒。大 repo / 慢網路可能逾時。

```bash
export CLAUDE_CODE_PLUGIN_GIT_TIMEOUT_MS=300000  # 5 分鐘
```

### 7. 相對路徑 plugin 在 URL-based marketplace 失敗

**症狀**：用 URL 加 marketplace，plugin 報「path not found」

**原因**：URL-based marketplace 只下載 `marketplace.json`，不下載其他檔案

**解法**：
- 改用外部來源（GitHub / npm / git URL）
- 或用 git-based marketplace（會 clone 整個 repo）

### 8. 安裝後找不到檔案

**症狀**：plugin 安裝了，但參考 plugin 目錄外檔案失敗

**原因**：plugin 被複製到快取目錄，不是就地使用。`../shared-utils` 這類路徑失效。

**解法**：見 [Plugin caching and file resolution](https://code.claude.com/docs/zh-TW/plugins-reference#plugin-caching-and-file-resolution)

---

## 相關文件

- [探索並安裝預先建立的 plugins](https://code.claude.com/docs/zh-TW/discover-plugins)
- [建立 Plugin](https://code.claude.com/docs/zh-TW/plugins)
- [Plugins 完整技術參考](https://code.claude.com/docs/zh-TW/plugins-reference)
- [Plugin 設定](https://code.claude.com/docs/zh-TW/settings#plugin-settings)
- [strictKnownMarketplaces 參考](https://code.claude.com/docs/zh-TW/settings#strictknownmarketplaces)
- [Plugin 依賴](https://code.claude.com/docs/zh-TW/plugin-dependencies)
- [Plugin 相關性](https://code.claude.com/docs/zh-TW/plugin-relevance)
- [GitHub Enterprise Server 上的 Marketplace](https://code.claude.com/docs/zh-TW/github-enterprise-server#plugin-marketplaces-on-ghes)
- [環境變數](https://code.claude.com/docs/zh-TW/env-vars#variables)

---

## 速查表

### 常用指令

| 用途 | 指令 |
|:---|:---|
| 新增 marketplace | `/plugin marketplace add <source>` |
| 安裝 plugin | `/plugin install <plugin>@<marketplace>` |
| 更新 marketplace | `/plugin marketplace update` |
| 驗證 | `claude plugin validate .` |
| 列出 marketplace | `claude plugin marketplace list` |
| 移除 marketplace | `claude plugin marketplace remove <name>` |

### 環境變數速查

| 變數 | 用途 |
|:---|:---|
| `CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1` | 私人 repo 改用 HTTPS（GitHub 簡寫來源） |
| `CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE=1` | 背景 pull 失敗時保留副本 |
| `CLAUDE_CODE_PLUGIN_GIT_TIMEOUT_MS` | 調整 git 操作逾時（毫秒） |
| `CLAUDE_CODE_PLUGIN_SEED_DIR` | 容器預填 plugin 目錄路徑 |
| `CLAUDE_CODE_PLUGIN_CACHE_DIR` | 安裝時直接寫入的路徑（搭配 SEED_DIR 用） |

### Plugin 來源速查

| 需求 | source 寫法 |
|:---|:---|
| 同 repo 內的本機 plugin | `"./plugins/my-plugin"` |
| GitHub repo | `{ "source": "github", "repo": "owner/repo" }` |
| 任意 git URL | `{ "source": "url", "url": "https://...git" }` |
| Monorepo 子目錄 | `{ "source": "git-subdir", "url": "...", "path": "tools/plugin" }` |
| npm 套件 | `{ "source": "npm", "package": "@scope/name" }` |
