# Claude Code Plugin 完整學習系列

> 一套系統化的 Claude Code 擴展開發教材，由官方文件整理而成。
> 共 8 份文件，涵蓋從新手到專家的完整學習路徑。
> 總計約 250 KB / 5000+ 行繁體中文內容。

## 為什麼需要了解 Claude Code Plugin？

擴展 Claude 的能力 · 打造個人化 AI 工作流

| 😐 預設 Claude Code | 🚀 使用 Plugin 後 |
| :--- | :--- |
| 通用對話能力 | 可重複使用的 Skills（/command） |
| 內建工具：檔案、搜尋、Bash | 隔離上下文的 Subagents |
| 每次 session 都要重新解釋 | 事件驅動的 Hooks（自動化） |
| 無法自動化重複任務 | 團隊共享的 Marketplace |
| 無法團隊共享設定 | 自動化的格式化與檢查 |
| 個人風格無法持久化 | 個人化 AI 助手工作流 |

## 這套系列的規模

完整覆蓋 Claude Code Plugin 系統的各個面向

### 8 份

完整文件

### 6,682 行

繁體中文內容

### 272 KB

總檔案大小

> 📊 涵蓋 Claude Code v2.1.x（到 v2.1.236），所有內容整理自官方文件

## Part 1: Claude Code 擴展生態系全景

了解整體架構與各元件的角色

## Claude Code 擴展元件：核心元件（上）

從基礎規則到進階自動化，層層堆疊的擴展能力

### CLAUDE.md

專案說明書 · 每次 session 自動載入的規則

### Skills

可重用知識庫 · `/name` 觸發，隨叫隨到

### Subagents

隔離代理人 · 獨立 context 的子任務

### Hooks

事件自動化 · 確定性觸發的腳本

## Claude Code 擴展元件：核心元件（下）

從連接外部到包裝分享的高階元件

### MCP

外部服務 · 連接資料庫、API、瀏覽器

### Plugins

包裝箱 · 把上述元件打包成可發布單元

### Marketplaces

商店目錄 · 多個 plugin 的集合 + 版本管理

## 何時該用哪個元件？

| 需求 | 推薦元件 | 原因 |
| :--- | :--- | :--- |
| 每次 session 都要遵守的規則 | CLAUDE.md | 自動載入 |
| 重複使用的 SOP 或專業知識 | Skill | 隨時叫用 |
| 需要上下文隔離的任務 | Subagent | 不污染主對話 |
| 每次檔案編輯後自動跑 X | Hook | 確定性觸發 |
| 連接外部資料庫 / API | MCP | 標準化介面 |
| 想把上述組合成可發布的套件 | Plugin | 統一打包 |
| 想分享給團隊 / 社群 | Marketplace | 版本管理 + 發布 |

## Part 2: 8 份系列文件導覽

完整檔案地圖與學習路徑

## 8 份系列文件總覽

| 編號 | 檔案 | 主題 | 大小 | 你會學到 | 適合對象 |
| :---: | :--- | :--- | :---: | :--- | :--- |
| **00** | `00-claude-code-plugins-series.md` | 系列總覽 | 2.4 KB | 整體架構與導讀 | 所有人 |
| **01** | `01-plugin-marketplaces.md` | Plugin Marketplaces | 30 KB | 如何建立、託管、發布 plugin 集合 | 想分享 plugin 的人 |
| **02** | `02-plugins.md` | Plugin 開發指南 | 13 KB | 從零建立第一個 plugin | plugin 開發新手 |
| **03** | `03-plugins-reference.md` | Plugin 技術參考 | 29 KB | 完整架構、CLI、進階設定 | 進階開發者 |
| **04** | `04-skills.md` | Skills 完整指南 | 30 KB | Skills 的設計、撰寫、評估 | 想自訂 Claude 行為的人 |
| **05** | `05-subagents.md` | Subagents 自訂指南 | 26 KB | 隔離上下文、平行任務 | 想做進階自動化的人 |
| **06** | `06-hooks.md` | Hooks 自動化指南 | 44 KB | 事件驅動的工作流自動化 | 想做確定性自動化的人 |
| **07** | `07-discover-plugins.md` | 探索並安裝 Plugins | 12 KB | 從市場找到並使用 plugin | 一般使用者 |

> 📖 從 00 開始讀，可依需求選擇深入哪些章節

## 🟢 新手入門路徑（建議 1-2 天）

