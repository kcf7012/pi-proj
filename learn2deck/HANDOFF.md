# Handoff Document — learn2deck v1.0 開發

> **交接給下一個任務使用**
> 建立日期：2026/08
> 最後更新：2026/08（Phase 9 部分完成）
> 對應 GitHub：[kcf7012/pi-proj](https://github.com/kcf7012/pi-proj) `develop` 分支
> 對應 commit：`048ebba` (Phase 9 部分)

---

## 0. 狀態總結（2026/08）

- ✅ **Phase 1-8 全部完成**：套件骨架、核心資料結構、pptx_helpers、內建主題、9 種 builder、Markdown 解析器、4 條驗證規則、CLI 整合
- ✅ **Phase 9 部分完成**：markdown inline strip（`commits e7b3f2d` + `048ebba`）+ 結構驗證工具
- ⏳ **Phase 9 剩餘**：完整視覺驗證需由使用者用 LibreOffice / PowerPoint 比對
- ⏳ **Phase 10 待做**：文檔 + examples + 發佈
- 📊 **目前狀態**：**230 個測試全通過**、11 個 commit、純規則版完成

### Phase 9 環境限制

本環境無 LibreOffice / PowerPoint / pdftoppm，無法做真正的「視覺並排比對」。Phase 9 退而求其次：

1. **結構驗證**：tools/structural_report.py 量化 8 份新舊 pptx 的 slide 數 / shape 數 / 文字量
2. **版面檢查**：tools/layout_check.py 檢查形狀是否超出安全區、表格 / code 是否塞不下
3. **parser bug 修正**：markdown inline strip（commit `e7b3f2d`）
4. **最終人工視覺驗證**：使用者需在本機用 LibreOffice 開新舊 .pptx 並排確認

### Phase 9 識別但未修正的 bug（建議 v1.1）

- ⚠️ markdown parser 不會自動插入 COVER slide
- ⚠️ markdown parser 不會自動插入 SECTION_DIVIDER（無 `Part X` 偵測）
- ⚠️ grid_cards 推斷優先順序：當 H2 同時有 code + H3>=3 時，code 勝出而非 grid_cards
- ⚠️ 範例程式碼內的 `## H2`（如 SKILL.md 範例）會被誤認為頂層章節
- ⚠️ numbered list（`1. ` 開頭）不會被解析成 bullet

---

## 1. 目前任務目標

實作 `learn2deck` skill package 的 v1.0 純規則版（無 LLM）。完整規格見 `docs/learn2deck-spec.md`。

**最終成功標準**（最重要，**不能妥協**）：
> 用 learn2deck 重新產出的 8 份 PPTX（00/01/02/03/04/05/06/07）必須在版面、內容、視覺上與 pi-proj 現有版本**無法區分**。

> **Phase 9 進度**：markdown inline 標記已正確 strip（表格 cell 不再顯示 `**` 和 `` ` ``），但**完整視覺驗證**還沒做（環境限制 + 還有多個 builder bug 待修）。

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
