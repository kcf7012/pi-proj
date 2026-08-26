# 探索並安裝 Plugin

> 📖 系列：Claude Code Plugin 完整學習系列 #07
> 🌐 原文：[code.claude.com/docs/zh-TW/discover-plugins](https://code.claude.com/docs/zh-TW/discover-plugins)
> 📅 整理日期：2026 / 01
> 🎯 適用版本：Claude Code v2.1.x

## 本章你會學到

從瀏覽到管理的完整攻略

- 🏪 **Plugin 與 Marketplace**：先搞懂「商店 vs 商品」
- 🔌 **六類實用 Plugin 速覽**：從語言伺服器到安全審查
- 💻 **使用 /plugin 介面**：互動式管理 plugin
- 📥 **新增 Marketplace 來源**：從 6 種來源中挑選
- ⚙️ **安裝與管理**：4 種範圍 + 6 個指令

## Part 1: Plugin 與 Marketplace

先搞懂「商店 vs 商品」

## Plugin 與 Marketplace 的關係

- **Marketplace** = 商店（plugin 的目錄）
- **Plugin** = 商品（實際的擴展套件）

```
Marketplace (商店)
├── Plugin A
├── Plugin B
└── Plugin C

每個 Marketplace 可包含多個 Plugins
```

## 官方 Anthropic Marketplace

Anthropic 提供 3 個官方 marketplaces：

| 名稱 | 用途 |
|:-----|:-----|
| `claude-plugins-official` | Anthropic 精選的官方 plugins |
| `claude-community` | 社群貢獻 plugins（審查後納入）|
| `claude-code-templates` | 範本與 starter kits |

> 第一次啟動 Claude Code 時會自動新增官方 marketplace

## Part 2: 六類實用 Plugin 速覽

從語言伺服器到安全審查

## 程式碼智慧 Plugin（LSP）

提供 IDE 等級的程式碼智慧（自動完成、跳轉定義、錯誤檢查）

推薦 plugins：
- `typescript-lsp`
- `pyright-lsp`
- `rust-analyzer-lsp`
- `gopls`

## 外部整合 Plugin（MCP 預設配置）

連接外部服務（資料庫、API、瀏覽器）

推薦 plugins：
- `github` — GitHub API
- `slack` — Slack 通知
- `postgres` — PostgreSQL 資料庫

## 其他四類實用 Plugin

| 類型 | 推薦 | 用途 |
|:-----|:-----|:-----|
| 安全審查 | `security-guidance` | 自動偵測漏洞 |
| 開發工作流程 | `commit-commands` | Git 提交流程 |
| 輸出樣式 | `explanatory-output-style` | 學習模式 |
| 文件生成 | `feature-dev` | 完整功能開發 |

## Part 3: 使用 /plugin 介面

互動式管理 plugin

## /plugin 介面：4 個標籤

進入 `/plugin` 介面可看到 4 個標籤：

1. **Discover**：瀏覽可用的 plugins
2. **Installed**：已安裝的 plugins
3. **Marketplaces**：管理 marketplaces
4. **Settings**：plugin 設定

> Discover 標籤可依類別篩選（語言、整合、安全等）

## Part 4: 新增 Marketplace 來源

從 6 種來源中挑選

## 新增 Marketplace：6 種來源

```bash
# 1. GitHub（公開）
/plugin marketplace add anthropics/claude-plugins-official

# 2. GitHub（私人）
/plugin marketplace add acme-corp/internal-plugins

# 3. 其他 Git 主機
/plugin marketplace add https://gitlab.com/company/plugins.git

# 4. 本機路徑
/plugin marketplace add ./my-marketplace

# 5. 環境變數
/plugin marketplace add ${MY_MARKETPLACE_DIR}

# 6. URL-based
/plugin marketplace add https://example.com/marketplace.json
```

## URL-based vs Git-based

| 類型 | 優點 | 缺點 |
|:-----|:-----|:-----|
| Git-based | 版本控制、可追蹤變更 | 需要 git host |
| URL-based | 簡單、靜態託管 | 無版本控制 |

## Part 5: 安裝與管理

4 種範圍 + 6 個指令

## 安裝 Plugin

```bash
# 從已註冊的 marketplace 安裝
/plugin install <plugin>@<marketplace>

# 從 URL 直接安裝
/plugin install https://example.com/plugin.zip

# 從本機路徑安裝
/plugin install ./my-plugin
```

## 4 種安裝範圍

| 範圍 | 位置 | 適用 |
|:-----|:-----|:-----|
| User | `~/.claude/plugins/` | 個人所有專案 |
| Project | `.claude/plugins/` | 當前專案（可共享）|
| Local | `.claude/plugins/local/` | 當前專案（gitignored）|
| Plugin | `<plugin>/...` | plugin 內附 |

## 管理已安裝的 Plugin

```bash
/plugin list              # 列出已安裝
/plugin details <name>    # 詳細資訊
/plugin enable <name>     # 啟用
/plugin disable <name>    # 停用
/plugin uninstall <name>  # 解除安裝
```

## 不重新啟動就套用變更

```bash
/reload-plugins
```

重新載入所有 plugin 元件：
- Skills
- Agents
- Hooks
- MCP servers
- LSP servers

## 自動更新

預設 Claude Code 會定期檢查 marketplace 更新。

可手動觸發：

```bash
/plugin marketplace update
```

> 自動更新失敗時 plugin 保留現有版本（用 `CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE=1` 環境變數）

## 團隊配置與安全性

把 marketplace 加到 `.claude/settings.json` 讓團隊共享：

```json
{
  "extraKnownMarketplaces": {
    "company-tools": {
      "source": "github",
      "repo": "company/approved-plugins"
    }
  }
}
```

企業環境用 `strictKnownMarketplaces` 強制限制：

```json
{
  "strictKnownMarketplaces": [
    {"source": "github", "repo": "company/approved"}
  ]
}
```

## 重點回顧

- Marketplace = 商店，Plugin = 商品
- 官方 marketplace 自動註冊
- 6 種來源：GitHub、其他 Git、本機、URL 等
- 4 種範圍：User、Project、Local、Plugin
- `/reload-plugins` 不重啟套用變更
- `strictKnownMarketplaces` 強制安全管控
- 用 `/plugin` 介面互動管理

- 🎯 立刻：進 `/plugin` 看 Discover 標籤
- 📚 30 分鐘：裝 3 個實用 plugin（commit-commands、security-guidance、pyright-lsp）
- 🛠 2 小時：為專案加 marketplace 配置
- 🚀 一週：把團隊內部 plugin 上架到公司 marketplace