從零開始，快速建立第一個 plugin

### 1. 先讀 07

探索並安裝 · 實際裝幾個 plugin 玩玩

### 2. 讀 04

Skills · 學會寫簡單的 skill

### 3. 讀 02

Plugin 開發 · 把 skill 包成 plugin

### 4. 動手做

claude plugin init · 建立第一個 plugin！

> 🎯 重點：動手做比讀完更重要！每讀完一份，立刻實作一次。

## 🟡 進階使用者路徑（建議 3-5 天）

掌握 Subagents、Hooks、Marketplace

### 1. 讀 05

Subagents · 學會委派任務、隔離 context

### 2. 讀 06

Hooks · 學會事件自動化

### 3. 讀 01

Marketplace · 開始分享你的 plugin

### 4. 實戰

建立團隊 marketplace

> 📘 學會整合所有元件，建立複雜的多功能 plugin

## 🔴 專家 / 團隊負責人路徑（建議 1 週+）

掌握完整技術規格，部署企業級 plugin 系統

### 1. 讀 03

技術參考 · 掌握所有細節

### 2. 回頭讀 01

Marketplace 進階 · 建立企業 marketplace

### 3. 整合所有元件

建立複雜的多功能 plugin

### 4. 動手做

部署企業級 plugin 系統

> 💡 整合所有元件，部署企業級 plugin 系統

## Part 3: 任務導向索引

快速找到你要的章節

## 任務導向索引

| 你的目標 | 該看哪份 |
| :--- | :--- |
| 找別人寫好的 plugin 來用 | [07-discover-plugins](./07-discover-plugins.md) |
| 寫第一個 plugin | [02-plugins](./02-plugins.md) |
| 寫可重用的 `/command` 指令 | [04-skills](./04-skills.md) |
| 寫可重用的「代理人」 | [05-subagents](./05-subagents.md) |
| 編輯檔案後自動跑測試 | [06-hooks](./06-hooks.md) |
| 阻擋危險命令（`rm -rf`） | [06-hooks § PreToolUse](./06-hooks.md) |
| 部署到團隊 / 公司 | [01-plugin-marketplaces](./01-plugin-marketplaces.md) |
| 提交到 Anthropic 官方 | [02-plugins § 提交](./02-plugins.md) |
| 理解完整技術規格 | [03-plugins-reference](./03-plugins-reference.md) |
| 查特定 CLI 指令用法 | [03-plugins-reference § CLI](./03-plugins-reference.md) |
| 解決疑難問題 | 各文件最後的「疑難排解」章節 |

## 推薦先裝的官方 Plugin

| Plugin | 用途 |
| :--- | :--- |
| `commit-commands` | Git 提交工作流（推薦新手先裝） |
| `pr-review-toolkit` | PR 審查工具 |
| `security-guidance` | 自動安全審查 |
| `typescript-lsp` / `pyright-lsp` | 程式碼智慧 |
| `explanatory-output-style` | 學習模式 |

> 💡 裝完 `commit-commands` 和 `pr-review-toolkit` 就足以應付大多數日常工作

## Part 4: 7 個元件深入介紹

逐一認識每個元件的能力

## 元件 1/7：CLAUDE.md

每次 session 自動載入的專案規則

CLAUDE.md 是放在專案根目錄的 Markdown 檔，Claude Code 每次啟動時會自動載入。內容包括：
- 專案架構說明
- 編碼規範
- 常用指令
- 禁止事項

> 💡 CLAUDE.md 是最低成本的擴展方式，適合團隊規範

## 元件 2/7：Skills

可重用的專業知識庫

Skills 是放在 `.claude/skills/` 目錄下的 SKILL.md 檔案，可用 `/skill-name` 觸發。內容包括：
- 漸進式揭露的知識
- YAML frontmatter 描述
- 可選的支援檔案

> 💡 Skills 適合 SOP、技術審查清單、團隊最佳實踐

## 元件 3/7：Subagents

獨立上下文的代理人

Subagents 是透過 `.claude/agents/` 定義的獨立 Claude 實例，可：
- 隔離 context（不污染主對話）
- 平行執行任務
- 使用不同模型
- 限制可用工具

> 💡 Subagents 適合大量輸出的任務（測試、日誌分析）

## 元件 4/7：Hooks

事件驅動的自動化腳本

