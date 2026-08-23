# 探索並安裝 Plugin（一般使用者指南）

> 📖 **系列**：Claude Code Plugin 完整學習系列 #07
> 🌐 **原文**：[code.claude.com/docs/zh-TW/discover-plugins](https://code.claude.com/docs/zh-TW/discover-plugins)
> 📅 **整理日期**：2026 / 01
> 🎯 **適用版本**：Claude Code v2.1.x

> 💡 **本系列總覽**：見 [00-claude-code-plugins-series.md](./00-claude-code-plugins-series.md)
> 📚 **上一篇**：[06-hooks.md](./06-hooks.md)（Hooks 自動化指南）
> 📚 **下一篇**：回到系列總覽

## 目錄

1. [Plugin 與 Marketplace 基本概念](#plugin-與-marketplace-基本概念)
2. [官方 Anthropic Marketplace](#官方-anthropic-marketplace)
3. [程式碼智慧 Plugin](#程式碼智慧-plugin)
4. [外部整合 Plugin](#外部整合-plugin)
5. [自動安全審查](#自動安全審查)
6. [開發工作流程 Plugin](#開發工作流程-plugin)
7. [輸出樣式 Plugin](#輸出樣式-plugin)
8. [社群 Marketplace](#社群-marketplace)
9. [使用 /plugin 介面](#使用-plugin-介面)
10. [新增 Marketplace 來源](#新增-marketplace-來源)
11. [安裝 Plugin](#安裝-plugin)
12. [管理已安裝的 Plugin](#管理已安裝的-plugin)
13. [安裝範圍](#安裝範圍)
14. [自動更新](#自動更新)
15. [配置團隊 Marketplace](#配置團隊-marketplace)
16. [安全性](#安全性)
17. [疑難排解](#疑難排解)

---

## Plugin 與 Marketplace 基本概念

**Plugin** 透過 skills、agents、hooks 和 MCP servers 擴展 Claude Code 的功能。

**Marketplace** 是別人建立和分享的 plugin 目錄，可以把它想成「應用程式商店」：

```
1. 新增商店（marketplace）→ 讓你存取整個目錄
2. 瀏覽並下載（install）→ 只選你要的 plugin
```

> 想要自己建立並發布 marketplace？請參考 [01-plugin-marketplaces.md](./01-plugin-marketplaces.md)。
> 想要自己寫 plugin？請參考 [02-plugins.md](./02-plugins.md)。

---

## 官方 Anthropic Marketplace

官方 Anthropic marketplace (`claude-plugins-official`) 在你啟動 Claude Code 時自動可用。

### 怎麼用

執行 `/plugin`，切換到 **Discover** 標籤瀏覽可用項目。

或從命令列安裝：

```bash
/plugin install github@claude-plugins-official
```

> ⚠️ 若 Claude Code 找不到 marketplace，執行：
> ```bash
> /plugin marketplace update claude-plugins-official
> # 或
> /plugin marketplace add anthropics/claude-plugins-official
> ```

### 官方 marketplace 包含什麼？

官方 marketplace 由 Anthropic 策劃，主要分為以下類別：

---

## 程式碼智慧 Plugin

**Code intelligence plugins** 啟用 Claude Code 的內建 LSP 工具，使 Claude 能跳轉到定義、尋找參考資料，並在編輯後立即看到型別錯誤。

這些 plugin 配置了 [Language Server Protocol](https://microsoft.github.io/language-server-protocol/) 連接 — 就是 VS Code 程式碼智慧背後的技術。

### 各語言的 Plugin 對照表

| 語言 | Plugin 名稱 | 需要的二進位檔 |
|:-----|:------------|:---------------|
| C/C++ | `clangd-lsp` | `clangd` |
| C# | `csharp-lsp` | `csharp-ls` |
| Go | `gopls-lsp` | `gopls` |
| Java | `jdtls-lsp` | `jdtls` |
| Kotlin | `kotlin-lsp` | `kotlin-language-server` |
| Lua | `lua-lsp` | `lua-language-server` |
| PHP | `php-lsp` | `intelephense` |
| Python | `pyright-lsp` | `pyright-langserver` |
| Rust | `rust-analyzer-lsp` | `rust-analyzer` |
| Swift | `swift-lsp` | `sourcekit-lsp` |
| TypeScript | `typescript-lsp` | `typescript-language-server` |

> ⚠️ **必須先安裝語言伺服器二進位檔**！Plugin 只是配置連接，不包含伺服器本體。
> 若看到 `Executable not found in $PATH`，請從上表安裝所需的二進位檔。

### Claude 從程式碼智慧 Plugin 獲得的功能

安裝 plugin 且語言伺服器可用後，Claude 獲得兩項強大能力：

1. **自動診斷** — 每次 Claude 編輯後，語言伺服器分析變更並自動回報錯誤和警告。Claude 看到型別錯誤、遺漏的匯入和語法問題，**無需執行編譯器或 linter**。若 Claude 引入錯誤，會在同一輪中修正問題。
2. **程式碼導航** — Claude 可以跳轉到定義、尋找參考、懸停取得型別資訊、列出符號、追蹤呼叫層次。

> 💡 看到「找到診斷」指示器時，按 **Ctrl+O** 內聯查看診斷。

---

## 外部整合 Plugin

這些 plugin 捆綁預先配置的 [MCP servers](./02-plugins.md#mcp-servers)，讓你連接 Claude 到外部服務，無需手動設定：

| 類別 | Plugin |
|:-----|:-------|
| **原始碼控制** | `github`、`gitlab` |
| **專案管理** | `atlassian`（Jira/Confluence）、`asana`、`linear`、`notion` |
| **設計** | `figma` |
| **基礎設施** | `vercel`、`firebase`、`supabase` |
| **通訊** | `slack` |
| **監控** | `sentry` |

---

## 自動安全審查

`security-guidance` plugin 會審查 Claude 的每項變更，檢查常見漏洞，並指示 Claude 在**同一工作階段中**修復發現的問題。

詳見 [security-guidance](https://code.claude.com/docs/zh-TW/security-guidance)。

---

## 開發工作流程 Plugin

為常見開發任務新增 skills 和 agents：

| Plugin | 用途 |
|:-------|:-----|
| `commit-commands` | Git 提交工作流程（commit、push、PR 建立） |
| `pr-review-toolkit` | 審查 pull request 的專門 agents |
| `agent-sdk-dev` | 使用 Claude Agent SDK 構建的工具 |
| `plugin-dev` | 建立 plugin 的工具組 |

---

## 輸出樣式 Plugin

自訂 Claude 的回應方式：

| Plugin | 用途 |
|:-------|:-----|
| `explanatory-output-style` | 對實作選擇提供教育性見解 |
| `learning-output-style` | 用於 skill 建立的互動式學習模式 |

---

## 社群 Marketplace

位於 [`anthropics/claude-plugins-community`](https://github.com/anthropics/claude-plugins-community) 的社群 marketplace 託管已通過 Anthropic 自動驗證和安全篩選的第三方 plugin。

每個 plugin 都固定到目錄中的特定 commit SHA。

### 新增社群 marketplace

```bash
/plugin marketplace add anthropics/claude-plugins-community
```

然後從中安裝：

```bash
/plugin install <plugin-name>@claude-community
```

> 想提交你的 plugin 到社群？請參考 [02-plugins.md 的「提交 plugin 到社群 marketplace」章節](./02-plugins.md#提交-plugin-到社群-marketplace)。

---

## 試試看：新增示範 Marketplace

Anthropic 也維護一個[示範 marketplace](https://github.com/anthropics/claude-code/tree/main/plugins)（`claude-code-plugins`），包含展示 plugin 系統可能性的範例 plugin。

```bash
/plugin marketplace add anthropics/claude-code
```

---

## 使用 /plugin 介面

執行 `/plugin` 開啟 plugin 管理器。介面有四個標籤，用 **Tab**（或 **Shift+Tab**）切換：

| 標籤 | 功能 |
|:-----|:-----|
| **Discover** | 從所有 marketplaces 瀏覽可用 plugin |
| **Installed** | 檢視和管理已安裝的 plugin |
| **Marketplaces** | 新增、移除或更新已新增的 marketplace |
| **Errors** | 檢視 plugin 載入錯誤

### 詳細資訊窗格

選擇 plugin 後會看到：

- **Context cost** 估計（v2.1.143+，每輪新增的 token 數）
- **Last updated** 日期（v2.1.144+）
- **Will install** 區段（v2.1.145+，列出 commands、agents、skills、hooks、MCP servers、LSP servers 讓你預覽）

### 與目錄相關的建議

當管理員透過 [`pluginSuggestionMarketplaces`](https://code.claude.com/docs/zh-TW/settings#available-settings) 受管設定將 marketplace 加入允許清單時，與你目前工作目錄相關的 plugin 會釘在頂部，並帶有 **suggested for this directory** 標籤。

---

## 新增 Marketplace 來源

使用 `/plugin marketplace add` 從不同來源新增 marketplace：

| 來源類型 | 範例 |
|:---------|:-----|
| **GitHub 簡寫** | `/plugin marketplace add anthropics/claude-code` |
| **Git URL（HTTPS）** | `/plugin marketplace add https://gitlab.com/company/plugins.git` |
| **Git URL（SSH）** | `/plugin marketplace add git@gitlab.com:company/plugins.git` |
| **本機路徑** | `/plugin marketplace add ./my-marketplace` |
| **本機 JSON 檔案** | `/plugin marketplace add ./path/to/marketplace.json` |
| **遠端 URL** | `/plugin marketplace add https://example.com/marketplace.json` |

> 💡 **快捷方式**：`/plugin market` 等同 `/plugin marketplace`，`rm` 等同 `remove`。

### 注意事項

- GitHub 簡寫用 `owner/repo` 格式（如 `anthropics/claude-code`）
- HTTPS URL **必須包含 `https://` 前綴**（v2.1.196+ 會拒絕無前綴的 URL）
- 加上 `.git` 後綴讓 Claude Code 複製整個儲存庫（而不是當作 `marketplace.json` 直接連結）
- 加上 `#ref` 固定到特定分支或標籤：
  ```bash
  /plugin marketplace add https://gitlab.com/company/plugins.git#v1.0.0
  ```

### URL-based vs Git-based Marketplace

基於 URL 的 marketplace（直接指向 `marketplace.json`）有個限制：**只下載那個 JSON 檔案本身**。如果你的 plugin 項目用相對路徑（如 `"./plugins/my-plugin"`），會找不到檔案。

**解決方案**：
- 改用 GitHub、npm、或 git URL 來源
- 或用 git-based marketplace（會複製整個 repo）

---

## 安裝 Plugin

新增 marketplace 後，可直接安裝 plugin：

```bash
/plugin install plugin-name@marketplace-name
```

這會打開 plugin 詳細資訊，讓你選擇**安裝範圍**。

### 從 Discover 標籤安裝

1. 執行 `/plugin`
2. 切到 **Discover** 標籤
3. 在 plugin 上按 **Enter**
4. 選擇範圍
5. 安裝

### 從命令列安裝

不開啟互動介面：

```bash
/plugin install commit-commands@claude-code-plugins
```

或用 CLI（預設為 user 範圍）：

```bash
claude plugin install formatter@your-org
```

---

## 安裝範圍

| 範圍 | 設定檔 | 使用案例 |
|:-----|:-------|:---------|
| **user** | `~/.claude/settings.json` | 個人 plugin，所有專案可用（預設） |
| **project** | `.claude/settings.json` | 團隊共享，透過版本控制 |
| **local** | `.claude/settings.local.json` | 專案特定，不共享（gitignored） |
| **managed** | 受管設定 | 管理員部署，唯讀 |

> 你可能會看到 **managed** 範圍的 plugin — 這些是管理員透過[受管設定](https://code.claude.com/docs/zh-TW/settings#settings-files)安裝的，無法修改。

---

## 管理已安裝的 Plugin

### 互動式介面

執行 `/plugin` 並切到 **Installed** 標籤：
- 按 `f` 加入/取消最愛
- 輸入文字篩選（按名稱或描述）
- 按 Enter 開啟詳細檢視，啟用、停用或解除安裝

清單排序：載入錯誤 → 未解決依賴 → 最愛 → 停用 plugin（摺疊在底部）。

### CLI 指令

```bash
# 列出已安裝 plugin
/plugin list
# 或過濾
/plugin list --enabled
/plugin list --disabled

# 停用（不移除）
/plugin disable plugin-name@marketplace-name

# 重新啟用
/plugin enable plugin-name@marketplace-name

# 完全移除
/plugin uninstall plugin-name@marketplace-name

# 針對特定範圍操作
claude plugin install formatter@your-org --scope project
claude plugin uninstall formatter@your-org --scope project
```

### 解除安裝時的範圍處理

解除 `.claude/settings.json` 啟用的 plugin 時，會問你想：
- 只為自己停用（寫到 `.claude/settings.local.json`，保留專案安裝）
- 為所有人解除安裝（從 `.claude/settings.json` 移除）

> 需要 Claude Code v2.1.203+。在此版本前只有「本地停用」選項。

### 「最近未使用」功能

**Installed** 標籤會收集你安裝但**至少兩週未使用**且跨**至少 10 個工作階段**的 marketplace plugin，列在 **Not used recently** 標題下。詳情檢視會顯示每個 plugin 的 **Last used** 行。

> 💡 用這功能找出不再使用但仍在增加啟動和 context 成本的 plugin，停用或解除安裝它們。
> 需要 v2.1.187+。

**永遠不會列為未使用的 plugin**：
- 組織管理的 plugin 或用 `--plugin-dir` 載入的
- 提供 theme、output style、monitor 或 workflow 的（這些提供無需叫用的價值）

> 當組織使用 [`strictKnownMarketplaces`](https://code.claude.com/docs/zh-TW/settings#strictknownmarketplaces) 時，這個功能會隱藏。

---

## 在不重新啟動的情況下套用 Plugin 變更

工作階段期間安裝、啟用或停用 plugin 時，執行：

```bash
/reload-plugins
```

這會重新載入所有 plugin，顯示 plugin、skills、agents、hooks、plugin MCP servers 和 plugin LSP servers 的計數。

> ⚠️ `/reload-plugins` 會在下個請求產生 token 成本（新元件會在對話中宣告自己）。提供 MCP servers 的 plugin 若其工具未被 [tool search](https://code.claude.com/docs/zh-TW/mcp#scale-with-mcp-tool-search) 延遲，會使快取失效，這時 `/reload-plugins` 會顯示警告且**不套用**重新載入。傳遞 `--force` 強制套用。

---

## 自動更新

Claude Code 可在啟動後**自動在背景**更新 marketplace 和已安裝的 plugin。

### 啟用後的行為

- 工作階段開始後檢查更新，隨機延遲最多 10 分鐘
- 執行中的工作階段仍使用啟動時載入的版本
- 若任何 plugin 已更新，會提示你執行 `/reload-plugins`，或新版本下次啟動時載入

### 為個別 marketplace 切換自動更新

1. 執行 `/plugin`
2. 選擇 **Marketplaces**
3. 從清單選擇 marketplace
4. 選擇 **Enable auto-update** 或 **Disable auto-update**

**預設行為**：
- 官方 Anthropic marketplace：預設**啟用**
- 第三方和本機開發 marketplace：預設**停用**

### 環境變數

```bash
# 完全停用所有自動更新
export DISABLE_AUTOUPDATER=1

# Claude Code 不自動更新，但 plugin 仍自動更新
export DISABLE_AUTOUPDATER=1
export FORCE_AUTOUPDATE_PLUGINS=1
```

---

## 配置團隊 Marketplace

團隊管理員可在 `.claude/settings.json` 配置自動 marketplace 安裝。當團隊成員信任 repo 資料夾時，會提示他們安裝。

```json
{
  "extraKnownMarketplaces": {
    "my-team-tools": {
      "source": {
        "source": "github",
        "repo": "your-org/claude-plugins"
      }
    }
  }
}
```

完整配置（含 `extraKnownMarketplaces` 和 `enabledPlugins`）見 [Plugin 設定](https://code.claude.com/docs/zh-TW/settings#plugin-settings)。

> 📌 自 v2.1.195+：此安裝步驟適用於載入 plugin 的每個路徑。專案 `.claude/settings.json` 啟用但來自外部來源（GitHub、npm）的 plugin，在團隊成員安裝前不會載入。在此之前，Claude Code 會報告 plugin 未安裝並顯示要執行的 `claude plugin install` 命令。

---

## 安全性

⚠️ **Plugin 和 marketplace 是高度受信任的元件**，可使用你的使用者權限在機器上執行任意程式碼。

**最佳實踐**：
- 僅從你信任的來源安裝 plugin 和新增 marketplace
- 檢查每個 plugin 的首頁了解更多
- 組織可使用[受管 marketplace 限制](./01-plugin-marketplaces.md#受管-marketplace-限制)限制使用者能新增的 marketplace
- 注意 plugin 中包含的 MCP servers、檔案或其他軟體 — Anthropic 無法控制也無法驗證它們是否按預期運作

---

## 疑難排解

### `/plugin` 命令無法識別

若看到「未知命令」：

1. **檢查版本**：`claude --version`
2. **更新 Claude Code**：
   ```bash
   # Homebrew
   brew upgrade claude-code

   # npm
   npm install -g @anthropic-ai/claude-code@latest

   # 原生安裝程式
   # 從 setup 頁面重跑安裝命令
   ```
3. **重新啟動 Claude Code**

### 常見問題

| 問題 | 解決方案 |
|:-----|:---------|
| Marketplace 未載入 | 驗證 URL 可存取 + `.claude-plugin/marketplace.json` 存在 |
| Plugin 安裝失敗 | 檢查 plugin 來源 URL 可存取 + repo 公開或有權限 |
| 安裝後找不到檔案 | Plugin 被複製到快取，引用 plugin 目錄外的路徑會失效 |
| Plugin skills 未出現 | `rm -rf ~/.claude/plugins/cache`、重啟、重裝 |

### 程式碼智慧問題

| 問題 | 解決方案 |
|:-----|:---------|
| 語言伺服器未啟動 | 驗證二進位檔已安裝且在 `$PATH` 中 |
| 高記憶體使用 | `rust-analyzer` 和 `pyright` 在大專案會吃大量記憶體。可用 `/plugin disable` 停用，改用 Claude 內建搜尋 |
| Monorepos 誤報診斷 | 內部套件的未解決匯入錯誤通常不影響 Claude 編輯能力 |

---

## 速查表

| 動作 | 指令 |
|:-----|:-----|
| 開啟 plugin 管理器 | `/plugin` |
| 從 GitHub 新增 marketplace | `/plugin marketplace add owner/repo` |
| 從 git URL 新增 | `/plugin marketplace add https://gitlab.com/.../plugins.git` |
| 從本機路徑新增 | `/plugin marketplace add ./my-marketplace` |
| 列出 marketplaces | `/plugin marketplace list` |
| 更新 marketplace | `/plugin marketplace update <name>` |
| 移除 marketplace | `/plugin marketplace remove <name>` |
| 安裝 plugin | `/plugin install <plugin>@<marketplace>` |
| 列出已安裝 plugin | `/plugin list` |
| 停用 plugin | `/plugin disable <plugin>@<marketplace>` |
| 啟用 plugin | `/plugin enable <plugin>@<marketplace>` |
| 解除安裝 | `/plugin uninstall <plugin>@<marketplace>` |
| 重新載入所有 plugin | `/reload-plugins` |

---

## 開始你的第一個 Plugin 探索之旅

1. **執行 `/plugin`** → 切到 Discover 標籤
2. **挑一個小工具試試** → 建議先裝 `commit-commands`（實用、風險低）
3. **重啟 Claude Code**（或執行 `/reload-plugins`）
4. **試用 skill**：例如 `/commit-commands:commit`

裝完後，你會對 plugin 是什麼、有什麼能力有更具體的感受。

接下來，建議閱讀 [02-plugins.md](./02-plugins.md) 學習如何從零建立自己的 plugin！
