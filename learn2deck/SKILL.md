---
name: learn2deck
description: 從 Markdown 教材與技術文件自動產生符合設計風格的 PPTX 簡報。Use this skill when the user asks to "產生簡報", "做成簡報", "做簡報", "做一份簡報", "做投影片", "做成投影片", "轉成投影片", "做 deck", "md 轉 pptx", "markdown 轉 pptx", "markdown 轉投影片", "make slides", "build a deck", "build deck", or when user expresses clear conversion intent combining markdown source with slide deck output (e.g. "從 markdown 產生 pptx", "把 .md 做成 pptx", "從 md 產生 pptx", "把 .md 轉成投影片", "幫我做 Plugin 簡報", "我要 8 份文件的簡報", "產生 Plugin 的 deck", "幫我做一份 Plugin 簡報"). Do NOT use for editing existing PPTX files, general presentation advice, or non-markdown content sources.
---

# learn2deck Skill

從 Markdown 自動產生符合設計風格的 PPTX 簡報。基於 learn2deck v1.0 純規則版 CLI（不呼叫 LLM）。

## 觸發條件

啟用此 skill 當使用者：

- 直接說「**產生簡報 / 做投影片 / build deck / make slides**」等明確指令
- 提供 .md 檔並提到「**簡報 / 投影片 / PPTX / deck / slides**」
- 提供 .md 檔並提到「**展示 / 分享 / 教學 / 培訓 / 演講**」
- 提到現有檔名 + 期望轉成 .pptx 輸出（例如「00-overview.md 做成 pptx」）

關鍵字觸發（高信心）：`產生簡報`, `做投影片`, `md 轉 pptx`, `markdown 投影片`, `make slides`, `build deck`, `pptx`

## 不要觸發

- ❌ 編輯、修改既有 .pptx（請用戶端工具如 PowerPoint 或 LibreOffice）
- ❌ 一般簡報建議、設計建議（不在本 skill 範圍）
- ❌ 把 Word / PDF / 純文字轉成 PPTX（非 markdown 來源）
- ❌ 「這份 markdown 很好」等純評論（無轉檔意圖）
- ❌ 從 PPTX 反推 Markdown 內容

## 執行流程

### 1. 識別輸入檔

- 使用者明確指定 → 用指定檔案
- 只有 1 個 .md 在當前目錄 → 用它
- 多個 .md → 列出候選並詢問（可批次處理）
- 找不到 .md → 詢問檔案路徑

### 2. 決定輸出位置

- 預設：`/tmp/new_<basename>.pptx`（`<basename>` 是去掉 `.md` 的檔名）
- 使用者指定 → 用指定路徑
- 批次模式 → 全部輸出到 `/tmp/new_*.pptx`

### 3. 執行 build

```bash
learn2deck build <input.md> -o <output.pptx> --validate
```

> **路徑提醒**：如果系統找不到 `learn2deck` 指令，使用 `python -m learn2deck build ...` 或確認套件已正確安裝（見 troubleshooting Q6）。

### 4. 檢查驗證結果

CLI `--validate` 旗標會跑 R1-R5 驗證規則（見 `references/validation-rules.md`）：

- **✨ No issues found** → 報告成功（slide 數 + 輸出路徑）
- **有 Issues** → 列出問題，問使用者：
  - 接受警告（warning）繼續
  - 修正錯誤（error）後重跑
  - 略過驗證（不加 `--validate`）

### 5. 報告結果

產出後必須回報：

- ✅/❌ 成功狀態
- 📊 slide 數量
- 📁 輸出檔案完整路徑
- 🔍 驗證結果（issues 數）
- ⚠️ 任何 warning 或 error

## 範例觸發與回應

### 範例 1 — 單檔明確觸發

> **使用者**：「幫我把 04-skills.md 做成簡報」

**執行**：
```bash
learn2deck build 04-skills.md -o /tmp/new_skills.pptx --validate
```

**回報**：
```
✅ 04-skills.md 簡報已產出
📊 30 slides
📁 /tmp/new_skills.pptx
🔍 0 errors, 0 warnings
```

### 範例 2 — 多檔批次觸發

> **使用者**：「我要 8 份文件的簡報」

**執行**：對 `00-07*.md` 全部 build

**回報**：列出 8 份檔案的產出狀態表

### 範例 3 — 意圖觸發（需確認）

> **使用者**：「想用這份 README 做個分享」

**回應**：先問「你要把 README 轉成 PPTX 簡報嗎？輸出到 `/tmp/new_README.pptx`？」

### 範例 4 — 排除（不觸發）

> **使用者**：「把這個 .pptx 改成橫式」

**回應**：「這需要編輯現有 PPTX，建議用 PowerPoint 或 LibreOffice 直接修改。本 skill 專門從 Markdown 產出新 PPTX，無法直接編輯。」

## 錯誤處理

| 情況 | 處理 |
|:-----|:-----|
| CLI 失敗（例外訊息） | 報告完整錯誤訊息，建議檢查 .md 格式（見 `references/troubleshooting.md`） |
| 驗證有 Issues | 列出具體 issue + 位置（slide # / shape name），問使用者是否接受 |
| .md 找不到 | 詢問檔案路徑，或建議 `ls *.md` 看現有檔案 |
| 指令找不到 | 提示使用 `python -m learn2deck ...` 或檢查 `pip show learn2deck` |
| 多檔但其中一個失敗 | 繼續處理其他檔案，最後彙整失敗清單 |

## 相關文件（references/）

- `references/style-guide.md` — Claude Orange 設計系統（顏色/字體/版面/安全區）
- `references/slide-types.md` — 9 種版型速查與 Markdown 對應規則
- `references/validation-rules.md` — R1-R5 驗證規則詳解
- `references/cli-reference.md` — 完整 CLI 指令與旗標
- `references/troubleshooting.md` — 常見錯誤與解決方案

## 範本（templates/）

- `templates/tutorial-outline.yaml` — 教學型簡報（分章節）
- `templates/reference-spec.yaml` — 技術規格型簡報（API/CLI 參考）
- `templates/quickstart.yaml` — 快速入門型簡報（5 步驟教學）

## 範例（examples/）

- `examples/minimal-plugin/` — Plugin 開發介紹範例（含 outline.yaml + content.md）

## 重要注意事項

- ⚡ **v1.0 純規則版**：本 skill 不呼叫任何 LLM，所有轉換由本地 CLI 完成
- 🎨 **預設主題**：claude-orange（與 Claude Code 設計風格一致）
- 📊 **已驗證**：可在多份 .md 上產生對齊設計風格的 PPTX 簡報
- 🚫 **不做**：編輯既有 PPTX、即時協作、雲端同步、動畫/影片
- 💡 **CLI 安裝**：`pip install learn2deck` 後即可使用 `learn2deck` 指令