Hooks 在特定事件發生時自動執行腳本：
- PreToolUse（工具執行前）
- PostToolUse（工具執行後）
- Notification（通知時）
- Stop（結束時）

> 💡 Hooks 適合「檔案編輯後自動 format」、「阻擋危險命令」

## 元件 5/7：MCP (Model Context Protocol)

連接外部服務的標準介面

MCP 是 Anthropic 提出的標準協議，讓 Claude Code 連接：
- 資料庫（PostgreSQL、MongoDB）
- API（GitHub、Slack）
- 瀏覽器（Puppeteer、Chrome）
- 自訂服務

> 💡 MCP 是「擴展 Claude 能力到外部世界」的標準方式

## 元件 6/7：Plugins

把元件打包成可發布單元

Plugin 是包裝多個元件的目錄，可包含：
- Skills
- Subagents
- Hooks
- MCP servers
- Commands

> 💡 Plugin 是「可分享、可安裝」的元件集合

## 元件 7/7：Marketplaces

多個 plugin 的集合 + 版本管理

Marketplace 是 plugin 的目錄，支援：
- 從 GitHub 直接託管
- 版本控制
- 受管部署
- 團隊預先配置

> 💡 Marketplace 是「plugin 的商店」，適合企業內部分發

## 實戰：所有元件的組合應用

一個真實的 plugin 包含所有元件

### Plugin 結構

`.claude-plugin/plugin.json` 定義 metadata + 元件目錄

### Skills + Subagents

用 Skill 觸發 Subagent 執行隔離任務

### Hooks + MCP

用 Hook 在檔案變更時自動同步到資料庫

> 📘 學會組合元件是 plugin 開發的核心能力

## Part 5: 實戰案例與最佳實踐

從真實案例學習，避開常見陷阱

## 4 個真實世界的 Plugin 使用案例

### 1. 程式碼審查 plugin

用 Skill 定義審查清單 + Subagent 隔離審查 context

### 2. 文件生成 plugin

用 Hook 在 README 變更時自動重新生成

### 3. 測試自動化 plugin

用 Subagent 執行測試，Hook 自動收集結果

### 4. 部署工作流 plugin

用 MCP 連接部署服務，Hook 自動觸發部署

> 📘 從真實案例學習 plugin 的組合模式

## 開發 Plugin 的最佳實踐

- 保持 plugin 單一職責（一個 plugin 做一件事）
- 提供清楚的 README 和範例
- 用 frontmatter 描述每個 skill
- 提供預設設定但允許覆寫
- 測試在不同 Claude Code 版本下的相容性
- 善用 Subagent 隔離大量輸出
- 用 Hook 自動化重複任務
- 把 plugin 拆成小元件方便重用

> 💡 好的 plugin 是「可組合、可重用、可測試」

## 新手常見的 5 個陷阱

- **插件過於龐大**：把所有功能塞進一個 plugin，難以維護
- **缺少文件**：沒有 README，使用者不知道怎麼用
- **硬編碼路徑**：無法在不同環境下運作
- **忽略版本控制**：更新後破壞舊用戶的設定
- **沒考慮 hooks 的副作用**：hook 失敗導致主流程中斷

> 💡 從一開始就避免這些陷阱，省下未來重構成本

## 📊 本簡報系列總覽

| 編號 | 主題 | 適合誰 |
| :---: | :--- | :--- |
| 00 | 系列總覽（這份） | 所有人 |
| 01 | Plugin Marketplaces | 想分享 plugin 的人 |
| 02 | Plugin 開發指南 | plugin 開發新手 |
| 03 | Plugin 技術參考 | 進階開發者 |
| 04 | Skills 完整指南 | 想自訂 Claude 行為的人 |
| 05 | Subagents 自訂指南 | 想做進階自動化的人 |
| 06 | Hooks 自動化指南 | 想做確定性自動化的人 |
| 07 | 探索並安裝 Plugins | 一般使用者 |

## 開始你的 Plugin 之旅 🚀

從 [02-plugins](./02-plugins.md) 開始，建立你的第一個 plugin

建立日期：2026/01 | 整理自官方文件 · 繁體中文教學用途

## 📜 授權與來源

- **內容來源**：所有內容整理自 [code.claude.com/docs](https://code.claude.com/docs)
- **授權方式**：整理自官方文件，繁體中文教學用途
- **建立日期**：2026/01
- **對應 Claude Code 版本**：v2.1.x（到 v2.1.236）
