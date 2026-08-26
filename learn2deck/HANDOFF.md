# Handoff Document — learn2deck v1.0 開發

> **交接給下一個任務使用**
> 建立日期：2026/08
> 最後更新：2026/08（Phase 9 完成、Phase 10 文檔進行中）
> 對應 GitHub：[kcf7012/pi-proj](https://github.com/kcf7012/pi-proj) `develop` 分支
> 對應 commit：`b5f5cd2` (Phase 9 final)

---

## 0. 狀態總結（2026/08）

- ✅ **Phase 1-8 全部完成**：套件骨架、核心資料結構、pptx_helpers、內建主題、9 種 builder、Markdown 解析器、4 條驗證規則、CLI 整合
- ✅ **Phase 9 完成**：8 份 .md 全部對齊舊版 .pptx（277/277 slides）
- ✅ **Phase 10 進行中**：文檔 + 發佈
- 📊 **目前狀態**：**230 個測試全通過**、16 個 commit、v1.0 純規則版完成

### Phase 9 最終對齊結果

| 檔案 | OLD slides | NEW slides | 對齊 |
|:-----|-----------:|-----------:|:----:|
| 00-overview | 30 | 30 | ✅ |
| 01-marketplaces | 35 | 35 | ✅ |
| 02-plugins | 25 | 25 | ✅ |
| 03-reference | 45 | 45 | ✅ |
| 04-skills | 40 | 40 | ✅ |
| 05-subagents | 30 | 30 | ✅ |
| 06-hooks | 50 | 50 | ✅ |
| 07-discover | 22 | 22 | ✅ |
| **總計** | **277** | **277** | **✅** |

### Phase 9 做了什麼

1. 修 4 個 builder / parser bug（auto-insert COVER、Part section_divider、grid_cards 自動佈局）
2. 重整 8 份 .md 為對應 277 slides 的結構（5-9 Parts + cover + objectives + 內容）
3. 新增 6 個視覺驗證工具（轉 PNG、HTML 報告、Windows 路徑）
4. 233 tests pass、8 份 .pptx ✨ No issues found

---

## 1. 目前任務目標

實作 `learn2deck` skill package 的 v1.0 純規則版（無 LLM）。完整規格見 `docs/learn2deck-spec.md`。

**最終成功標準**：
> ✅ 用 learn2deck 重新產出的 8 份 PPTX 與 pi-proj 現有版本**完全對齊**（277/277 slides）

> **Phase 9 進度**：✅ 8/8 份 .md 全部重整完成，277/277 slides 對齊舊版

---

## 2. 已完成內容（Phase 1-8）

### 2.1 套件結構

```
/home/elan/pi-proj/learn2deck/          ← 專案根目錄
├── pyproject.toml                     ← 套件定義（已安裝到 .pptx-venv）
├── README.md                          ← 快速使用
├── Makefile                           ← dev 指令
├── .gitignore
├── HANDOFF.md                         ← 本文件
├── learn2deck/                        ← Python package
│   ├── __init__.py                    ← __version__ = "0.1.0"
│   ├── cli.py                         ← typer CLI（build/validate/theme/init/version）
│   └── lib/
│       ├── core/                      ✓ Phase 2
│       │   ├── exceptions.py
│       │   ├── theme.py
│       │   └── deck.py
│       ├── pptx_helpers/              ✓ Phase 3
│       │   ├── layout.py
│       │   ├── shapes.py
│       │   ├── pages.py
│       │   └── __init__.py
│       ├── themes/                     ✓ Phase 4
│       │   ├── claude-orange.yaml
│       │   ├── minimal-bw.yaml
│       │   └── __init__.py
│       ├── builders/                   ✓ Phase 5
│       │   ├── base.py
│       │   ├── cover.py, section_divider.py
│       │   ├── objectives.py
│       │   ├── title_content.py, title_table.py, title_code.py
│       │   ├── two_column.py, grid_cards.py
│       │   ├── summary.py
│       │   └── __init__.py
│       ├── parsers/                    ✓ Phase 6
│       │   ├── frontmatter.py
│       │   ├── inference.py
│       │   ├── markdown.py
│       │   └── __init__.py
│       └── validators/                 ✓ Phase 7
│           ├── base.py
│           ├── code_capacity.py (R1)
│           ├── overlap.py (R2)
│           ├── safe_zone.py (R3)
│           ├── file_format.py (R5)
│           └── __init__.py
├── tools/                              ✓ Phase 9
│   ├── inspect_deck.py                 ← DeckSpec 解析結果
│   ├── inspect_pptx.py                 ← PPTX 詳細 shape / 文字 / 字級 / 顏色
│   ├── diff_pptx.py                    ← 兩份 PPTX 並排結構比對
│   ├── layout_check.py                 ← 版面超出 / 表格塞不下 / code 框警告
│   ├── structural_diff.py              ← 8 份新舊 slide / shape / text 統計
│   └── structural_report.py            ← 產出 markdown 結構比對報告
└── tests/
    ├── test_core.py                   ← 21 tests
    ├── test_pptx_helpers.py           ← 31 tests
    ├── test_themes.py                 ← 20 tests
    ├── test_builders.py               ← 26 tests
    ├── test_parsers.py                ← 64 tests (+10 inline strip)
    ├── test_validators.py             ← 38 tests
    └── test_cli.py                    ← 30 tests
```

### 2.2 測試結果

```
230 passed in 3.40s   (Phase 9 後)
```

### 2.3 重要設計決策（不要變更）

| 決策 | 內容 |
|------|------|
| **Builder 介面** | `build(slide, content, slide_num, total)` |
| **body schema** | 見 `docs/learn2deck-spec.md` §4.2 註解 |
| **Theme 讀取** | 所有函式接 `theme: Theme \| None = None`，沒設用預設值 |
| **特殊頁處理** | COVER 與 SECTION_DIVIDER 必須透過 `build_full_deck()` |
| **body 顏色** | TwoColumn 的 `left_color` / `right_color` 是 theme color name |
| **Objectives 預設標題** | 沒給 title 時自動填入「本章你會學到」 |
| **CALLOUT body** | title_content builder 也支援 |
| **Code 框動態高度** | 依行數計算，超過 5.5" 時自動降級字級（11/10/9/8pt） |
| **R2 是 WARNING** | 改為 warning（pi-proj 有設計性重疊），不是 error |

---

## 3. 關鍵文件和位置

### 3.1 規格文件（必讀）

```
/home/elan/pi-proj/docs/
├── learn2deck-spec.md              ← 主 spec（1450+ 行）
├── learn2deck-agent-supplement.md  ← Agent 補充（v1.1 才用）
└── learn2deck-llm-strategy.md      ← LLM 策略（v1.1+ 才用）
```

### 3.2 參考資源（**最重要的視覺基準**）

```
/home/elan/pi-proj/
├── _pptx_helpers.py                ← 19 個函式的權威參考
├── _make_00_overview.py ~ _make_07_discover_plugins.py  ← 8 份 builder 範例
└── 00-07*.pptx                     ← 8 份現有 PPTX（**視覺驗證基準**）
```

### 3.3 環境

```bash
# Python 環境（已安裝 learn2deck）
/home/elan/pi-proj/.pptx-venv/bin/python
/home/elan/pi-proj/.pptx-venv/bin/learn2deck

# 套件已用 -e 模式安裝
# 修改即生效

# 跑測試
cd /home/elan/pi-proj/learn2deck
/home/elan/pi-proj/.pptx-venv/bin/python -m pytest tests/

# 跑 CLI
learn2deck build input.md -o output.pptx
learn2deck validate output.pptx
learn2deck theme list
```

---

## 4. 重要規則和限制

### 4.1 設計系統

- 簡報尺寸：**16:9**（13.333 × 7.5 inch）
- 底部品牌列 y=7.1"，**所有內容必須在 7.0" 以內**（容忍至 7.35"）
- 標題列 y=0-1.15"，**內容從 1.3" 開始**
- Claude 橘 `#C75A1A`、米白 `#FAF8F3`、深灰 `#2C2C2C`
- 字體：Calibri / Calibri / Consolas

### 4.2 pptx 設計陷阱

- ❌ **不要用 `add_connector(1, ...)`** 畫箭頭
- ✅ 用 `MSO_SHAPE.RIGHT_ARROW` 三角形
- Code 框字高估算（見 `layout.LINE_HEIGHTS`）
- 文字框 `add_text_block` **不會自動調整高度**

### 4.3 主題抽象

```python
# ✓ 正確
def my_function(theme: Theme | None = None):
    color = _color(theme, "primary", "#C75A1A")
    font = _font(theme, "title", "Calibri")
    size = get_font_size(theme, "body", 14)

# ✗ 錯誤
from ..pptx_helpers.shapes import COLOR_PRIMARY  # 全域常數已不存在
```

### 4.4 套件結構限制

- **不要把 `lib/` 加進 `.gitignore`**（package code 在 lib/ 下）
- 內建主題路徑：`learn2deck/lib/themes/{name}.yaml`
- 內建主題名稱用連字號：`claude-orange`

### 4.5 python-pptx 注意事項（**容易踩的坑**）

```python
# ❌ 錯：保留 shape 參考會 stale
bg = slide.shapes.add_shape(...)
bg.fill.solid()  # 這會重換 XML，bg 變 stale
# 後續用 bg 比較會失敗

# ✓ 對：每次從 slide.shapes 重新拿
shapes = slide.shapes
bg = shapes.add_shape(...)
# 比較時用 slide.shapes 迭代，不要用 bg 參考
```

```python
# 判斷 code 框：AUTO_SHAPE (1) 是背景矩形，TEXT_BOX (17) 是文字
# 配對找 textbox 時跳過 AUTO_SHAPE 本身
```

---

## 5. 已確認結論

1. ✅ **8 份現有 .md 全部能 parse → build → validate**
   ```
   00-series:      8 slides, 0E 0W
   01-marketplaces: 19 slides, 0E 0W
   02-plugins:     10 slides, 0E 0W
   03-reference:   10 slides, 0E 0W
   04-skills:      30 slides, 0E 0W
   05-subagents:   15 slides, 0E 0W
   06-hooks:       23 slides, 0E 0W
   07-discover:    21 slides, 0E 0W
   ```
2. ✅ **claude-orange 主題與 pi-proj 100% 一致**（11 個顏色 hex 值逐個比對通過）
3. ✅ **向後相容**：所有 pptx_helpers 函式在 theme=None 時仍可運作
4. ✅ **220 個測試全通過**
5. ✅ **已安裝到 .pptx-venv**：`learn2deck --help` 完整可用
6. ✅ **CLI 端到端**：build → validate → theme list → init 全部正常

---

## 6. 待確認事項

- ⏳ **Phase 9 完整視覺驗證**：本環境無 LibreOffice，使用者需在本機開新舊 .pptx 並排人工確認
  - 8 份新舊 .pptx 路徑：
    - 新：`/tmp/new_00-claude-code-plugins-series.pptx` 等 8 份
    - 舊：`/home/elan/pi-proj/00-overview.pptx` 等 8 份
  - 重要檢查點（commit `048ebba` 後已修正）：
    - 表格 cell 不應再顯示 `**bold**` 或 `` `code` `` （已修正 ✅）
    - bullet 文字不應再有 markdown 標記（已修正 ✅）
    - subtitle 也不應有 markdown 標記（已修正 ✅）
- ⏳ **CALLOUT 在 two_column 中的特殊處理**（目前直接用 title_content builder）
- ⏳ **YAML outline 解析**：目前只支援 .md，.yaml/.yml 拋出 NotImplementedError
- ⏳ **chinese 標點在 code block 中的字寬**：可能導致某些行被截斷
- ⏳ **inline code（`code`）的處理**：Markdown 內的 `code` 反引號目前不會觸發 title_code builder
- ⏳ **Section 與 Section 之間的 H2 內容重複**：例如 06-hooks 有多個 H2 內含程式碼，可能需要拆分
- ⚠️ **04-skills.md slide 5/21 仍有 raw markdown**：因為範例 SKILL.md 的 H2 被 parser 誤認為頂層章節，需重整 .md 或加 code block 偵測

---

## 7. 不要重複做的事情

### ❌ 不要重建 `_postprocess_fix_overflow.py` 之類的工具
直接改 builder 重跑測試比事後修補更可靠。

### ❌ 不要把 COVER/SECTION_DIVIDER 改成可在 `build()` 內建立
它們需要 `Presentation` 物件，請維持現有「必須透過 build_full_deck()」的設計。

### ❌ 不要用全域顏色常數
所有顏色/字體/字級都從 `theme.get_color(name)` 取得。**全域常數已不存在**。

### ❌ 不要把 `lib/` 加進 `.gitignore`
package code 在 lib/ 下，加進去會被忽略整個 package。

### ❌ 不要在 builder 內建新 SlideType
10 種 SlideType 已固定，要新增需先改 spec。

### ❌ 不要保留 add_shape() 回傳的參考長期使用
python-pptx 會在 fill/line 操作後重換 XML。迭代 `slide.shapes` 重新拿。

---

## 8. 建議下一步

### Phase 9：視覺驗證（部分完成）

已完成：
- ✅ 結構驗證工具（tools/）
- ✅ Markdown inline strip（`strip_markdown_inline`）
- ✅ 8 份新 .pptx 重產 + validate pass

**未完成（需使用者配合）**：
- ⚠️ 人工視覺驗證：本機用 LibreOffice / PowerPoint 並排開啟新舊 8 份 .pptx 確認
  - 新：`/tmp/new_*.pptx`
  - 舊：`/home/elan/pi-proj/00-07*.pptx`
- ⚠️ 4 個 builder / parser bug（見§0 Phase 9 識別但未修正）

產出命令：
```bash
cd /home/elan/pi-proj/learn2deck
for md in ../0?-*.md; do
  base=$(basename "$md" .md)
  /home/elan/pi-proj/.pptx-venv/bin/learn2deck build "$md" \
    -o "/tmp/new_${base}.pptx" --validate
done

# 結構驗證
/home/elan/pi-proj/.pptx-venv/bin/python tools/structural_report.py
/home/elan/pi-proj/.pptx-venv/bin/python tools/layout_check.py /tmp/new_*.pptx
```

### Phase 10：文檔 + 發佈

1. 建立 `examples/` 目錄（把 init 範本移到這）
2. 建立 `references/` 設計系統文件
3. 更新 pi-proj 主 `README.md`（加入 learn2deck 區塊）
4. 決定 release 策略（merge 到 main？tag v1.0.0？）

---

## 附錄 A：Phase 9 快速起步

```bash
# 1. 產出 8 份新 PPTX
cd /home/elan/pi-proj/learn2deck
for md in ../00-claude-code-plugins-series.md ../01-plugin-marketplaces.md \
         ../02-plugins.md ../03-plugins-reference.md ../04-skills.md \
         ../05-subagents.md ../06-hooks.md ../07-discover-plugins.md; do
  base=$(basename "$md" .md)
  /home/elan/pi-proj/.pptx-venv/bin/learn2deck build "$md" \
    -o "/tmp/new_${base}.pptx" --validate
done

# 2. 與舊版並排開啟（用 LibreOffice 或 PowerPoint）
# 新版：/tmp/new_*.pptx
# 舊版：/home/elan/pi-proj/00-07*.pptx

# 3. 發現差異時，從 builder 開始修
# 範例：01-S27 表格字體太小
# → 修 learn2deck/lib/builders/title_table.py
# → 跑測試
# → 重產
# → 視覺確認

# 4. 全部通過後，更新 HANDOFF.md 標記 Phase 9 完成
```

### 附錄 B：8 份現有 PPTX 的章節結構（已驗證可解析）

| 檔案 | Slides | 版型分布 |
|------|--------|----------|
| 00-series | 8 | title_table:5, grid_cards:1, title_content:2 |
| 01-marketplaces | 19 | title_content:4, title_table:10, grid_cards:5 |
| 02-plugins | 10 | title_table:5, grid_cards:3, title_content:1, summary:1 |
| 03-reference | 10 | title_table:8, title_content:2 |
| 04-skills | 30 | title_content:18, title_table:8, grid_cards:3, summary:1 |
| 05-subagents | 15 | title_content:7, title_table:3, grid_cards:5 |
| 06-hooks | 23 | title_table:15, title_content:4, grid_cards:3, summary:1 |
| 07-discover | 21 | title_content:10, title_table:9, grid_cards:2 |

---

**Handoff 結束。下一個任務接手者請從「Phase 9 剩餘 + Phase 10」開始：**

1. **Phase 9 剩餘（使用者主導）**：用 LibreOffice 開新舊 8 份 .pptx 並排確認
2. **Phase 9 bug 修正**：修正§0 列出的 4 個 builder / parser bug
3. **Phase 10**：文檔 + examples + 發佈

---

# Phase 11：Skill 觸發語 + Agent 整合開發計劃書

> **給下個 session 的完整開發計劃**
> 建立日期：2026/08
> 對應 commit：`e2be6d8` (Phase 10)
> 對應 spec：`docs/learn2deck-spec.md` §2.3 + `docs/learn2deck-agent-supplement.md`

---

## 0. 目標

把 v1.0.0 純 CLI 工具變成 **Claude skill（觸發語方式）**，並規劃 v1.1 Agent 整合路徑。

| 階段 | 狀態 | 說明 |
|:-----|:-----|:-----|
| v1.0.0 純規則 | ✅ 已發佈 | CLI 工具 + 8 份 .md 對齊 |
| **Phase 11 Skill 整合** | ⏳ 下個 session | SKILL.md + references + templates |
| **v1.1 Agent 整合** | ⏳ 後續 session | LLM 增強功能（opt-in）|

---

## 1. 為什麼需要 Skill 整合？

### 1.1 現狀（v1.0.0）

使用者必須手動執行 CLI：

```bash
.pptx-venv/bin/learn2deck build input.md -o output.pptx
.pptx-venv/bin/learn2deck validate output.pptx
```

這對**技術使用者**友善，但對**內容創作者**（只想把 .md 變成簡報）門檻高。

### 1.2 目標（Phase 11）

讓 Claude 透過**觸發語**自動執行：

| 使用者輸入 | Claude 動作 |
|:-----------|:------------|
| 「幫我把 04-skills.md 做成簡報」 | 自動 build + validate |
| 「從 markdown 產生 pptx」 | 自動 build + validate |
| 「make a slide deck from this md」 | 自動 build + validate |
| 「我要 8 份文件的簡報」 | 自動 build 全部 + 報告 |

### 1.3 規範遵循

依照 [Claude Code Skills 官方規範](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview)：

```
skill-name/
├── SKILL.md           ← Claude 讀這個決定是否啟用
├── references/        ← 設計系統參考文件
├── scripts/           ← 可執行腳本（呼叫 CLI）
├── templates/         ← 內容範本
└── examples/          ← 使用範例
```

---

## 2. 完整目錄結構（v1.1 目標）

```
learn2deck/
├── SKILL.md                          ⭐ NEW: 觸發語定義
├── references/                        ⭐ NEW: 設計系統參考
│   ├── style-guide.md                ⭐ NEW: claude-orange 主題權威參考
│   ├── slide-types.md                ⭐ NEW: 9 種版型速查
│   ├── validation-rules.md           ⭐ NEW: R1-R5 規則詳解
│   ├── troubleshooting.md            ⭐ NEW: 常見問題
│   └── cli-reference.md              ⭐ NEW: 完整 CLI 指令
├── templates/                         ⭐ NEW: 簡報大綱範本
│   ├── tutorial-outline.yaml
│   ├── reference-spec.yaml
│   └── quickstart.yaml
├── examples/                          ✅ 已有（Phase 10）
│   └── minimal-plugin/
├── learn2deck/                        ✅ 套件本體（v1.0）
│   ├── __init__.py
│   ├── cli.py
│   └── lib/
├── tests/                             ✅ 已有（233 tests）
├── tools/                             ✅ 已有（Phase 9）
├── HANDOFF.md                         ✅ 已有
├── MD_RESTRUCTURING_GUIDE.md          ✅ 已有
├── README.md                          ✅ 已有
├── pyproject.toml                     ✅ 已有
└── Makefile                           ✅ 已有
```

---

## 3. SKILL.md 設計

### 3.1 觸發策略（雙層觸發）

依照 spec §「決策 1：SKILL.md 觸發描述」：

**Layer 1 — 關鍵字觸發**（高信心度）

| 關鍵字 | 範例 |
|:------|:-----|
| `產生簡報` | 「幫我產生簡報」 |
| `md 轉 pptx` | 「把這個 md 轉 pptx」 |
| `markdown 投影片` | 「從 markdown 做投影片」 |
| `make slides` | 「make slides from this」 |
| `pptx` | 「產生 .pptx」 |
| `build deck` | 「build a deck」 |

**Layer 2 — 意圖觸發**（中信心度）

| 場景 | 範例 |
|:-----|:-----|
| 有 .md 檔 + 提到「簡報 / 投影片 / PPTX / deck / slides」 | 「把 README 變成簡報分享給團隊」 |
| 有 .md 檔 + 提到「展示 / 分享 / 教學」 | 「想展示這份教學內容」 |
| 提到現有檔名 + 期望輸出 | 「00-overview.md 做成 pptx」 |

### 3.2 SKILL.md 範本

```markdown
---
name: learn2deck
description: 從 Markdown 教材與技術文件自動產生符合設計風格的 PPTX 簡報。Use this skill when the user asks to "產生簡報", "md 轉 pptx", "make slides from markdown", "build a deck", or mentions converting markdown content to PowerPoint/PPTX. Do NOT use for editing existing PPTX files or general presentation advice.
---

# learn2deck Skill

從 Markdown 自動產生符合設計風格的 PPTX 簡報。

## 觸發條件

- 使用者說「產生簡報 / 做投影片 / build deck / make slides」
- 有 .md 檔且想轉成 .pptx

## 不要觸發

- 編輯現有 .pptx（用戶端工具）
- 一般簡報建議（不在 skill 範圍）

## 執行流程

1. **識別輸入檔**：找到 .md 檔（單一或多個）
2. **確認輸出位置**：
   - 預設：`/tmp/new_<basename>.pptx`
   - 或使用者指定
3. **執行 build**：
   ```bash
   learn2deck build <input.md> -o <output.pptx> --validate
   ```
4. **檢查驗證結果**：
   - ✨ No issues found → 報告成功
   - 有 Issues → 列出問題，問使用者是否繼續
5. **報告結果**：
   - slides 數
   - 視覺驗證狀態
   - 輸出檔位置

## 範例

### 單檔
> 「幫我把 04-skills.md 做成簡報」
→ 執行 `learn2deck build 04-skills.md -o /tmp/new_skills.pptx`

### 多檔
> 「我要 8 份文件的簡報」
→ 對 00-07 全部執行 build

### 帶驗證
> 「產生簡報並驗證」
→ 加上 `--validate` flag

## 錯誤處理

- CLI 失敗 → 報告錯誤訊息，建議檢查 .md 格式
- 驗證有 Issues → 列出具體 issue，問使用者是否接受
- .md 找不到 → 詢問檔案路徑

## 相關文件

- `references/style-guide.md` — 設計系統
- `references/slide-types.md` — 9 種版型
- `references/cli-reference.md` — 完整 CLI
- `examples/minimal-plugin/` — 範例

## 注意事項

- v1.0 純規則版，不呼叫 LLM
- 視覺風格為 claude-orange 主題
- 8 份 .md 已驗證可正確解析（277/277 slides 對齊）
```

### 3.3 觸發語測試案例

下個 session 必須測試：

```bash
# 在 pi-proj 目錄下，用 Claude Code 測試這些觸發語：

"幫我把 04-skills.md 做成簡報"
→ 預期：Claude 呼叫 learn2deck skill

"從 markdown 產生 pptx"
→ 預期：Claude 詢問哪個 .md

"我要 8 份文件的簡報"
→ 預期：Claude 對 00-07 全部 build

"用 learn2deck build 00-overview.md"
→ 預期：Claude 直接執行（明確指令）
```

---

## 4. references/ 內容設計

### 4.1 references/style-guide.md

**目的**：設計系統權威參考（從 `_pptx_helpers.py` 提取）

```markdown
# Claude Orange 主題設計指南

## 顏色
| 名稱 | Hex | 用途 |
|------|-----|------|
| primary | #C75A1A | 橘色裝飾條 |
| bg_cream | #FAF8F3 | 背景米白 |
| dark | #2C2C2C | 主要文字 |
| gray_text | #6B6B6B | 次要文字 |
| bg_gray | #F3F0E9 | 卡片背景 |
| white | #FFFFFF | 卡片文字 |

## 字體
- title: Calibri
- body: Calibri
- code: Consolas

## 安全區
- 頂部：1.3" 起
- 底部：7.0" 止（容忍至 7.35"）
- 左：0.5" 起
- 右：12.833" 止

## 裝飾
- 頂部橘色條：0.15" 高 × 13.33" 寬
- 底部品牌列：y=7.1"
- 頁碼：右上角
```

### 4.2 references/slide-types.md

**目的**：9 種版型速查

```markdown
# 9 種 Slide Type 速查

| Type | 用途 | body schema |
|------|------|-------------|
| cover | 封面 | {tag: string} |
| objectives | 學習目標 | {items: [...]} |
| section | 章節分隔 | {section_num, section_subtitle} |
| title_content | 標題+文字 | {items: [str]} 或 {text: str} |
| title_table | 標題+表格 | {headers, rows} |
| title_code | 標題+程式碼 | {code, language} |
| two_column | 雙欄對比 | {left, right} |
| grid_cards | 網格卡片 | {items: [{icon, title, desc}], cols?} |
| summary | 重點回顧 | {key_points: [...]} |

## Markdown 對應規則

| Markdown | Slide Type |
|----------|------------|
| `## Part X: 標題` | section_divider |
| `## 標題` + table | title_table |
| `## 標題` + ```code``` | title_code |
| `## 標題` + 3+ ### H3 | grid_cards |
| `## 下一步` | summary |
| 其他 | title_content（預設）|
```

### 4.3 references/validation-rules.md

**目的**：R1-R5 規則詳解

```markdown
# 驗證規則詳解

## R1: code 框容量（錯誤）
- 規則：N 行 × 行高 ≤ 框高
- 自動修正：加大高度或縮小字體

## R2: 元素重疊（錯誤）
- 規則：兩個非配對元素 bounding box 有交集
- 自動修正：提示下移後者

## R3: 品牌列安全（警告）
- 規則：top + height > 7.0"
- 自動修正：建議重新配置

## R5: 檔案格式（錯誤）
- 規則：產出檔案不是 Microsoft PowerPoint 2007+
- 自動修正：阻止產出
```

### 4.4 references/cli-reference.md

**目的**：完整 CLI 指令速查

```markdown
# CLI 完整參考

## learn2deck build
learn2deck build <input> -o <output> [--validate] [--theme <name>] [--quiet]

## learn2deck validate
learn2deck validate <input>

## learn2deck theme list
learn2deck theme list

## learn2deck theme show <name>
learn2deck theme show <name>

## learn2deck init <dir>
learn2deck init my-project

## learn2deck version
learn2deck version
```

### 4.5 references/troubleshooting.md

**目的**：常見問題與解決方案

```markdown
# 疑難排解

## Q: build 失敗 list index out of range
A: Markdown table 的 column 數不一致。檢查 `|` 是否需要跳脫為 `\|`

## Q: 表格塞不下
A: 拆成多張 slide，或減少 row 數

## Q: 重疊 warning (R2)
A: grid_cards 的 desc 太長。縮短或加寬 col

## Q: Markdown 沒被解析
A: 檢查 H2 標題格式（## 開頭）
```

---

## 5. templates/ 範本設計

### 5.1 templates/tutorial-outline.yaml

```yaml
# 教學型簡報範本（適合分章節教學）
deck:
  title: 教學主題
  subtitle: 學習指南
  theme: claude-orange

slides:
  - type: cover
    title: 教學主題
    body: {tag: 教學 · #00}

  - type: objectives
    title: 本章你會學到
    body:
      items:
        - {icon: 🎯, title: 概念, desc: 核心觀念}
        - {icon: 🛠, title: 實作, desc: 動手做}

  - type: section_divider
    title: Part 1: 基礎
    subtitle: 第一個章節

  - type: title_content
    title: 內容標題
    body: {items: [bullet1, bullet2]}
```

### 5.2 templates/reference-spec.yaml

```yaml
# 技術規格型簡報範本（適合 API/CLI 參考）
deck:
  title: 技術規格
  theme: claude-orange

slides:
  - type: cover
    title: 規格文件
    body: {tag: API Reference}

  - type: title_table
    title: 完整欄位速查
    body:
      headers: [欄位, 類型, 必填, 描述]
      rows:
        - [name, string, 是, 識別碼]

  - type: title_code
    title: 使用範例
    body: {code: "...", language: bash}
```

### 5.3 templates/quickstart.yaml

```yaml
# 快速入門型簡報範本（適合 5 步驟教學）
deck:
  title: 快速入門
  theme: claude-orange

slides:
  - type: cover
    title: 5 分鐘學會 XXX

  - type: grid_cards
    title: 5 個步驟
    body:
      items:
        - {icon: 1️⃣, title: 步驟一, desc: ...}
        - {icon: 2️⃣, title: 步驟二, desc: ...}
        ...
```

---

## 6. 開發時程規劃

### Session 1（Phase 11 — 純 Skill 整合，3-4 小時）

| 工作項目 | 預估時間 |
|:---------|:--------:|
| 1.1 建立 SKILL.md | 1 小時 |
| 1.2 建立 references/ 5 個檔案 | 1.5 小時 |
| 1.3 建立 templates/ 3 個範本 | 0.5 小時 |
| 1.4 測試觸發語（手動 + Claude Code）| 0.5 小時 |
| 1.5 更新 HANDOFF + commit | 0.5 小時 |
| **總計** | **4 小時** |

### Session 2+（Phase 12 — Agent 整合，待評估）

依照 `docs/learn2deck-agent-supplement.md`：

| 工作項目 | 預估時間 |
|:---------|:--------:|
| 2.1 BaseLLMAgent 抽象介面 | 2 小時 |
| 2.2 ClaudeAgent 實作 | 3 小時 |
| 2.3 A1-A6 6 個 Agent 能力 | 6-8 小時 |
| 2.4 --ai-assist CLI flag | 1 小時 |
| 2.5 測試 + commit | 1 小時 |
| **總計** | **~15 小時** |

---

## 7. 開發步驟（依序）

### 步驟 1：建立 SKILL.md

```bash
cd /home/elan/pi-proj/learn2deck
# 建立 SKILL.md（內容見 §3.2）
vim SKILL.md
```

### 步驟 2：建立 references/

```bash
mkdir -p references
# 建立 5 個 .md 檔案
for f in style-guide slide-types validation-rules troubleshooting cli-reference; do
  touch references/${f}.md
done
# 填入內容（§4）
```

### 步驟 3：建立 templates/

```bash
mkdir -p templates
# 建立 3 個 YAML 範本
touch templates/tutorial-outline.yaml
touch templates/reference-spec.yaml
touch templates/quickstart.yaml
```

### 步驟 4：測試觸發語

```bash
# 安裝到 ~/.claude/skills/learn2deck/
ln -s /home/elan/pi-proj/learn2deck ~/.claude/skills/learn2deck

# 用 Claude Code 測試：
# 1. "幫我把 00-overview.md 做成簡報"
# 2. "從 markdown 產生 pptx"
# 3. "make slides from 04-skills.md"
```

### 步驟 5：更新文件並 commit

```bash
git add SKILL.md references/ templates/
git commit -m "feat(learn2deck): Phase 11 - Claude skill integration

- SKILL.md with double-layer trigger strategy
- references/ with style-guide, slide-types, validation-rules,
  troubleshooting, cli-reference
- templates/ with 3 outline templates (tutorial, reference, quickstart)
- 觸發語測試通過：[列測試案例]"
```

---

## 8. 驗收標準

### Phase 11 完成條件

- [ ] SKILL.md 建立完成（觸發描述完整）
- [ ] references/ 5 個檔案建立（每個至少 50 行）
- [ ] templates/ 3 個 YAML 範本建立（每個至少 20 行）
- [ ] 觸發語測試：3+ 個案例成功觸發 skill
- [ ] 觸發語測試：1+ 個「不要觸發」案例正確排除
- [ ] 233+ tests 仍然 pass
- [ ] Commit + tag v1.1.0

### 測試觸發語矩陣

| 觸發語 | 預期行為 |
|:-------|:---------|
| 「幫我把 04-skills.md 做成簡報」 | ✅ 觸發 skill |
| 「從 markdown 產生 pptx」 | ✅ 觸發 skill |
| 「make slides from this md」 | ✅ 觸發 skill |
| 「build a deck for 00-overview」 | ✅ 觸發 skill |
| 「把這個 .pptx 改成橫式」 | ❌ 不觸發（編輯現有）|
| 「幫我看一下這個 pptx」 | ❌ 不觸發（檢視）|

---

## 9. 風險與緩解

### 風險 1：觸發語誤觸發

**情境**：使用者說「這份 markdown 很好」也可能觸發。

**緩解**：SKILL.md 的「Do NOT use for」明確排除。

### 風險 2：CLI 路徑問題

**情境**：skill 啟動時找不到 `learn2deck` 指令。

**緩解**：SKILL.md 註明需要 `.pptx-venv/bin/learn2deck` 路徑，或全域安裝。

### 風險 3：多檔觸發時效能

**情境**：使用者說「8 份都做」，8 次 build 會花時間。

**緩解**：skill 內提示「將花費 ~5 分鐘」，並用平行 build（background task）。

---

## 10. 給下個 session 的入口

### 最優先要做的 3 件事

1. **建立 SKILL.md**（內容見 §3.2）— 直接 vim / write 即可
2. **建立 references/ 5 個檔案** — 內容見 §4
3. **測試觸發語** — 用 Claude Code 實測

### 完成後

- 更新本 HANDOFF.md 標記 Phase 11 完成
- Commit + tag v1.1.0
- 進入 Phase 12（Agent 整合）

---

## 11. v1.0.0 完成總結（背景）

v1.0.0 純規則版已於 `b5f5cd2` commit 達成：

- ✅ 233 tests pass
- ✅ 8 份 .pptx 對齊舊版（277/277 slides）
- ✅ CLI 4 個指令（build/validate/theme/init）
- ✅ Tag v1.0.0 + merged to main

Phase 11 是**讓使用者用觸發語呼叫 v1.0.0**，而不是取代或擴充它。

---

**Handoff 結束。下一個任務接手者請從「Phase 11: Skill 觸發語整合」開始（見本文件 §3-§7）。**
