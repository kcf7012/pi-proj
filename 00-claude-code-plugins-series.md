# Claude Code Plugin 完整學習系列

> 一套系統化的 Claude Code 擴展開發教材，由官方文件整理而成。
> 共 8 份文件，涵蓋從新手到專家的完整學習路徑。
> 總計約 250 KB / 5000+ 行繁體中文內容。

## 📚 系列目錄

本系列依「使用 → 開發 → 進階」的學習路徑編排：

| 編號 | 檔案 | 主題 | 大小 | 你會學到 | 適合對象 |
|:----:|:-----|:-----|:----:|:---------|:---------|
| **00** | `00-claude-code-plugins-series.md` | 系列總覽 | 2.4 KB | 整體架構與導讀 | 所有人 |
| **01** | `01-plugin-marketplaces.md` | Plugin Marketplaces | 30 KB | 如何建立、託管、發布 plugin 集合 | 想分享 plugin 的人 |
| **02** | `02-plugins.md` | Plugin 開發指南 | 13 KB | 從零建立第一個 plugin | plugin 開發新手 |
| **03** | `03-plugins-reference.md` | Plugin 技術參考 | 29 KB | 完整架構、CLI、進階設定 | 進階開發者 |
| **04** | `04-skills.md` | Skills 完整指南 | 30 KB | Skills 的設計、撰寫、評估 | 想自訂 Claude 行為的人 |
| **05** | `05-subagents.md` | Subagents 自訂指南 | 26 KB | 隔離上下文、平行任務 | 想做進階自動化的人 |
| **06** | `06-hooks.md` | Hooks 自動化指南 | 44 KB | 事件驅動的工作流自動化 | 想做確定性自動化的人 |
| **07** | `07-discover-plugins.md` | 探索並安裝 Plugins | 12 KB | 從市場找到並使用 plugin | 一般使用者 |

## 🎯 學習路徑建議

### 🟢 新手入門（建議 1-2 天）
1. **先讀 07**（探索並安裝）→ 實際裝幾個 plugin 玩玩
2. **讀 04**（Skills）→ 學會寫簡單的 skill
3. **讀 02**（Plugin 開發）→ 把 skill 包成 plugin
4. 動手做：用 `claude plugin init` 建立你的第一個 plugin

### 🟡 進階使用者（建議 3-5 天）
1. **讀 05**（Subagents）→ 學會委派任務、隔離 context
2. **讀 06**（Hooks）→ 學會事件自動化
3. **讀 01**（Marketplace）→ 開始分享你的 plugin
4. 動手做：建立團隊專屬的 marketplace

### 🔴 專家 / 團隊負責人（建議 1 週+）
1. **讀 03**（技術參考）→ 掌握所有細節
2. **回頭讀 01**（Marketplace 進階）→ 建立企業 marketplace
3. **整合所有元件** → 建立複雜的多功能 plugin
4. 動手做：部署企業級 plugin 系統

## 🧭 Claude Code 擴展全景

在深入閱讀前，先建立全貌：

```
Claude Code 擴展生態系
├── CLAUDE.md               → 每次 session 都會看到的「專案說明書」
├── Skills                  → 可重複使用的指令知識庫（/name 觸發）
├── Subagents               → 隔離上下文的子代理人
├── Hooks                   → 事件驅動的確定性自動化
├── MCP                     → 連接外部服務
├── Plugins                 → 上述所有元件的「包裝箱」
└── Marketplaces            → 多個 plugin 的「商店目錄」
```

每個元件的最佳使用時機：

| 需求 | 推薦元件 | 原因 |
|:-----|:---------|:-----|
| 「每次 session 都要遵守的規則」 | CLAUDE.md | 自動載入 |
| 「重複使用的 SOP 或專業知識」 | Skill | 隨時叫用 |
| 「需要上下文隔離的任務」 | Subagent | 不污染主對話 |
| 「每次檔案編輯後自動跑 X」 | Hook | 確定性觸發 |
| 「連接外部資料庫 / API」 | MCP | 標準化介面 |
| 「想把上述組合成可發布的套件」 | Plugin | 統一打包 |
| 「想分享給團隊 / 社群」 | Marketplace | 版本管理 + 發布 |

## 📖 配套資源

### 官方資源
- **官方文件**：[code.claude.com/docs](https://code.claude.com/docs)
- **官方 Plugin 範例**：[github.com/anthropics/claude-code/tree/main/plugins](https://github.com/anthropics/claude-code/tree/main/plugins)
- **社群 Marketplace**：[github.com/anthropics/claude-plugins-community](https://github.com/anthropics/claude-plugins-community)
- **官方 Marketplace**：[github.com/anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official)

### 必裝的官方 Plugin（從 Marketplace）
| Plugin | 用途 |
|:-------|:-----|
| `commit-commands` | Git 提交工作流（推薦新手先裝） |
| `pr-review-toolkit` | PR 審查工具 |
| `security-guidance` | 自動安全審查 |
| `typescript-lsp` / `pyright-lsp` | 程式碼智慧 |
| `explanatory-output-style` | 學習模式 |

---

## 🔍 內容索引：你可以從這裡開始搜尋

### 想要做某個特定的事？

| 你的目標 | 該看哪份 |
|:---------|:---------|
| 找別人寫好的 plugin 來用 | [07-discover-plugins.md](./07-discover-plugins.md) |
| 寫第一個 plugin | [02-plugins.md](./02-plugins.md) |
| 寫可重用的 `/command` 指令 | [04-skills.md](./04-skills.md) |
| 寫可重用的「代理人」 | [05-subagents.md](./05-subagents.md) |
| 編輯檔案後自動跑測試 | [06-hooks.md](./06-hooks.md) |
| 阻擋危險命令（`rm -rf`） | [06-hooks.md § PreToolUse](./06-hooks.md#pretooluse) |
| 部署到團隊/公司 | [01-plugin-marketplaces.md](./01-plugin-marketplaces.md) |
| 提交到 Anthropic 官方 | [02-plugins.md § 提交](./02-plugins.md#將你的-plugin-提交到官方社群-marketplace) |
| 理解完整技術規格 | [03-plugins-reference.md](./03-plugins-reference.md) |
| 查特定 CLI 指令用法 | [03-plugins-reference.md § CLI](./03-plugins-reference.md#cli-完整指令參考) |
| 解決疑難問題 | 各文件最後的「疑難排解」章節 |

## 🤝 貢獻與回饋

這份系列整理自 Claude Code 官方文件。隨著 Claude Code 版本演進，部分內容可能會過時。

如發現錯誤或有想補充的主題，歡迎一起完善！

---

## 📜 授權與來源

- **內容來源**：所有內容整理自 [code.claude.com/docs](https://code.claude.com/docs) 官方文件
- **授權方式**：原始官方文件由 Anthropic 發布，本系列整理為繁體中文教學用途
- **引用建議**：如需引用，建議註明「整理自 Claude Code 官方文件」並附上原文連結

---

## 🔄 變更紀錄

| 日期 | 版本 | 說明 |
|:-----|:-----|:-----|
| 2026/01 | 1.0 | 初版發布，涵蓋 Claude Code v2.1.x（到 v2.1.236） |

---

**版本資訊**
- 整理日期：2026/01
- 對應 Claude Code 版本：v2.1.x（涵蓋到 v2.1.236）
- 文件來源：code.claude.com/docs（中文版與英文版混合）
