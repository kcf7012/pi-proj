# Handoff Document — learn2deck v1.0 開發

> **交接給下一個任務使用**
> 建立日期：2026/08
> 最後更新：2026/08（Phase 8 完成）
> 對應 GitHub：[kcf7012/pi-proj](https://github.com/kcf7012/pi-proj) `develop` 分支
> 對應 commit：`34a6e38` (Phase 8)

---

## 0. 狀態總結（2026/08）

- ✅ **Phase 1-8 全部完成**：套件骨架、核心資料結構、pptx_helpers、內建主題、9 種 builder、Markdown 解析器、4 條驗證規則、CLI 整合
- ✅ **8 份現有 .md 全部能 CLI build + validate 通過**
- ⏳ **Phase 9 待做**：用 8 份現有 .md 重產 8 份 PPTX 視覺驗證（**最重要的成功標準**）
- ⏳ **Phase 10 待做**：文檔 + examples + 發佈
- 📊 **目前狀態**：**220 個測試全通過**、9 個 commit、純規則版完成

---

## 1. 目前任務目標

實作 `learn2deck` skill package 的 v1.0 純規則版（無 LLM）。完整規格見 `docs/learn2deck-spec.md`。

**最終成功標準**（最重要，**不能妥協**）：
> 用 learn2deck 重新產出的 8 份 PPTX（00/01/02/03/04/05/06/07）必須在版面、內容、視覺上與 pi-proj 現有版本**無法區分**。

> **Phase 8 進度**：CLI 端到端可用，R1/R2/R3/R5 驗證規則正常運作，但**視覺上**還沒有人工比對確認。

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
└── tests/
    ├── test_core.py                   ← 21 tests
    ├── test_pptx_helpers.py           ← 31 tests
    ├── test_themes.py                 ← 20 tests
    ├── test_builders.py               ← 26 tests
    ├── test_parsers.py                ← 54 tests
    ├── test_validators.py             ← 38 tests
    └── test_cli.py                    ← 30 tests
```

### 2.2 測試結果

```
220 passed in 3.42s
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

- ⏳ **Phase 9 視覺驗證（最關鍵）**：用 8 份 .md 重產 8 份 PPTX，**逐張人工比對**與 pi-proj 現有版本是否視覺一致
  - 用 LibreOffice 或 PowerPoint 開啟新舊版本
  - 重點檢查：標題位置、字體大小、code 框高度、卡片對齊
  - 預期可能需要微調 builder 的 `top`、`height`、`font_size` 等參數
- ⏳ **CALLOUT 在 two_column 中的特殊處理**（目前直接用 title_content builder）
- ⏳ **YAML outline 解析**：目前只支援 .md，.yaml/.yml 拋出 NotImplementedError
- ⏳ **chinese 標點在 code block 中的字寬**：可能導致某些行被截斷
- ⏳ **inline code（`code`）的處理**：Markdown 內的 `code` 反引號目前不會觸發 title_code builder
- ⏳ **Section 與 Section 之間的 H2 內容重複**：例如 06-hooks 有多個 H2 內含程式碼，可能需要拆分

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

### Phase 9：視覺驗證（**最關鍵的成功標準**）
目標：確認 8 份新產出的 PPTX 與 pi-proj 現有版本視覺一致

1. 開啟 PowerPoint 或 LibreOffice
2. 對比 `01-plugin-marketplaces.pptx`（新）vs `01-plugin-marketplaces.pptx`（舊）
3. 逐張檢查：版面、字體、顏色、code 框容量
4. 發現差異 → 改 builder（不是改 _pptx_helpers.py）→ 重跑測試 → 重產
5. 重複 8 次

具體檢查清單：
- [ ] Cover: 大標題、副標題、tag 位置
- [ ] Objectives: 卡片網格對齊、icon 位置
- [ ] Section: 大編號字級、位置
- [ ] Title+content: bullets 對齊、字級
- [ ] Title+table: 表格 alternating row bg
- [ ] Title+code: code 框高度、字體 monospace
- [ ] Two column: 卡片邊框顏色、bullet 對齊
- [ ] Grid cards: 卡片大小、icon 位置
- [ ] Summary: 關鍵要點、下一步

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

**Handoff 結束。下一個任務接手者請從「Phase 9 視覺驗證」開始（最重要的成功標準）。**
