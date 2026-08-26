# .md 改寫指南 — 從「內容文章」到「投影片大綱」

> 用途：把現有 .md 從「閱讀型長文」改寫成「投影片大綱」，
> 讓 learn2deck 能產出對齊舊版 .pptx 結構的視覺驗證版本。
>
> 對應 commit：`4e0585c`（Part B + C）
> 對應範例：`00-claude-code-plugins-series.md`（從 8 slides → 31 slides）

---

## 0. 目標

讓新版 .pptx 在 **slide 數** 和 **視覺風格** 上對齊舊版。

| 檔案 | 舊版 slides | 新版目標 slides |
|---|---|---|
| 00-overview | 30 | 31 (1 cover + 30) ✅ 已完成 |
| 01-marketplaces | 35 | ~36 |
| 02-plugins | 25 | ~26 |
| 03-reference | 45 | ~46 |
| 04-skills | 40 | ~41 |
| 05-subagents | 30 | ~31 |
| 06-hooks | 50 | ~51 |
| 07-discover | 22 | ~23 |

---

## 1. 從舊版 .py 腳本提取大綱

每份舊版 .pptx 都有對應的 `_make_XX.py` 腳本（例如 `_make_00_overview.py`）。這個腳本是**投影片藍圖**，告訴你：

- 每張 slide 的標題
- 每張 slide 的版型（cover / section / table / grid / etc.）
- 每張 slide 的內容（bullet / table / code）

### 步驟

```bash
# 1. 讀舊版腳本
cat /home/elan/pi-proj/_make_02_plugins.py | head -100
```

找出所有 `add_*_slide` 呼叫，例如：
- `h.add_cover_slide(prs, "Title", "Subtitle", tag="...")` → cover
- `h.add_section_divider(prs, "Part 1", "Title", "Subtitle")` → section_divider
- `h.add_two_column_compare(slide, "Left", [...], "Right", [...])` → two_column
- `h.add_comparison_table(slide, [...], [...])` → title_table
- `h.add_code_block(slide, code, ...)` → title_code
- `h.add_text_block(slide, text, x, y, w, h, font_size=14)` → title_content

---

## 2. 把每張 slide 轉成 .md 結構

### 2.1 Cover slide（自動插入）

**不需要手寫**。parser 自動從 H1 + blockquote 副標產生。

如果你要明確寫 cover：
```markdown
## Slide: Cover

這是 cover 內容
slide_type: cover
tag: 系列總覽 · #00
title: 自訂標題
subtitle: 自訂副標
```

### 2.2 Section divider

```markdown
## Part 1: 章節標題

章節副標（選用）
```

會自動推斷為 `section_divider`，body 含：
- `section_num`: "Part 1"
- `section_subtitle`: 章節副標（從第一段抽出）

### 2.3 Title + Content（預設）

```markdown
## 標題

副標（選用）

- bullet 1
- bullet 2
- bullet 3
```

### 2.4 Title + Table

```markdown
## 何時該用哪個元件？

| 需求 | 推薦元件 | 原因 |
| :--- | :--- | :--- |
| 每次 session 都要遵守的規則 | CLAUDE.md | 自動載入 |
| 重複使用的 SOP | Skill | 隨時叫用 |
```

### 2.5 Title + Code

```markdown
## 範例：建立 SKILL.md

`~/.claude/skills/summarize-changes/SKILL.md`：

```yaml
---
description: Reviews code...
---

When reviewing code, check for:
1. Code organization
2. Error handling
```
```

### 2.6 Grid Cards（H3 子節）

```markdown
## Claude Code 擴展元件：核心元件（上）

從基礎規則到進階自動化

### CLAUDE.md

專案說明書 · 每次 session 自動載入的規則

### Skills

可重用知識庫 · `/name` 觸發，隨叫隨到

### Subagents

隔離代理人 · 獨立 context 的子任務

### Hooks

事件自動化 · 確定性觸發的腳本
```

⚠️ **grid_cards 上限 ~6 個**。7+ 個會超出 7.0" 安全區。建議拆成「上」「下」兩張。

### 2.7 Two Column

```markdown
## 為什麼需要了解 Claude Code Plugin？

擴展 Claude 的能力

| 😐 預設 Claude Code | 🚀 使用 Plugin 後 |
| :--- | :--- |
| 通用對話能力 | 可重複使用的 Skills |
| 內建工具 | 隔離上下文的 Subagents |
```

⚠️ parser 用 `✅ / ❌` 偵測 pros/cons，但 markdown table 形式比較好維護。

### 2.8 Summary（下一步）

```markdown
## 下一步

- 想學寫 subagent → 閱讀 [05-subagents](./05-subagents.md)
- 想學事件自動化 → 閱讀 [06-hooks](./06-hooks.md)
```

