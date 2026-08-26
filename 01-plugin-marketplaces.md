# 建立並分發 Plugin Marketplace

> 📖 系列：Claude Code Plugin 完整學習系列 #01
> 🌐 原文：[code.claude.com/docs/zh-TW/plugin-marketplaces](https://code.claude.com/docs/zh-TW/plugin-marketplaces)
> 📅 整理日期：2026 / 01
> 🎯 適用版本：Claude Code v2.1.x

## 本章你會學到

概念、流程、Schema 完整攻略

- 📚 **Marketplace 基礎**：理解什麼是 marketplace 與整體流程
- 🚀 **快速入門**：6 步驟建立本機 marketplace
- 📋 **Schema 完整攻略**：marketplace.json 與 plugin 項目所有欄位
- 🔌 **5 種 Plugin 來源**：git、npm、本機路徑等
- 🔒 **Strict Mode 與託管**：企業環境的安全管控
- 👥 **團隊預先配置**：pre-config 與 seed dir
- 🛡 **受管 Marketplace 限制**：strictKnownMarketplaces 設定
- 📤 **版本、發佈、驗證**：semver、發行通道、CLI 指令

## Part 1: Marketplace 基礎

概念、流程、必備檔案

## 什麼是 Plugin Marketplace？

**Plugin Marketplace** 是一個目錄，用來把 plugin 分發給其他人。它提供：

- ✅ **集中式探索**（讓人容易找到）
- ✅ **版本追蹤**（清楚知道用的是哪一版）
- ✅ **自動更新**（推送後使用者能拉新版本）
- ✅ **多種來源支援**（git 儲存庫、本機路徑、npm…）

一句話：Marketplace = 別人加入來源、安裝你寫的 plugin 的入口。

## 使用者端 3 個關鍵指令

| 指令 | 作用 |
|:-----|:-----|
| `/plugin marketplace add <source>` | 新增 marketplace 來源 |
| `/plugin install <plugin>@<marketplace>` | 安裝特定 plugin |
| `/plugin marketplace update` | 重新整理本機副本 |

## Part 2: 快速入門：建立本機 Marketplace

6 步驟完成第一個 marketplace

## 建立 Marketplace 的 6 個步驟

從目錄結構到第一個 plugin 啟用

### 1. 建立目錄結構

mkdir + 3 層子目錄

### 2. 建立 SKILL.md

YAML frontmatter + 說明

### 3. 建立 plugin manifest

plugin.json name + version

### 4. 建立 marketplace 目錄

marketplace.json 含 plugins 列表

### 5. 新增並安裝

/plugin marketplace add + install

### 6. 使用 skill

plugin 命名空間呼叫

## 範例：完整程式碼（上）

Step 1-3 的程式碼

```bash
mkdir -p my-marketplace/.claude-plugin
mkdir -p my-marketplace/plugins/quality-review-plugin/.claude-plugin
mkdir -p my-marketplace/plugins/quality-review-plugin/skills/quality-review
```

`my-marketplace/plugins/quality-review-plugin/skills/quality-review/SKILL.md`：

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

## 範例：完整程式碼（下）

Step 4-6 的程式碼

`my-marketplace/plugins/quality-review-plugin/.claude-plugin/plugin.json`：

```json
{
  "name": "quality-review-plugin",
  "description": "新增 quality-review skill 以進行快速程式碼審查",
  "version": "1.0.0"
}
```

`my-marketplace/.claude-plugin/marketplace.json`：

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

執行：

```bash
/plugin marketplace add ./my-marketplace
/plugin install quality-review-plugin@my-plugins
/quality-review-plugin:quality-review
```

## Part 3: Marketplace 與 Plugin Schema

完整欄位速查

## Marketplace 完整範例

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

## Marketplace Schema

完整欄位速查

| 欄位 | 類型 | 必填 | 描述 |
|:-----|:-----|:-----|:-----|
| `name` | string | 是 | Marketplace 識別碼（kebab-case） |
| `owner` | object | 是 | Marketplace 維護者資訊 |
| `plugins` | array | 是 | 可用 plugin 的清單 |
| `metadata` | object | 否 | 額外的 metadata |
| `description` | string | 否 | marketplace 描述 |

## Plugin 項目欄位

| 欄位 | 類型 | 必填 | 描述 |
|:-----|:-----|:-----|:-----|
| `name` | string | 是 | Plugin 名稱（kebab-case） |
| `source` | string 或 object | 是 | Plugin 來源（路徑或物件） |
| `description` | string | 否 | Plugin 描述 |
| `version` | string | 否 | 語意化版本 |
| `author` | object | 否 | 作者資訊 |
| `homepage` | string | 否 | Plugin 首頁 |
| `repository` | string | 否 | source code URL |
| `license` | string | 否 | 授權類型 |
| `keywords` | array | 否 | 搜尋標籤 |

## 進階 Plugin 項目範例

含完整 metadata 的 plugin 項目

```json
{
  "name": "deployment-tools",
  "source": {
    "source": "github",
    "repo": "company/deploy-plugin"
  },
  "description": "部署自動化工具",
  "version": "2.1.0",
  "author": {
    "name": "DevTools Team",
    "email": "devtools@example.com"
  },
  "homepage": "https://github.com/company/deploy-plugin",
  "license": "MIT",
  "keywords": ["deployment", "automation", "ci-cd"]
}
```

## Part 4: Plugin 來源（5 種）

從本機路徑到 npm 套件

## 5 種 Plugin 來源

| 來源類型 | 語法 | 用途 |
|:--------|:-----|:-----|
| 相對路徑 | `"./plugins/foo"` 或 `"../shared/foo"` | 本機開發 |
| GitHub | `{"source": "github", "repo": "owner/repo"}` | 公開 GitHub 託管 |
| Git URL | `{"source": "git", "url": "https://..."}` | GitLab、Bitbucket 等 |
| npm | `{"source": "npm", "package": "foo"}` | npm 套件形式 |
| 環境變數 | `"${MY_PLUGIN_DIR}"` | CI/CD 動態配置 |

## 相對路徑的陷阱

⚠️ 相對路徑是**相對於 marketplace.json 所在位置**，不是 marketplace 註冊位置

```json
{
  "name": "company-tools",
  "plugins": [
    {
      "name": "local-plugin",
      "source": "./plugins/local-plugin"
    }
  ]
}
```

> 路徑 `"./plugins/local-plugin"` 是相對於 `marketplace.json`，所以 plugin 必須在 `marketplace.json` 同目錄下的 `plugins/` 子資料夾。

## Part 5: Strict Mode 與託管

企業環境的安全管控

## Strict Mode 嚴格模式

`strict` 欄位控制 `plugin.json` 是否為元件定義的權威

| 值 | 行為 |
|:---|:---|
| `true`（預設） | `plugin.json` 為權威。marketplace 項目可補充元件。 |
| `false` | marketplace 項目是完整定義。若 plugin 也有 `plugin.json` 衝突則無法載入。 |

- **`strict: true`**：plugin 有自己的 `plugin.json` 並自行管理元件（大多數情境）
- **`strict: false`**：marketplace 運營商要完全控制（重組或策劃 plugin 的元件）

## 託管並分發 Marketplace

四種託管方式

### 1. GitHub（推薦）

```bash
/plugin marketplace add owner/repo
```

### 2. 其他 Git 主機

```bash
/plugin marketplace add https://gitlab.com/company/plugins.git
```

### 3. 私人儲存庫

需要 git 認證助手：
- HTTPS：`gh auth login`、Keychain、`git-credential-store`
- SSH：`known_hosts` + `ssh-agent`

### 4. 本機測試

```bash
/plugin marketplace add ./my-marketplace
```

## 私人 Repo 認證：3 種解法

| 情境 | 解法 |
|:-----|:-----|
| 背景更新失敗 | `CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE=1` |
| HTTPS 認證 | `gh auth setup-git` |
| 全域 token 嵌入 | `git config --global url."https://x-access-token:TOKEN@github.com/...".insteadOf "https://github.com/..."` |

## Part 6: 為團隊與容器預先配置

pre-config 與 seed dir

## 為團隊預先配置 Marketplace

把 marketplace 加到 `.claude/settings.json`，團隊成員信任專案資料夾時會自動被提示安裝：

```json
{
  "extraKnownMarketplaces": {
    "company-tools": {
      "source": "github",
      "repo": "company/plugins"
    }
  }
}
```

> 信任 `.claude/settings.json` 的使用者會在 `/plugin` 看到提示，選擇性安裝

## 為容器預先填充 Plugin

CI/CD 環境可用 `seed-dir` 在容器建立時預先安裝 plugins：

```bash
# 在建置腳本中
mkdir -p /workspace/.claude/plugins
/plugin install code-formatter@company-tools --scope project
```

或用 `--plugin-dir` 旗標載入：

```bash
claude --plugin-dir /workspace/seed-plugins/code-formatter
```

> 容器預先填充適合 ephemeral environments 與 CI runners

## Part 7: 受管 Marketplace 限制

企業級安全管控

## 受管 Marketplace 限制

`strictKnownMarketplaces` 強制使用者只能使用特定 marketplaces

```json
{
  "strictKnownMarketplaces": [
    {
      "source": "github",
      "repo": "company/approved-plugins"
    }
  ]
}
```

> 設定後，使用者嘗試新增未在清單內的 marketplace 會被拒絕

## strictKnownMarketplaces 實戰配置

```json
{
  "strictKnownMarketplaces": [
    {
      "source": "github",
      "repo": "acme-corp/approved-plugins"
    },
    {
      "source": "github",
      "repo": "acme-corp/internal-tools"
    }
  ],
  "blockedMarketplaces": [
    {
      "source": "github",
      "repo": "untrusted/random-plugins"
    }
  ]
}
```

> 也可設定 `blockedMarketplaces` 明確禁止某些 marketplace

## Part 8: 版本、發佈、驗證

semver、發行通道、CLI 指令

## 版本解析與發行通道

Marketplace 支援兩種發行通道

| 通道 | 行為 |
|:-----|:-----|
| `stable` | 只接受語意化版本（`1.2.3`） |
| `latest` | 接受任意 git ref（branch、tag、commit SHA） |

預設使用 `stable`，可在 marketplace.json 設定：

```json
{
  "name": "my-plugins",
  "releaseChannel": "stable"
}
```

## 穩定 vs 最新 發行通道

| 面向 | stable | latest |
|:-----|:-------|:-------|
| 版本格式 | 必須 `X.Y.Z` | 任意 git ref |
| 適用場景 | 生產環境 | 開發測試 |
| 更新頻率 | 受版本控制 | 跟隨 git push |
| 相容性 | 嚴格 | 寬鬆 |

## 重新命名或移除 Plugin

從 marketplace.json 移除 plugin 項目即可

**重新命名**：

```json
{
  "plugins": [
    {
      "name": "new-name",
      "source": "./plugins/foo"
    }
  ]
}
```

**移除**：直接從 `plugins` 陣列刪除項目，使用者下次 `update` 時會看到 plugin 被移除。

> 使用者已安裝的 plugin 不會自動解除安裝，但功能會停用

## 驗證與測試

用 `claude plugin validate` 驗證 marketplace.json 與所有 plugin 項目

```bash
claude plugin validate
```

會檢查：
- marketplace.json 結構
- 每個 plugin 項目的必填欄位
- source 路徑或 URL 是否有效
- version 格式（如使用 stable 通道）

## CLI 指令速查

| 指令 | 用途 |
|:-----|:-----|
| `/plugin marketplace add <source>` | 新增 marketplace 來源 |
| `/plugin marketplace remove <name>` | 移除 marketplace |
| `/plugin marketplace list` | 列出已註冊 marketplaces |
| `/plugin marketplace update` | 重新整理本機副本 |
| `/plugin install <plugin>@<marketplace>` | 安裝 plugin |
| `/plugin enable <plugin>` | 啟用已停用的 plugin |
| `/plugin disable <plugin>` | 停用 plugin（不解除安裝） |
| `/plugin uninstall <plugin>` | 解除安裝 plugin |

## 疑難排解速查

| 問題 | 排查方向 |
|:-----|:---------|
| Marketplace 無法新增 | 檢查 URL/路徑是否正確 |
| Plugin 找不到 | 確認 plugin 名稱與 marketplace 內宣告一致 |
| 安裝失敗 | 用 `claude --debug` 查看詳細錯誤 |
| 更新失敗 | 私人 repo 認證問題，檢查 git credentials |
| Skills 未出現 | 用 `/reload-plugins` 重整 |
| Strict mode 衝突 | 確認 plugin.json 與 marketplace 項目一致 |

## 重點回顧

- Marketplace 是 plugin 的分發目錄，提供集中式探索與版本管理
- 用 `marketplace.json` 定義 plugin 列表與來源
- 5 種來源：相對路徑、GitHub、Git URL、npm、環境變數
- Strict Mode 控制 plugin.json 與 marketplace 項目的元件合併行為
- `strictKnownMarketplaces` 強制企業級安全管控
- `stable` 通道用 semver，`latest` 通道接受任意 git ref
- 用 `claude plugin validate` 驗證設定

- 🎯 立刻：在 `/plugin` 新增第一個 marketplace
- 📚 30 分鐘：翻完 marketplace.json 完整欄位
- 🛠 2 小時：建立含 3 個 plugins 的本機 marketplace
- 🚀 一週：把團隊 marketplace 部署到 GitHub 並邀請成員
