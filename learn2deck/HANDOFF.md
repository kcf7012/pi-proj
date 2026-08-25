# Handoff Document — learn2deck v1.0 開發

> **交接給下一個任務使用**
> 建立日期：2026/08
> 對應 GitHub：[kcf7012/pi-proj](https://github.com/kcf7012/pi-proj) `develop` 分支
> 對應 commit：`e5118c0` (Phase 5)

---

## 0. 狀態總結

- ✅ **Phase 1-5 完成**：套件骨架 + 核心資料結構 + pptx_helpers + 內建主題 + 9 種 builder
- ⏳ **Phase 6 進行中**：Markdown 解析器
- ⏳ **Phase 7 待做**：4 條驗證規則
- ⏳ **Phase 8 待做**：CLI 整合
- ⏳ **Phase 9 待做**：用 8 份現有 .md 重產 8 份 PPTX 視覺驗證（**最重要的成功標準**）
- 📊 **目前狀態**：98 個測試全通過，4 個檔案 commit

---

## 1. 目前任務目標

實作 `learn2deck` skill package 的 v1.0 純規則版（無 LLM）。完整規格見 `docs/learn2deck-spec.md`。

**最終成功標準**（最重要，**不能妥協**）：
> 用 learn2deck 重新產出的 8 份 PPTX（00/01/03/05/07）必須在版面、內容、視覺上與 pi-proj 現有版本**無法區分**。

---

## 2. 已完成內容（Phase 1-5）

### 2.1 套件結構

```
/home/elan/pi-proj/learn2deck/          ← 專案根目錄
├── pyproject.toml                     ← 套件定義（已安裝到 .pptx-venv）
├── README.md                          ← 快速使用
├── Makefile                           ← dev 指令
├── .gitignore
├── learn2deck/                        ← Python package
│   ├── __init__.py                    ← __version__ = "0.1.0"
│   ├── cli.py                         ← typer CLI（目前只有 version 子指令）
│   └── lib/
│       ├── core/                      ✓ Phase 2
│       │   ├── exceptions.py          ← 16 個自訂例外
│       │   ├── theme.py               ← Theme dataclass + 載入器
│       │   └── deck.py                ← SlideType enum + SlideContent + DeckSpec
│       ├── pptx_helpers/              ✓ Phase 3
│       │   ├── layout.py              ← 版面常數 + 計算工具
│       │   ├── shapes.py              ← 12 個基礎形狀函式
│       │   ├── pages.py               ← 4 個特殊頁面（cover/section/summary/two_col）
│       │   └── __init__.py
│       ├── themes/                     ✓ Phase 4
│       │   ├── claude-orange.yaml     ← 預設主題（與 pi-proj 100% 一致）
│       │   ├── minimal-bw.yaml        ← 黑白極簡風
│       │   └── __init__.py
│       ├── builders/                   ✓ Phase 5
│       │   ├── base.py                ← BaseBuilder 抽象 + build_slide + build_full_deck
│       │   ├── cover.py               ← COVER
│       │   ├── section_divider.py     ← SECTION_DIVIDER
│       │   ├── objectives.py          ← OBJECTIVES（繼承 GridCards）
│       │   ├── title_content.py       ← TITLE_CONTENT + CALLOUT
│       │   ├── title_table.py         ← TITLE_TABLE
│       │   ├── title_code.py          ← TITLE_CODE
│       │   ├── two_column.py          ← TWO_COLUMN
│       │   ├── grid_cards.py          ← GRID_CARDS
│       │   ├── summary.py             ← SUMMARY
│       │   └── __init__.py
│       ├── parsers/                    ⏳ Phase 6（待做）
│       └── validators/                 ⏳ Phase 7（待做）
└── tests/
    ├── test_core.py                   ← 21 tests
    ├── test_pptx_helpers.py           ← 31 tests
    ├── test_themes.py                 ← 20 tests
    └── test_builders.py               ← 26 tests
```

### 2.2 測試結果

```
98 passed in 0.73s
```

### 2.3 重要設計決策（不要變更）

| 決策 | 內容 |
|------|------|
| **Builder 介面** | `build(slide, content, slide_num, total)` |
| **body schema** | 見 `docs/learn2deck-spec.md` §4.2 註解 |
| **Theme 讀取** | 所有函式接 `theme: Theme \| None = None`，沒設用預設值 |
| **特殊頁處理** | COVER 與 SECTION_DIVIDER 必須透過 `build_full_deck()`（因 add_cover_slide 需要 prs） |
| **body 顏色** | TwoColumn 的 `left_color` / `right_color` 是 **theme color name**（如 "blue"），不是 hex |
| **Objectives 預設標題** | 沒給 title 時自動填入「本章你會學到」 |
| **CALLOUT body** | title_content builder 也支援，body 內含 text + icon + style(info/warning/success) |

---

## 3. 關鍵文件和位置

### 3.1 規格文件（必讀）

```
/home/elan/pi-proj/docs/
├── learn2deck-spec.md              ← 主 spec（1450 行，所有設計決策）
├── learn2deck-agent-supplement.md  ← Agent 補充（500 行，v1.1 才用）
└── learn2deck-llm-strategy.md      ← LLM 策略（842 行，v1.1+ 才用）
```

### 3.2 參考資源（**最重要的視覺基準**）

```
/home/elan/pi-proj/
├── _pptx_helpers.py                ← 19 個函式的權威參考
├── _make_00_overview.py            ← 30 張簡報的 builder 範例
├── _make_01_marketplaces.py        ← 35 張
├── _make_02_plugins.py             ← 25 張
├── _make_03_plugins_reference.py   ← 45 張
├── _make_04_skills.py              ← 40 張
├── _make_05_subagents.py           ← 30 張
├── _make_06_hooks.py               ← 50 張
├── _make_07_discover_plugins.py    ← 22 張
└── 00-07*.pptx                     ← 8 份現有 PPTX（**視覺驗證基準**）
```

### 3.3 環境

```bash
# Python 環境（已安裝 learn2deck）
/home/elan/pi-proj/.pptx-venv/bin/python

# 套件已用 -e 模式安裝（修改即生效）
uv pip install --python /home/elan/pi-proj/.pptx-venv/bin/python -e ".[dev]"

# 跑測試
cd /home/elan/pi-proj/learn2deck
/home/elan/pi-proj/.pptx-venv/bin/python -m pytest tests/
```

---

## 4. 重要規則和限制

### 4.1 設計系統（從 pi-proj 移植）

- 簡報尺寸：**16:9**（13.333 × 7.5 inch）
- 底部品牌列 y=7.1"，**所有內容必須在 7.0" 以內**
- 標題列 y=0-1.15"，**內容從 1.3" 開始**
- Claude 橘 `#C75A1A`、米白 `#FAF8F3`、深灰 `#2C2C2C`
- 字體：Calibri / Calibri / Consolas

### 4.2 pptx 設計陷阱（重要！）

- ❌ **不要用 `add_connector(1, ...)`** 畫箭頭（會被 PowerPoint 繞路）
- ✅ 用 `MSO_SHAPE.RIGHT_ARROW` 三角形
- Code 框的字高估算：`12pt → 0.20"/行`，9pt → 0.15"，8pt → 0.14"
- 文字框 `add_text_block` **不會自動調整高度**，必須手動算空間

### 4.3 主題抽象（v1.0 不可妥協的約定）

```python
# ✓ 正確
def my_function(theme: Theme | None = None):
    color = _color(theme, "primary", "#C75A1A")  # 提供 fallback
    font = _font(theme, "title", "Calibri")
    size = get_font_size(theme, "body", 14)  # 第二個參數是 fallback

# ✗ 錯誤
def my_function():
    from ..pptx_helpers.shapes import COLOR_PRIMARY  # 全域常數已不存在
```

### 4.4 套件結構限制

- **不要把 `lib/` 加進 `.gitignore`**（之前已修，package code 在 lib/ 下）
- 內建主題路徑：`learn2deck/lib/themes/{name}.yaml`
- 內建主題名稱用連字號：`claude-orange`（不是底線）

---

## 5. 已確認結論

1. ✅ **9 種 builder 全部運作**（用 build_full_deck() 從 DeckSpec 產 9 張 PPTX，40KB，PowerPoint 2007+ 格式）
2. ✅ **claude-orange 主題與 pi-proj 100% 一致**（11 個顏色 hex 值逐個比對通過）
3. ✅ **向後相容**：所有 pptx_helpers 函式在 theme=None 時仍可運作（用預設值）
4. ✅ **98 個測試全通過**
5. ✅ **已安裝到 .pptx-venv**：`learn2deck --help` 與 `learn2deck version` 可執行

---

## 6. 待確認事項

- ⏳ **Phase 9 視覺驗證**：用 8 份現有 .md 重產 8 份 PPTX，比對版面（**最關鍵**）
- ⏳ **Phase 6 解析器**：如何處理 Markdown 自動推斷 slide_type 的啟發式（見 spec §4.4）
- ⏳ **CALLOUT 在兩欄對比中的特殊用法**：spec 沒明確說，目前 title_content 也支援
- ⏳ **未知來源**：Markdown frontmatter 中可否省略 title？（spec 沒明說，目前實作會 MissingFieldError）

---

## 7. 不要重複做的事情

### ❌ 不要重新設計 builder 介面
目前 `build(slide, content, slide_num, total)` 介面已通過 26 個測試，不要變動。

### ❌ 不要把 COVER/SECTION_DIVIDER 改成可在 `build()` 內建立
它們需要 `Presentation` 物件（用 `add_cover_slide(prs, ...)`），不能在既有 `Slide` 上畫。請維持現有「必須透過 build_full_deck()」的設計。

### ❌ 不要用全域顏色常數
所有顏色/字體/字級都從 `theme.get_color(name)` 取得。**全域常數已不存在**。

### ❌ 不要重建 `_postprocess_fix_overflow.py` 之類的工具
直接改 builder + 跑測試比事後修補更可靠。

### ❌ 不要把 `lib/` 加進 `.gitignore`
package code 在 lib/ 下，加進去會被忽略整個 package。

### ❌ 不要在 builder 內建新 SlideType
10 種 SlideType 已固定，要新增需先改 spec。

---

## 8. 建議下一步（Phase 6-10）

### Phase 6：Markdown 解析器（**下一個**）
目標：讓 `learn2deck build input.md -o output.pptx` 真的能跑

需要做的：
- `parsers/frontmatter.py`：解析 YAML frontmatter（`---\n...\n---`）
- `parsers/markdown.py`：把 Markdown 章節轉成 SlideContent
- 自動推斷 slide_type（啟發式，見 spec §4.4）：
  - 標題含「學習目標/Objectives/你會學到」→ OBJECTIVES
  - 標題含「Part N/章節 N/Section N」→ SECTION_DIVIDER
  - H2 後有 3+ 子標題 → GRID_CARDS
  - H2 後有「✅/❌/優點/缺點」→ TWO_COLUMN
  - 內含 ```code block``` → TITLE_CODE
  - 內含 Markdown table → TITLE_TABLE
  - 預設 → TITLE_CONTENT
- `parsers/yaml_outline.py`：支援 YAML 大綱格式

驗證標準：8 份現有 .md 能被解析為正確的 DeckSpec

### Phase 7：4 條驗證規則
- R1: code 框容量（N 行 × 行高 + 0.2" margin ≤ 框高）
- R2: 元素重疊
- R3: 品牌列安全（> 7.0" 警告）
- R5: PPTX 格式（PowerPoint 2007+）

### Phase 8：CLI 整合
- `learn2deck build input.md -o output.pptx --theme claude-orange`
- `learn2deck validate output.pptx`
- `learn2deck theme list`

### Phase 9：整合測試（**最關鍵**）
1. 把 8 份現有 .md 轉成結構化格式（或靠自動推斷）
2. 用 `learn2deck build` 重產 8 份 PPTX
3. 用 LibreOffice 或 Python 腳本比對版面（不能依賴肉眼）
4. 修正任何差異

### Phase 10：文檔與發佈
- 範例 examples/
- 更新 pi-proj README
- 決定是否 merge 到 main

---

## 附錄 A：Phase 6 快速起步指南

```bash
# 1. 切換到 develop 分支（已經在上面）
cd /home/elan/pi-proj
git checkout develop

# 2. 建立 parsers 套件結構
mkdir -p learn2deck/learn2deck/lib/parsers
touch learn2deck/learn2deck/lib/parsers/__init__.py
touch learn2deck/learn2deck/lib/parsers/.gitkeep  # 有真實檔案後刪掉

# 3. 建議的 parser 設計
# parsers/frontmatter.py: 解析 "---\nkey: value\n---\n"
# parsers/markdown.py: 用 python-markdown 或自寫 regex 解析 H2 章節
# parsers/yaml_outline.py: 完整的 YAML 大綱格式
# parsers/__init__.py: parse_content(input_path) -> DeckSpec 主入口
```

```python
# 主要 API 設計建議
def parse_content(source_path: str) -> DeckSpec:
    """從 .md 或 .yaml 檔案建立 DeckSpec

    - 自動偵測格式（frontmatter 開頭的 '---'）
    - 解析標題、副標題、章節
    - 自動推斷 slide_type
    """
    path = Path(source_path)
    if path.suffix in (".yaml", ".yml"):
        return parse_yaml_outline(path)
    return parse_markdown(path)


# 自動推斷的輔助函式
def infer_slide_type(title: str, content: str) -> SlideType:
    """根據標題與內容推斷 slide_type"""
    # 啟發式規則見 spec §4.4
    ...
```

### 附錄 B：8 份現有 .md 的章節結構

可從這些檔案取得自動推斷的測試資料：

| 檔案 | 章節數 | 特殊版型 |
|------|--------|----------|
| 00-claude-code-plugins-series.md | ~10 | 學習目標、章節分隔、總結 |
| 01-plugin-marketplaces.md | ~18 | 表格、雙欄比較、列表 |
| 02-plugins.md | ~13 | 程式碼、表格、圖示 |
| 03-plugins-reference.md | ~16 | 大量程式碼、表格、目錄樹 |
| 04-skills.md | ~15 | 程式碼、表格、流程圖 |
| 05-subagents.md | ~12 | 程式碼、範例 |
| 06-hooks.md | ~18 | 程式碼、表格、流程圖 |
| 07-discover-plugins.md | ~9 | 表格、命令列 |

---

**Handoff 結束。下一個任務接手者請從「Phase 6: Markdown 解析器」開始。**