會自動變成 `summary` slide。

---

## 3. 對應舊版的特殊內容

舊版有些**無法用現有 parser 表達**的設計：

| 舊版 | 改用 |
|---|---|
| 4 步驟流程圖（自訂橫向卡片）| 4 個 H3 grid_cards |
| 3 數據大卡片（72pt 數字）| 3 個 H3 grid_cards（小一點） |
| 6 元件網格（彩色）| 6 個 H3 grid_cards |
| 程式碼 + 註解混合 | title_content 的 bullet（如果 code 不重要）|

未來 builder 擴展支援的設計（v1.1+）：
- 多欄流程圖（custom flowchart builder）
- 大數字卡片（stat_card builder）
- 彩色網格元件（enhanced grid_cards with color attribute）

---

## 4. 改寫流程（以 02-plugins.md 為例）

### 步驟 1：讀舊版藍圖

```bash
cat /home/elan/pi-proj/_make_02_plugins.py | grep "add_section_divider\|add_cover_slide\|add_title_bar"
```

預期結果：
```
add_cover_slide(...)  # cover
add_section_divider(prs, "Part 1", ...)
add_section_divider(prs, "Part 2", ...)
... 大約 5 個 Part divider
... 約 20 個 content slide
```

### 步驟 2：列出每張 slide 對應

```
舊版 S1: cover → 自動
舊版 S2: 為什麼用 → two_column
舊版 S3: 規模 → 3 grid_cards
舊版 S4: Part 1 → section_divider
舊版 S5: 7 個元件 → grid_cards
舊版 S6: Part 2 → section_divider
... 依此類推
```

### 步驟 3：在 .md 內實作

按 §2 對應，把舊版內容寫成 .md 章節。記得：
- **Part X: 標題** → section_divider
- **## 標題 + bullet** → title_content
- **## 標題 + table** → title_table
- **## 標題 + H3** → grid_cards

### 步驟 4：驗證

```bash
/home/elan/pi-proj/.pptx-venv/bin/learn2deck build 02-plugins.md -o /tmp/test.pptx --validate
```

預期：`✨ No issues found!`

如果 R3 warning（超出安全區）：
- grid_cards 太多（>6）→ 拆成兩張
- bullet 太長 → 縮短
- code 太長 → 拆段

### 步驟 5：更新測試

```python
# tests/test_parsers.py
@pytest.mark.parametrize("filename,expected_min,expected_max", [
    ("00-claude-code-plugins-series.md", 25, 35),  # 30 slides
    ("01-plugin-marketplaces.md", 30, 40),         # 35 slides
    ("02-plugins.md", 20, 30),                     # 25 slides
    ...
])
```

---

## 5. 完成檢核清單

每份 .md 重整後：

- [ ] Slide 數對齊舊版（±1，因為多 cover）
- [ ] 版型分布合理（cover:1, section:N, table:N, grid:N, content:N）
- [ ] `learn2deck build` 通過（無 R1/R3 error）
- [ ] 視覺驗證（用 build_report_windows.py 開 HTML 報告比對）
- [ ] Markdown inline 不會洩漏到輸出（`**bold**` 應該變純文字）
- [ ] 7 個 grid_cards 拆成 4+3（避免 R3 overflow）

---

## 6. 後續 session 計畫

每份 .md 重整估計 1-2 小時：

| Session | 工作 | 預估時間 |
|---|---|---|
| 1（已完成）| 00-overview POC + builder bug | 2-3 小時 ✅ |
| 2 | 02-plugins（最簡單，25 slides）| 1-2 小時 |
| 3 | 04-skills（40 slides）| 2 小時 |
| 4 | 07-discover（22 slides，最簡單）| 1 小時 |
| 5 | 01-marketplaces（35 slides）| 1.5 小時 |
| 6 | 05-subagents（30 slides）| 1.5 小時 |
| 7 | 03-reference（45 slides）| 2 小時 |
| 8 | 06-hooks（50 slides，最大）| 2.5 小時 |

總計：~12-15 小時的 .md 重整工作。

---

## 7. 不重整 .md 的 trade-off

如果不想重整 .md，新版 .pptx 仍然能：
- ✅ 從 .md 自動產生 cover slide（自動插入）
- ✅ 套用一致的視覺風格（橘色裝飾條、字體、配色）
- ✅ 用 8 種版型呈現內容

但會缺少：
- ❌ Section divider（沒有「Part 1」「Part 2」等章節分隔頁）
- ❌ 精細的 slide 結構（每張 H2 = 1 slide，無法拆成更細）
- ❌ 舊版設計的視覺效果（流程圖、彩色卡片網格）

**建議**：對於最常被看的 00-overview 和 02-plugins 優先重整。其他可以慢慢做。
