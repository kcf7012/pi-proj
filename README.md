# Claude Code Plugin 完整學習系列

> 系統化的 Claude Code 擴展開發教材，由官方文件整理而成。

## 📚 內容總覽

本系列提供 **兩種學習格式**：

| 格式 | 檔案 | 用途 |
|:-----|:-----|:-----|
| **Markdown 教材** | `*.md`（8 份） | 詳細閱讀、查詢、原始參考 |
| **PPTX 簡報** | `*.pptx`（4 份） | 自學複習、團隊分享、快速理解 |

## 📂 檔案清單

### Markdown 教材

| 編號 | 檔案 | 主題 | 適合對象 |
|:----:|:-----|:-----|:---------|
| 00 | `00-claude-code-plugins-series.md` | 系列總覽 | 所有人 |
| 01 | `01-plugin-marketplaces.md` | Plugin Marketplaces | 想分享 plugin 的人 |
| 02 | `02-plugins.md` | Plugin 開發入門 | plugin 開發新手 |
| 03 | `03-plugins-reference.md` | Plugin 技術參考 | 進階開發者 |
| 04 | `04-skills.md` | Skills 完整指南 | 想自訂 Claude 行為的人 |
| 05 | `05-subagents.md` | Subagents 自訂指南 | 想做進階自動化的人 |
| 06 | `06-hooks.md` | Hooks 自動化指南 | 想做確定性自動化的人 |
| 07 | `07-discover-plugins.md` | 探索並安裝 Plugins | 一般使用者 |

### PPTX 簡報

| 編號 | 檔案 | 投影片數 | 對應 |
|:----:|:-----|:--------:|:----|
| 00 | `00-overview.pptx` | 30 張 | 系列總覽 |
| 02 | `02-plugins.pptx` | 25 張 | Plugin 開發 |
| 04 | `04-skills.pptx` | 40 張 | Skills 完整指南 |
| 06 | `06-hooks.pptx` | 50 張 | Hooks 自動化 |

> 簡報與對應的 .md 檔案結構一致，方便交叉對照。

## 🎯 學習路徑

### 🟢 新手入門（1-2 天）
1. 閱讀 `00-overview.pptx` 了解全貌
2. 閱讀 `04-skills.md` 學會寫第一個 skill
3. 閱讀 `02-plugins.md` 把 skill 包成 plugin

### 🟡 進階使用者（3-5 天）
1. 閱讀 `05-subagents.md`
2. 閱讀 `06-hooks.md`
3. 閱讀 `01-plugin-marketplaces.md`

### 🔴 專家 / 團隊負責人（1 週+）
1. 深入閱讀 `03-plugins-reference.md`
2. 建立團隊/企業 marketplace
3. 整合所有元件建立複雜 plugin

## 🛠️ 工具與建置

### 環境需求

- Python 3.11+
- `uv`（用於管理 Python 環境）
- PowerPoint 或相容軟體（開啟 .pptx）

### 重新產生簡報

```bash
# 建立環境
uv venv .pptx-venv --python 3.11
uv pip install --python .pptx-venv/bin/python python-pptx

# 產生所有簡報
.pptx-venv/bin/python _make_00_overview.py
.pptx-venv/bin/python _make_02_plugins.py
.pptx-venv/bin/python _make_04_skills.py
.pptx-venv/bin/python _make_06_hooks.py
```

### 修改與自訂

- 改顏色：編輯 `_pptx_helpers.py` 頂部的 `COLOR_*` 變數
- 改內容：編輯對應的 `_make_XX_*.py` 後重新執行

## 📖 內容來源

所有內容整理自 [Claude Code 官方文件](https://code.claude.com/docs/zh-TW/)（繁體中文版與英文版混合）。

涵蓋 Claude Code **v2.1.x**（到 v2.1.236）。

## 📜 授權

整理自官方文件，繁體中文教學用途。引用建議註明「整理自 Claude Code 官方文件」。

## 🔄 變更紀錄

| 日期 | 版本 | 說明 |
|:-----|:-----|:-----|
| 2026/01 | 1.0 | 初版發布 |

---

**整理人**：elan
**整理日期**：2026/01
