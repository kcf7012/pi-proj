# Skill Package 軟體開發需求文件

> **專案名稱**：`learn2deck`（暫定，可改）
> **文件版本**：v1.0 草案
> **建立日期**：2026/08
> **狀態**：待 review（請確認後開始實作）
> **作者**：Kenny Kang

---

## 1. 背景與動機

### 1.1 問題陳述

目前「從官方文件 → Markdown 教材 → PPTX 簡報」的流程是**手動且零散**的：

- Markdown 教材與 PPTX 各自獨立撰寫，**容易出現內容不同步**
- 設計系統（顏色/字體/版面）以 **Python 常數**形式存在 `_pptx_helpers.py`，**無法在不修改程式碼的情況下擴展新風格**
- 每份新教材都需從頭寫一個 `_make_XX_*.py`（數百行），**重複性高**
- 版面驗證只能事後用 PowerPoint 開啟檢查，**沒有自動化品質把關**
- 風格擴展需要**理解整套 helper API**，門檻高

### 1.2 目標

建立一個 **可重複使用、可擴展、可驗證** 的技能包，達成：

1. **單一輸入**（結構化 Markdown 或大綱）→ **單一輸出**（符合母版的 PPTX）
2. **風格可插拔**：換 YAML 設定檔就能切換整套視覺風格（顏色/字體/版面/裝飾）
3. **品質內建**：產出前自動跑版面驗證（code 框容量、重疊、品牌列安全區）
4. **可堆疊**：未來能從教材一路串到官方文件爬取、章節規劃、簡報生成的完整 pipeline

### 1.3 非目標

- **不**取代 PowerPoint 排版 — 簡報的最終微調仍可在 PowerPoint 內進行
- **不**處理圖表/動畫/影片 — 專注於文字、表格、程式碼的靜態簡報
- **不**做即時協作或雲端同步 — 純本機 CLI / Skill 工具
- **不**重新發明 `python-pptx` — 把它當底層依賴

---

## 2. 技能包設計哲學

### 2.1 名稱建議

- **候選**：`learn2deck`、`doc2slides`、`md2pptx`、`topic2deck`
- **推薦**：`learn2deck` — 「從學習材料到簡報」，語意清楚且暗示 pipeline
- **可改**：請在 review 時指定

### 2.2 範圍分層

技能包由 4 層組成，每層都可獨立使用：

```
┌─────────────────────────────────────────┐
│  Layer 4: Style Themes (風格主題)        │  ← 可插拔：YAML 設定檔
├─────────────────────────────────────────┤
│  Layer 3: Slide Builders (投影片建構)    │  ← 標準 9 種版型
├─────────────────────────────────────────┤
│  Layer 2: Content Model (內容模型)       │  ← 結構化輸入解析
├─────────────────────────────────────────┤
│  Layer 1: Validation (品質驗證)          │  ← 自動檢查 + 修正建議
└─────────────────────────────────────────┘
```

**核心原則**：
- **低耦合**：每層只透過明確介面互動
- **高內聚**：每層自成一個 Python 模組/套件
- **可測試**：每層有對應的單元測試

### 2.3 與 Claude Code Skill 系統整合

依照 Claude Code 官方 Skills 規範（[文件連結](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview)）：

```
learn2deck/
├── SKILL.md                    ← Skill 描述（Claude 讀這個來決定是否啟用）
├── references/
│   ├── style-guide.md          ← 設計系統權威參考
│   ├── slide-types.md          ← 9 種投影片版型速查
│   ├── validation-rules.md     ← 品質規則
│   └── troubleshooting.md      ← 常見問題
├── scripts/
│   ├── build_deck.py           ← 主入口 CLI
│   ├── validate_deck.py        ← 獨立驗證工具
│   └── render_preview.py       ← 產出預覽圖（可選）
├── lib/
│   ├── theme.py                ← Theme 抽象基底 + 內建主題
│   ├── builders/               ← 9 種版型的 builder
│   ├── content_parser.py       ← Markdown/YAML/JSON 解析
│   └── validators/             ← 各項驗證規則
├── themes/                     ← 內建風格設定檔
│   ├── claude-orange.yaml      ← 現有 Claude 橘（移植自 pi-proj）
│   └── minimal-bw.yaml         ← 黑白極簡風（示範）
├── templates/                  ← 投影片內容模板
│   ├── tutorial-outline.yaml
│   ├── reference-spec.yaml
│   └── quickstart.yaml
├── tests/
│   ├── test_theme.py
│   ├── test_builders.py
│   ├── test_parsers.py
│   └── test_validators.py
├── examples/
│   ├── sample-content.md       ← 完整範例
│   ├── generated/              ← 範例產出
│   └── README.md
└── README.md
```

---

## 3. Layer 1：品質驗證

### 3.1 驗證項目

| 規則 | 嚴重度 | 說明 | 自動修正 |
|------|--------|------|----------|
| **R1: code 框容量** | 錯誤 | `N 行 × 行高 + 0.2" margin ≤ 框高` | 提示加大高度或縮小字體 |
| **R2: 元素重疊** | 錯誤 | 兩個非配對元素的 bounding box 有交集 | 提示下移後者 |
| **R3: 品牌列安全** | 警告 | 任何元素 `top + height > 7.0"` | 建議重新配置 |
| **R4: 標題列安全** | 警告 | 內容元素 `top < 1.3"` | 提示下移 |
| **R5: PPTX 格式** | 錯誤 | 產出檔案不是 `Microsoft PowerPoint 2007+` | 阻止產出 |
| **R6: 必填元素** | 錯誤 | 每張投影片需有 `title_bar` | 阻止產出 |
| **R7: 編號連續** | 警告 | 投影片編號不連續（如 1,2,4,5） | 提示修正 |
| **R8: 一致性** | 警告 | 跨投影片同類元素位置/字體不一致 | 列出所有不一致處 |
| **R9: 箭頭形狀** | 錯誤 | 流程圖中出現 `add_connector(1, ...)` | 阻擋並建議 `RIGHT_ARROW` |
| **R10: 章節分隔** | 建議 | 連續 > 8 張同類投影片無分隔 | 建議加入 Part 章節頁 |

### 3.2 驗證 API

```python
from learn2deck import validate_deck

report = validate_deck(
    pptx_path="output.pptx",
    rules=["R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8", "R9", "R10"],
    strict=False  # strict=True 會把警告也視為錯誤
)

# report 結構
{
    "passed": True | False,
    "errors": [...],
    "warnings": [...],
    "suggestions": [...],
    "stats": {
        "total_slides": 35,
        "code_blocks": 18,
        "tables": 7,
        "max_content_bottom": 6.85
    }
}
```

### 3.3 CLI 介面

```bash
# 獨立驗證
learn2deck validate output.pptx
learn2deck validate output.pptx --strict --report json
learn2deck validate output.pptx --rules R1,R2

# 自動修正（v1.1+）
learn2deck validate output.pptx --fix
```

### 3.4 與現有驗證腳本的關係

現有於 `pi-proj` 內的「ad-hoc Python 驗證腳本」（見 HANDOFF §4.3）將被**完整吸收**到 Layer 1。並擴充：
- 加入 8 條新規則
- 改為**可重複使用**的函式庫
- 提供**結構化報告**（不再是 print）
- 加入**建議清單**（不只是錯誤清單）

---

## 4. Layer 2：內容模型

### 4.1 核心資料結構

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional

class SlideType(Enum):
    COVER = "cover"
    OBJECTIVES = "objectives"           # 學習目標
    SECTION_DIVIDER = "section"          # 章節分隔
    TITLE_CONTENT = "title_content"      # 標題+內容（最常用）
    TWO_COLUMN_COMPARE = "two_column"    # 雙欄對比
    GRID_CARDS = "grid_cards"            # 網格卡片
    TITLE_TABLE = "title_table"          # 標題+表格
    TITLE_CODE = "title_code"            # 標題+程式碼
    CALLOUT = "callout"                  # 純提示框
    SUMMARY = "summary"                  # 重點回顧

@dataclass
class SlideContent:
    type: SlideType
    title: str
    subtitle: Optional[str] = None
    body: Optional[Dict] = None       # 依 type 不同結構不同
    slide_num: Optional[int] = None
    source_ref: Optional[str] = None # 對應的 Markdown 段落

@dataclass
class DeckSpec:
    title: str
    subtitle: str
    theme: str = "claude-orange"
    source_path: str                  # 原始 Markdown 路徑
    slides: List[SlideContent] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
```

### 4.2 支援的輸入格式

#### 4.2.1 結構化 Markdown（**主要格式**）

利用現有 8 份 `.md` 的風格，加上 YAML frontmatter：

```markdown
---
deck:
  title: Plugin 開發入門
  subtitle: 從零建立你的第一個 Claude Code Plugin
  theme: claude-orange
  source_ref: 02-plugins.md
  slide_types:
    objectives: 0
    section: 1
    title_content: 20
    two_column: 2
    summary: 1
---

# Plugin 開發入門
...

## Slide: 學習目標
slide_type: objectives
items:
  - icon: 🎯
    title: 理解 plugin 的核心概念
    desc: 為什麼要用 plugin？什麼時候該用？
  - icon: 📦
    title: 建立第一個 plugin
    desc: 從零開始的完整步驟
...

## Slide: 章節: 快速開始
slide_type: section
section_num: "Part 1"
section_title: Plugin vs 獨立配置
section_subtitle: 什麼時候該升級成 plugin？
...

## Slide: Plugin vs 獨立配置
slide_type: title_table
title: Plugin vs 獨立配置
subtitle: 兩種擴展 Claude Code 的方式
table:
  headers: [面向, 獨立配置, Plugin]
  rows:
    - [Skill 名稱, "/hello（簡短）", "/my-plugin:hello（命名空間）"]
    ...
```

#### 4.2.2 YAML 大綱（**精確控制**）

```yaml
deck:
  title: Plugin 開發入門
  theme: claude-orange
  
slides:
  - type: cover
    title: Plugin 開發入門
    subtitle: 從零建立你的第一個 Claude Code Plugin
    tag: "#02 · Plugin 開發"
    
  - type: objectives
    title: 本章你會學到
    subtitle: 建立、測試、除錯你的第一個 plugin
    items:
      - {icon: "🎯", title: "理解概念", desc: "..."}
      ...
      
  - type: section
    section_num: "Part 1"
    section_title: "..."
    
  - type: title_table
    title: "Plugin vs 獨立配置"
    subtitle: "..."
    table: {headers: [...], rows: [...]}
```

#### 4.2.3 純 Markdown（**向後相容**）

支援現有的 8 份 `.md`，自動推斷結構：
- `# 標題` → cover
- `## 學習目標 / 本章你會學到 / Objectives` → objectives
- `## 目錄 / Table of Contents` → toc（可選）
- `## Part N` 或 `## 章節 N` → section
- 其他 `## 標題` → title_content
- `## 比較 / 對比 / vs` → two_column
- 程式碼區塊（```）→ title_code
- 表格（Markdown table）→ title_table

### 4.3 解析器介面

```python
from learn2deck import parse_content

# 從 frontmatter Markdown
deck = parse_content("path/to/02-plugins.md")

# 從 YAML 大綱
deck = parse_content("path/to/outline.yaml")

# 從程式直接建立
deck = DeckSpec(title="...", slides=[...])
```

### 4.4 自動推斷的規則

對於**純 Markdown**輸入，以下啟發式規則：

| Markdown 模式 | 推斷為 | 信心度 |
|--------------|--------|--------|
| 開頭 H1 + 「副標題/一句話介紹」 | cover | 高 |
| `## ` 標題含「學習目標/Objectives/你會學到」 | objectives | 高 |
| `## ` 標題含「Part N/章節 N/Section N」 | section | 高 |
| H2 後有 3+ 個 `###` 子標題 | grid_cards | 中 |
| H2 後有「✅ / ❌ / 優點 / 缺點」並列 | two_column | 中 |
| 內含 3+ 行 ```code block``` | title_code | 高 |
| 內含 Markdown table | title_table | 高 |
| 其他 H2 | title_content | 預設 |

信心度低的會**標記為待確認**，可在 CLI 中互動修正。

---

## 5. Layer 3：投影片建構（Slide Builders）

### 5.1 9 種版型

每種版型對應一個 builder class，遵循統一介面：

```python
class BaseBuilder(ABC):
    def __init__(self, theme: Theme):
        self.theme = theme
    
    @abstractmethod
    def build(self, slide: SlideObject, content: SlideContent) -> None:
        """在 slide 上繪製對應版型"""
        pass
```

### 5.2 版型清單

| Builder | 用途 | 對應 SlideType |
|---------|------|---------------|
| `CoverBuilder` | 封面/標題頁 | COVER |
| `ObjectivesBuilder` | 學習目標（網格卡片） | OBJECTIVES |
| `SectionDividerBuilder` | 章節分隔（大數字+標題） | SECTION_DIVIDER |
| `TitleContentBuilder` | 標題+文字/子標題+bullet | TITLE_CONTENT |
| `TitleTableBuilder` | 標題+表格 | TITLE_TABLE |
| `TitleCodeBuilder` | 標題+程式碼區塊 | TITLE_CODE |
| `TwoColumnBuilder` | 雙欄對比 | TWO_COLUMN_COMPARE |
| `GridCardsBuilder` | 網格卡片（N×M） | GRID_CARDS |
| `SummaryBuilder` | 重點回顧 | SUMMARY |

### 5.3 內建 helper 函式（從 `_pptx_helpers.py` 移植）

| 函式 | 用途 | 移植來源 |
|------|------|---------|
| `new_presentation()` | 建立 16:9 簡報 | ✅ |
| `add_blank_slide(prs)` | 新增空白頁 | ✅ |
| `set_slide_bg(slide, color)` | 設定背景色 | ✅ |
| `add_title_bar(...)` | 標題列（含頁碼/來源） | ✅ |
| `add_text_block(...)` | 純文字區塊 | ✅ |
| `add_bullet_list(...)` | 階層式項目清單 | ✅ |
| `add_code_block(...)` | 深色背景程式碼 | ✅ |
| `add_callout(...)` | 圓角提示框 | ✅ |
| `add_comparison_table(...)` | 比較表格 | ✅ |
| `add_two_column_compare(...)` | 雙欄對比佈局 | ✅ |
| `add_flow_box(...)` | 流程圖方塊 | ✅ |
| `add_arrow(...)` | 箭頭（用 RIGHT_ARROW） | ✅ |
| `add_cover_slide(...)` | 封面頁 | ✅ |
| `add_section_divider(...)` | 章節分隔頁 | ✅ |
| `add_summary_slide(...)` | 重點回顧頁 | ✅ |

**改進點**：
- 所有函式加入 `theme` 參數，**不再依賴全域常數**
- 顏色/字體改從 `theme.get_color(name)` / `theme.get_font(name)` 取得
- 移除 magic numbers，改用具名常數

### 5.4 Builder 介面範例

```python
class TitleTableBuilder(BaseBuilder):
    def build(self, slide, content: SlideContent) -> None:
        # 1. 標題列
        self._add_title_bar(slide, content)
        # 2. 表格
        table_data = content.body["table"]
        self._add_comparison_table(
            slide,
            headers=table_data["headers"],
            rows=table_data["rows"],
            top=self.theme.LAYOUT["title_table_top"],
            height=self.theme.LAYOUT["title_table_height"]
        )
        # 3. 自動驗證
        self._validate(slide, content)
```

### 5.5 自動版面計算

每個 builder 知道：
- **自己佔用多少垂直空間**
- **下一個元素應該從哪裡開始**

```
Title (1.3-2.1) → 0.8"
↓
Content (2.3-X) → 根據內容計算 X
↓
如果 X > 6.85：警告「內容過多，建議分割成兩張」
```

---

## 6. Layer 4：風格主題（Style Themes）

### 6.1 Theme 抽象

```python
@dataclass
class Theme:
    name: str
    description: str
    
    # 顏色
    colors: Dict[str, RGBColor]
    
    # 字體
    fonts: Dict[str, str]  # {title, body, mono}
    
    # 字級
    font_sizes: Dict[str, int]  # {title, subtitle, body, code, callout}
    
    # 版面尺寸（inches）
    layout: Dict[str, float]
    
    # 裝飾元素
    decorations: Dict  # 頂部橘條、底部品牌等
```

### 6.2 內建主題

#### 6.2.1 `claude-orange`（從 pi-proj 移植）

```yaml
# themes/claude-orange.yaml
name: claude-orange
description: Claude Code Plugin 學習系列風格（橘+米白）

colors:
  primary: "#C75A1A"        # Claude 橘
  dark: "#2C2C2C"           # 深灰（主要文字）
  bg_cream: "#FAF8F3"       # 米白（背景）
  bg_gray: "#F3F0E9"        # 淺米（卡片背景）
  blue: "#3B82F6"           # 輔助藍
  green: "#16A34A"          # 強調綠
  red: "#DC2626"            # 警告紅
  white: "#FFFFFF"
  gray_text: "#6B6B6B"      # 次要文字
  code_bg: "#1E1E1E"        # 程式碼區塊背景
  code_fg: "#E6E6E6"        # 程式碼前景

fonts:
  title: "Calibri"
  body: "Calibri"
  mono: "Consolas"

font_sizes:
  cover_title: 54
  cover_subtitle: 22
  slide_title: 32
  slide_subtitle: 16
  body: 14
  code: 12
  callout: 13
  brand: 9

layout:
  # 簡報尺寸
  slide_width: 13.333
  slide_height: 7.5
  
  # 安全區域
  content_top: 1.3
  content_bottom: 7.0
  brand_y: 7.1
  
  # 標題列
  title_top: 0.3
  title_height: 0.7
  subtitle_top: 1.0
  subtitle_height: 0.4
  
  # 內邊距
  content_left: 0.5
  content_right_margin: 0.5
  column_gap: 0.13

decorations:
  top_accent_bar:
    enabled: true
    height: 0.15
    color: primary
  brand_text:
    left: "Claude Code Plugin 完整學習系列"
    right_template: "📖 來源：{source}"
```

#### 6.2.2 `minimal-bw`（示範第二個主題）

```yaml
name: minimal-bw
description: 黑白極簡風（學術/技術分享適用）

colors:
  primary: "#000000"
  dark: "#1A1A1A"
  bg_cream: "#FFFFFF"
  bg_gray: "#F5F5F5"
  # ... 其他灰階

fonts:
  title: "Helvetica"
  body: "Helvetica"
  mono: "Monaco"

font_sizes:
  cover_title: 48
  slide_title: 28
  # ... 略小一點
```

### 6.3 內建主題套件（v1.0）

| 主題名 | 描述 | 用途 |
|--------|------|------|
| `claude-orange` | Claude 橘+米白 | 預設，AI/開發工具 |
| `minimal-bw` | 黑白極簡 | 學術、技術分享 |
| `ocean-blue` | 海洋藍 | 企業/商務 |
| `forest-green` | 森林綠 | 永續/環保主題 |

### 6.4 自訂主題

使用者可用以下方式新增主題：

1. **複製 YAML 修改**：最快
2. **繼承後覆寫**：在 `lib/themes/custom.py` 定義 class
3. **CLI 互動生成**：`learn2deck theme new` 引導式建立

---

## 7. 主入口 CLI

### 7.1 指令架構

```bash
learn2deck <command> [options]

Commands:
  build     從內容產生 PPTX
  validate  驗證已產出的 PPTX
  theme     管理主題
  init      初始化新專案（建立範本）
  preview   產出預覽圖（PNG）

Global options:
  --config PATH      設定檔路徑
  --theme NAME       指定主題（預設 claude-orange）
  --verbose          詳細輸出
  --quiet            安靜模式
```

### 7.2 `build` 指令

```bash
# 從 Markdown 產生 PPTX
learn2deck build input.md -o output.pptx

# 指定主題
learn2deck build input.md -o output.pptx --theme ocean-blue

# 從 YAML 產生
learn2deck build outline.yaml -o output.pptx

# 批次產生
learn2deck build content/*.md -o decks/ --batch

# 自動驗證（產出後跑驗證）
learn2deck build input.md -o output.pptx --validate

# 嚴格模式（警告也視為錯誤）
learn2deck build input.md -o output.pptx --validate --strict
```

### 7.3 `validate` 指令

```bash
# 基本驗證
learn2deck validate output.pptx

# 詳細報告
learn2deck validate output.pptx --verbose

# JSON 輸出（CI/CD 用）
learn2deck validate output.pptx --json > report.json

# 只跑部分規則
learn2deck validate output.pptx --rules R1,R2,R5

# 自動修正（實驗性）
learn2deck validate output.pptx --fix
```

### 7.4 `theme` 指令

```bash
# 列出所有主題
learn2deck theme list

# 顯示主題詳情
learn2deck theme show claude-orange

# 從現有主題建立新主題
learn2deck theme new my-theme --base claude-orange

# 驗證自訂主題
learn2deck theme validate my-theme.yaml
```

### 7.5 `init` 指令

```bash
# 初始化新 deck 專案
learn2deck init my-deck/

# 會建立：
# my-deck/
# ├── outline.yaml       ← 編輯這個
# ├── content.md         ← 或這個
# ├── theme.yaml         ← 或自訂主題
# └── README.md          ← 指引
```

---

## 8. 程式碼組織（建議）

### 8.1 套件結構

```python
# learn2deck/                          ← 根套件
# ├── __init__.py
# ├── cli.py                           ← CLI 入口（typer）
# ├── config.py                        ← .env 載入（pydantic-settings）
# │
# ├── core/                            ← 核心資料結構
# │   ├── __init__.py
# │   ├── deck.py                      ← DeckSpec, SlideContent
# │   ├── theme.py                     ← Theme 抽象
# │   └── exceptions.py                ← 自訂例外
# │
# ├── parsers/                         ← 輸入解析
# │   ├── __init__.py
# │   ├── markdown.py                  ← Markdown 解析
# │   ├── yaml_outline.py              ← YAML 大綱解析
# │   └── frontmatter.py               ← YAML frontmatter
# │
# ├── builders/                        ← 投影片建構（Layer 3）
# │   ├── __init__.py
# │   ├── base.py                      ← BaseBuilder
# │   ├── cover.py
# │   ├── objectives.py
# │   ├── section_divider.py
# │   ├── title_content.py
# │   ├── title_table.py
# │   ├── title_code.py
# │   ├── two_column.py
# │   ├── grid_cards.py
# │   └── summary.py
# │
# ├── pptx_helpers/                    ← python-pptx 底層封装
# │   ├── __init__.py
# │   ├── shapes.py                    ← 從 pi-proj 移植 + 改進
# │   └── layout.py                    ← 版面計算工具
# │
# ├── themes/                          ← 內建主題（Layer 4）
# │   ├── __init__.py
# │   ├── claude_orange.yaml
# │   ├── minimal_bw.yaml
# │   ├── ocean_blue.yaml              ← v1.1
# │   └── forest_green.yaml            ← v1.1
# │
# ├── validators/                      ← 驗證規則（Layer 1）
# │   ├── __init__.py
# │   ├── base.py                      ← BaseValidator
# │   ├── code_capacity.py             ← R1
# │   ├── overlap.py                   ← R2
# │   ├── safe_zone.py                 ← R3, R4
# │   ├── file_format.py               ← R5
# │   ├── required.py                  ← R6
# │   ├── numbering.py                 ← R7
# │   ├── consistency.py               ← R8
# │   ├── arrows.py                    ← R9
# │   └── section_breaks.py            ← R10
# │
# ├── llm/                             ← LLM 整合（v1.1 新增）
# │   ├── __init__.py
# │   ├── base.py                      ← BaseLLMClient 介面
# │   ├── claude.py                    ← ClaudeClient（v1.1）
# │   ├── openai.py                    ← OpenAIClient（v2.0）
# │   ├── ollama.py                    ← OllamaClient（v2.0）
# │   ├── factory.py                   ← create_llm_client()
# │   └── prompts/                     ← ⭐ prompt 模板
# │       ├── __init__.py
# │       ├── base.py                  ← PromptLoader 抽象
# │       ├── claude.py                ← CLAUDE_PROMPTS（v1.1）
# │       ├── openai.py                ← OPENAI_PROMPTS（v2.0）
# │       └── ollama.py                ← OLLAMA_PROMPTS（v2.0）
# │
# └── agent/                           ← 高階 Agent 業務邏輯（v1.1 新增）
#     ├── __init__.py
#     ├── base.py                      ← BaseLLMAgent
#     ├── claude_agent.py              ← ClaudeAgent（v1.1）
#     ├── router.py                    ← FallbackAgent（v1.1）
#     └── tasks/                       ← 6 個 Agent 任務
#         ├── __init__.py
#         ├── classify_content.py      ← A1
#         ├── simplify_text.py         ← A2（v1.1）
#         ├── suggest_layout.py        ← A3（v1.1）
#         ├── recommend_theme.py       ← A4
#         ├── plan_outline.py          ← A5
#         └── review_quality.py        ← A6
```
```

### 8.2 安裝方式

```bash
# 從 PyPI（未來）
pip install learn2deck

# 從原始碼
git clone https://github.com/kcf7012/learn2deck
cd learn2deck
uv pip install -e .

# 安裝到 Claude Code skills 目錄
mkdir -p ~/.claude/skills/learn2deck
cp -r . ~/.claude/skills/learn2deck/
```

### 8.3 與 Claude Code Skill 系統整合

`SKILL.md` 範例：

```yaml
---
name: learn2deck
description: |
  從結構化 Markdown 或 YAML 大綱產生符合設計風格的 PPTX 簡報。
  Use when: 使用者要從 Markdown 教材、學習筆記、技術文件產生簡報，
  或要套用 Claude Plugin 學習系列的設計風格。
  Triggers: "產生簡報", "從 markdown 轉 pptx", "套用 Claude 風格",
  "make slides from this doc", "我要做簡報"
allowed-tools: Bash, Read, Write, Edit
model: claude-sonnet-4
---

# learn2deck

將結構化 Markdown 或 YAML 大綱轉換為符合設計風格的 PowerPoint 簡報。

## 快速使用
```bash
learn2deck build input.md -o output.pptx
learn2deck build input.md -o output.pptx --theme ocean-blue
```

## 輸入格式
... (更多內容)
```

---

## 9. 開發階段規劃

### 9.0 版本演進關係

> **核心原則**：**v1.1 包含 v1.0，v2.0 包含 v1.1**。每個新版都是**增量**，不是取代。
>
> ```
> v1.0 (純規則)          v1.1 (+Agent)              v2.0 (+多家LLM)
> ┌──────────────┐      ┌───────────────────┐      ┌────────────────────────┐
> │ 4 層架構      │      │ v1.0 全部          │      │ v1.1 全部              │
> │ 9 種版型      │  →   │ + BaseLLMAgent 介面 │  →   │ + BaseLLMClient 抽象   │
> │ 2 個主題      │      │ + ClaudeAgent      │      │ + OpenAIAgent          │
> │ 4 條驗證      │      │ + A2/A3 功能       │      │ + OllamaAgent          │
> │ 純本地，零成本 │      │ + .env 設定         │      │ + 跨 LLM 測試套件      │
> │              │      │ + --ai-assist opt-in│      │ + Fallback 鏈          │
> └──────────────┘      └───────────────────┘      └────────────────────────┘
>   4-6 週                +2 週                       +4 週
> ```

**向下相容原則**：
- v1.0 寫的所有 `_make_*.py` → v1.1 可直接用 `learn2deck build` 取代
- v1.1 設定 `.env` 但沒設 `ANTHROPIC_API_KEY` → 完全等同 v1.0 行為
- v2.0 沒裝 Ollama 但用 `ollama` provider → 友善錯誤訊息 + fallback 提示

---

### 9.1 v1.0 MVP（4-6 週）— 純規則版

**目標**：核心功能可用，能取代現有 8 個 `_make_*.py` 的 80% 工作

**範圍**：
- ✅ Layer 1: 4 條核心驗證規則（R1, R2, R3, R5）
- ✅ Layer 2: Markdown + YAML frontmatter 解析
- ✅ Layer 3: 9 種版型 builder
- ✅ Layer 4: 2 個內建主題（claude-orange + minimal-bw）
- ✅ CLI: build + validate + theme list
- ✅ 從現有 pi-proj 的 `_make_*.py` 移植並改寫
- ✅ 用現有 8 份 Markdown 重新產生 8 份 PPTX 驗證

**不做**：
- ❌ JSON 輸入
- ❌ 自動修正（--fix）
- ❌ 預覽圖（preview）
- ❌ 7 條進階驗證規則
- ❌ 互動式 theme 編輯
- ❌ **任何 LLM 整合**（這是 v1.1 才有的）

### 9.2 v1.1 增強（+2 週）— + Agent Layer

> **v1.1 = v1.0 全部功能 + Agent 整合**

**增量範圍**（不重做 v1.0 的部分）：
- ✅ **保留 v1.0 全部功能**（向下相容）
- ✅ **Layer 5: Agent Layer**（新增）
  - BaseLLMAgent 抽象介面
  - ClaudeAgent 實作（鎖定 Claude）
  - A2 文字精簡（code 框裝不下時自動修正）
  - A3 版型選擇（內容推斷時建議版型）
- ✅ **`.env` 設定系統**（pydantic-settings）
  - `ANTHROPIC_API_KEY`
  - `LEARN2DECK_LLM_PROVIDER=claude`（固定）
  - `LEARN2DECK_AI_MAX_COST=1.0`
- ✅ **CLI 新旗標**（全部 opt-in）
  - `--ai-assist` 啟用 A2 + A3
  - `--ai-tasks simplify,layout` 選擇性啟用
  - `--max-llm-cost 0.50` 成本控制
- ✅ **prompt 模板介面**（v1.1 只有 Claude 版本，v2.0 才擴充）
- ✅ **自動 fallback**：LLM 失敗時降級到純規則（確保產出不中斷）

**預設行為**（**極重要**）：
- ❎ 沒設 `ANTHROPIC_API_KEY` → 完全等同 v1.0，零成本
- ❎ 沒加 `--ai-assist` → 完全等同 v1.0，零成本
- ✅ 設了 `ANTHROPIC_API_KEY` + 加 `--ai-assist` → 才會呼叫 LLM

### 9.3 v2.0 完整版（+4 週）— + 多家 LLM 支援

> **v2.0 = v1.1 全部功能 + 多家 LLM 抽象**

**增量範圍**：
- ✅ **保留 v1.1 全部功能**
- ✅ **抽出 BaseLLMClient 介面**（更低層）
- ✅ **多家 LLM 支援**：
  - OpenAIClient（GPT-4o, GPT-4o-mini）
  - OllamaClient（Llama 3, Qwen, Mistral）
  - AzureOpenAIClient（企業用）
- ✅ **每家 LLM 有自己的 prompt 變體**
- ✅ **跨 LLM 測試套件**（N × M 組合）
- ✅ **Fallback 鏈**（primary → fallback）
- ✅ **模型分層**（fast/smart/smartest 不同模型配對）

**向下相容**：
- v1.1 的 `.env` 設定在 v2.0 仍可使用
- v1.1 沒呼叫 LLM 的指令在 v2.0 行為完全相同

### 9.4 測試策略

- **單元測試**：每個 builder / validator / parser 獨立測試
- **整合測試**：用 8 份現有 Markdown 重新產生 8 份 PPTX，比對版面
- **視覺測試**：開啟 PowerPoint 截圖比對
- **回歸測試**：版面修改不應破壞既有簡報

### 9.5 v1.1 詳細設計（4 個關鍵決策）

本節定下 v1.1 實作前的 4 個細節問題，避免日後回頭改動。

#### 決策 1：SKILL.md 觸發描述

**最終決定**：採用**双層觸發**策略，同時支援關鍵字與意圖。

**SKILL.md frontmatter 範本**（v1.1 實作時填入）：

```yaml
---
name: learn2deck
description: |
  從 Markdown 教材、技術文件、學習筆記產生符合設計風格的 PPTX 簡報。
  支援 Claude Plugin 學習系列的 claude-orange 預設風格，與可切換主題。
  
  Use this skill when:
  - 使用者要「產生簡報」、「轉成 PPTX」、「做投影片」
  - 有 Markdown 文件要「變成可演講的格式」
  - 要套用 Claude 橘色或其他預設設計風格
  - 要從 00-claude-code-plugins-series.md 這類教材自動生出簡報
  
  Do NOT use for:
  - 純文字報告輸出
  - Word/Google Docs 格式
  - 即時協作編輯
  - 含有複雜動畫/影片的簡報

allowed-tools: Bash, Read, Write, Edit, Glob
model: claude-sonnet-4-5
---

# learn2deck
...（其他內容見 §2.3）
```

**關鍵設計**：
- 「Use this skill when」列出 3-4 個明確的**動作動詞**（「產生」、「轉成」、「做」）
- 「Do NOT use for」**明確排除**誤觸發情境
- 避免描述太廣（如「幫我處理文件」會誤觸發）

**使用方式**：
- 使用者輸入：「幫我把這份 markdown 變成簡報」
- Claude 看到 description 匹配 → 自動載入 SKILL
- 載入後讀 SKILL.md 主體、references/ 取得詳情

#### 決策 2：prompt 模板的目錄位置

**最終決定**：放在 **`lib/llm/prompts/`**（低層，貼近 LLM 實作），而不是 `lib/agent/prompts/`。

**目錄結構**：

```
lib/
├── llm/                          ← 所有 LLM 相關
│   ├── __init__.py
│   ├── base.py                   ← BaseLLMClient 介面
│   ├── claude.py                 ← ClaudeClient 實作
│   ├── openai.py                 ← OpenAIClient 實作（v2.0）
│   ├── ollama.py                 ← OllamaClient 實作（v2.0）
│   ├── factory.py                ← create_llm_client()
│   └── prompts/                  ← ⭐ prompt 模板
│       ├── __init__.py
│       ├── base.py               ← PromptLoader 抽象
│       ├── claude.py             ← CLAUDE_PROMPTS
│       ├── openai.py             ← OPENAI_PROMPTS（v2.0）
│       └── ollama.py             ← OLLAMA_PROMPTS（v2.0）
├── agent/                        ← 高階業務邏輯
│   ├── __init__.py
│   ├── base.py                   ← BaseLLMAgent（高階介面）
│   ├── claude_agent.py           ← ClaudeAgent（v1.1）
│   ├── router.py                 ← FallbackAgent（v1.1）
│   └── tasks/                    ← 6 個 Agent 任務
│       ├── __init__.py
│       ├── classify_content.py   ← A1
│       ├── simplify_text.py      ← A2
│       ├── suggest_layout.py     ← A3
│       ├── recommend_theme.py    ← A4
│       ├── plan_outline.py       ← A5
│       └── review_quality.py     ← A6
```

**理由**：
1. **職責分離**：`llm/` 是「怎麼跟 LLM 溝通」，`agent/` 是「怎麼用 LLM 解決問題」
2. **易擴展**：v2.0 加新 LLM 只動 `llm/` 與 `llm/prompts/`，`agent/` 不變
3. **prompt 是 LLM 實作的一部分**：不同 LLM 需要不同 prompt，這是 LLM client 的責任
4. **符合 DDD**：低層（llm）不知道業務，高層（agent）可以組合低層

**v1.1 只需建立**：
- `lib/llm/base.py`、`lib/llm/claude.py`、`lib/llm/factory.py`
- `lib/llm/prompts/base.py`、`lib/llm/prompts/claude.py`
- `lib/agent/base.py`、`lib/agent/claude_agent.py`、`lib/agent/router.py`
- `lib/agent/tasks/simplify_text.py`、`lib/agent/tasks/suggest_layout.py`

#### 決策 3：A2/A3 的 prompt 設計

**最終決定**：採用**任務隔離 + 結構化輸出 + 評分重試**三層保障。

##### 3.1 prompt 設計原則

每個 prompt 都遵守這個模板：

```python
TASK_TEMPLATE = """
[角色] 你是 {role}。
[背景] {context}
[任務] {task_description}
[輸入] {input_data}
[輸出格式] {output_format}
[限制] {constraints}
[例項] {example}
"""
```

**v1.1 只寫 Claude 優化版本**（v2.0 才加其他 LLM 版本）：

```python
# lib/llm/prompts/claude.py

CLAUDE_PROMPTS = {
    # === A2: 文字精簡 ===
    "simplify_text_system": """你是簡報內容精簡助手。
你擅長在不損失關鍵資訊的前提下，縮短技術文字長度。
你只回傳精簡後的內容，不加任何說明、引用、解釋。""",

    "simplify_text_user": """【任務】
將以下內容精簡到 {target_lines} 行以內。

【保留規則】
1. 所有關鍵技術資訊（API 名稱、版本號、參數名）
2. 所有可執行的程式碼語意（可重排、但不能改語意）
3. 所有 `黑體`、`反引號` 標記的關鍵詞

【移除規則】
1. 冗餘的修飾語（「實際上」、「一般來說」、「具體而言」等）
2. 重複的說明（同一概念換句話說兩次）
3. 範例中的多餘空行
4. 「如以下」、「如下所示」等引導句（直接進內容）

【輸入內容】
```
{text}
```

【輸出】
請只回傳精簡後的內容，不要任何前綴、解釋、引言。""",

    # === A3: 版型選擇 ===
    "suggest_layout_system": """你是簡報版型顧問。
你根據 Markdown 章節的語意與結構，選擇最適合的投影片版型。
你只回傳一個版型名稱，不加說明。""",

    "suggest_layout_user": """【任務】
根據以下 Markdown 章節內容，選擇最適合的投影片版型。

【可選版型】
{options}

【版型說明】
- cover: 封面（標題 + 副標題）
- objectives: 學習目標（多個項目以圖示呈現）
- section: 章節分隔（大編號 + 標題）
- title_content: 標題 + 純文字 / bullet
- title_table: 標題 + 表格
- title_code: 標題 + 程式碼區塊
- two_column: 左右雙欄對比
- grid_cards: 多個網格卡片
- callout: 單一提示框
- summary: 重點回顧

【輸入章節】
{content}

【輸出】
請只回傳一個版型名稱（例如：title_table），不加任何說明。""",

    # === A2 評分（重試用） ===
    "evaluate_simplify_system": """你是簡報內容品質審查員。
你評估「精簡後內容」的品質，給 0-1 的分數。""",

    "evaluate_simplify_user": """【任務】
評估以下「精簡後內容」的品質。

【評分標準】
1.0: 完美。保留所有關鍵資訊，簡潔有力。
0.8: 良好。資訊完整，可能多 1-2 行。
0.6: 可接受。有遺漏但不嚴重。
0.4: 差。遺漏關鍵資訊。
0.2: 極差。改變原意或變難讀。
0.0: 完全失敗。

【原始內容】
```
{original}
```

【精簡後內容】
```
{simplified}
```

【目標行數】{target_lines} 行
【實際行數】{actual_lines} 行

【輸出格式】
{{"score": 0.X, "reason": "簡短說明"}}""",
}
```

##### 3.2 結構化輸出（A3 重點）

A3 推薦的版型有 10 個選項，要保證 LLM 只回 1 個，用**「多選一」** prompt 技巧：

```python
async def suggest_layout(self, content: str) -> str:
    options = ["cover", "objectives", "section", "title_content",
               "title_table", "title_code", "two_column", "grid_cards",
               "callout", "summary"]
    options_str = "\n".join(f"- {opt}" for opt in options)
    
    prompt = CLAUDE_PROMPTS["suggest_layout_user"].format(
        options=options_str,
        content=content[:2000]  # 限長避免超 token
    )
    result = await self.client.complete(
        system=CLAUDE_PROMPTS["suggest_layout_system"],
        user=prompt,
        max_tokens=20  # 只要 1 個詞
    )
    
    # 驗證：確保回傳是合法版型
    result = result.strip().lower()
    if result in options:
        return result
    # 失敗時 fallback
    return self._fallback_classify(content)
```

##### 3.3 評分重試（A2 重點）

```python
async def simplify_text(self, text: str, target_lines: int) -> str:
    for attempt in range(3):  # 最多重試 3 次
        # 1. 精簡
        prompt = CLAUDE_PROMPTS["simplify_text_user"].format(
            target_lines=target_lines,
            text=text
        )
        simplified = await self.client.complete(
            system=CLAUDE_PROMPTS["simplify_text_system"],
            user=prompt
        )
        
        # 2. 評分
        actual_lines = simplified.count("\n") + 1
        score_prompt = CLAUDE_PROMPTS["evaluate_simplify_user"].format(
            original=text,
            simplified=simplified,
            target_lines=target_lines,
            actual_lines=actual_lines
        )
        score_result = await self.client.complete(
            system=CLAUDE_PROMPTS["evaluate_simplify_system"],
            user=score_prompt
        )
        score = self._parse_score(score_result)
        
        # 3. 通過門檻就回傳
        if score >= 0.7:
            return simplified
        
        # 4. 不夠好，把上次的結果丟回去重試
        log.warning(f"Simplify attempt {attempt+1} score={score:.2f}, retrying")
    
    return simplified  # 最後一次不管分數都回傳
```

##### 3.4 成本控制

```python
# v1.1 lib/agent/claude_agent.py
class ClaudeAgent(BaseLLMAgent):
    def __init__(self, config: LLMConfig):
        self.client = ClaudeClient(api_key=config.anthropic_api_key)
        self.model = config.claude_model
        self.max_cost = config.max_cost_usd
        self.cost_used = 0.0
    
    async def _tracked_call(self, system, user, max_tokens=2000):
        # 估算成本（Claude Sonnet: $3/M input, $15/M output）
        est_cost = (len(system) + len(user)) / 1_000_000 * 3.0 \
                 + max_tokens / 1_000_000 * 15.0
        
        if self.cost_used + est_cost > self.max_cost:
            raise CostLimitExceeded(
                f"Cost limit ${self.max_cost} reached. "
                f"Used: ${self.cost_used:.4f}, est: ${est_cost:.4f}"
            )
        
        result = await self.client.complete(system, user, max_tokens)
        self.cost_used += est_cost  # 簡化估算
        return result
```

#### 決策 4：fallback 失敗時的 UX

**最終決定**：採用**「三層降級 + 明確告知」**策略。

##### 4.1 三層降級路徑

```
Layer 1: AI 增強成功 → 使用 LLM 結果
   ↓ (LLM 失敗)
Layer 2: 自動降級到純規則 → 用備用啟發式
   ↓ (規則也不適用)
Layer 3: 明確錯誤 + 建議 → 中止並提示使用者手動處理
```

##### 4.2 實作

```python
# lib/agent/router.py
class FallbackAgent(BaseLLMAgent):
    """三層降級路由器"""
    
    def __init__(
        self,
        primary: BaseLLMAgent,        # ClaudeAgent
        fallback_rule: Callable,      # 純規則的 fallback function
        config: LLMConfig
    ):
        self.primary = primary
        self.fallback_rule = fallback_rule
        self.verbose = config.verbose
    
    async def simplify_text(self, text: str, target_lines: int) -> SimplifyResult:
        # Layer 1: 嘗試 AI
        try:
            if self.primary.has_budget():
                result = await self.primary.simplify_text(text, target_lines)
                return SimplifyResult(
                    content=result,
                    source="ai",
                    confidence=0.85
                )
        except (RateLimitError, APIError, CostLimitExceeded) as e:
            if self.verbose:
                log.warning(f"⚠️  AI 增強失敗：{e}，降級到純規則")
        
        # Layer 2: 純規則 fallback
        try:
            result = self.fallback_rule.simplify_text(text, target_lines)
            return SimplifyResult(
                content=result,
                source="rule",
                confidence=0.60,  # 規則品質較低
                warning="AI 增強未啟用，使用啟發式精簡"
            )
        except Exception as e:
            if self.verbose:
                log.error(f"❌ 純規則 fallback 也失敗：{e}")
        
        # Layer 3: 明確錯誤
        return SimplifyResult(
            content=text,  # 回傳原內容
            source="none",
            confidence=0.0,
            error="AI 與規則都無法處理此內容。建議：\n"
                  "1. 手動編輯內容\n"
                  "2. 拆分為多張投影片\n"
                  "3. 設定 ANTHROPIC_API_KEY 啟用 AI 增強"
        )
```

##### 4.3 使用者看到的訊息範例

**情境 A：AI 成功**
```
✓ 簡報產生完成：output.pptx (35 張)
  - AI 增強：3 處文字精簡 (A2)、1 處版型推薦 (A3)
  - 預估成本：$0.04
```

**情境 B：AI 失敗，降級到規則**
```
✓ 簡報產生完成：output.pptx (35 張)
  ⚠️  注意：AI 增強未啟用/失敗
    - 原因：ANTHROPIC_API_KEY 未設定（或 API 額度用盡）
    - 結果：2 處 code 框未自動精簡（仍裝不下，建議手動調整）
    - 解法：設定 .env 中的 ANTHROPIC_API_KEY 後重跑
```

**情境 C：完全失敗**
```
✗ 簡報產生失敗：exit code 1

錯誤詳情：
  Slide 12 (Plugin 完整目錄結構)
    - code 框 36 行無法裝入 5.0" 高度
    - AI 增強失敗：API 額度用盡
    - 規則 fallback 失敗：啟發式無法處理複雜目錄樹

建議：
  1. 編輯 03-plugins-reference.md，縮短目錄結構章節
  2. 或設定 ANTHROPIC_API_KEY 啟用 AI 精簡
  3. 或將該章節拆分為多張投影片
```

##### 4.4 退出碼設計

| 情境 | exit code | 含義 |
|------|----------|------|
| 全部成功 | 0 | 完美 |
| 成功但有警告 | 0 | 可用但有改善空間 |
| 部分成功（部分 slide fallback） | 0 | 仍產出 PPTX，附警告 |
| 完全失敗（無法產出 PPTX） | 1 | 使用者需介入 |
| 使用者中斷（Ctrl+C） | 130 | 標準中斷碼 |

##### 4.5 日誌策略

```python
# v1.1 lib/agent/router.py
import logging

class FallbackAgent(BaseLLMAgent):
    async def _log_fallback(self, level: str, message: str, details: dict):
        """統一日誌格式"""
        log.log(
            getattr(logging, level.upper()),
            f"[{level}] {message}",
            extra=details
        )
        # 同步輸出到 stderr（讓使用者即時看到）
        if self.config.verbose:
            icon = {"info": "ℹ️", "warning": "⚠️", "error": "❌"}[level]
            print(f"{icon} {message}", file=sys.stderr)
```

#### 決策總結表

| # | 問題 | 最終決定 | 為什麼 |
|---|------|---------|--------|
| 1 | SKILL.md 觸發描述 | 双層觸發：動作動詞 + 明確排除 | 避免誤觸發、覆蓋率高 |
| 2 | prompt 目錄位置 | `lib/llm/prompts/` | 職責分離、易擴展 |
| 3 | A2/A3 prompt 設計 | 任務隔離 + 結構化輸出 + 評分重試 | 品質穩定、可除錯 |
| 4 | fallback UX | 三層降級 + 明確告知 | 使用者清楚狀況、不中斷產出 |

#### 與其他章節的關係

- 決策 1 → 影響 §2.3 (SKILL.md 範本填入)
- 決策 2 → 影響 §8.1 (套件結構) — 已反映在新增的目錄
- 決策 3 → 影響 §9.2 v1.1 範圍 — 需實作評分重試機制
- 決策 4 → 影響 §7.2 build 指令 — exit code 與錯誤訊息

---

## 10. 與現有 pi-proj 的關係

### 10.1 短期（v1.0 開發期間）

- **不**立即替換 pi-proj 的 8 份 `_make_*.py`
- 在 `pi-proj/skills-experiment/` 建立實驗性 skill
- 確認能產出**同等品質**的 PPTX 才考慮替換

### 10.2 中期（v1.1 之後）

- 把 8 份 `_make_*.py` 改為**結構化 Markdown + `learn2deck build` 一行指令**
- 大幅縮減 1000+ 行的 Python 程式碼
- HANDOFF.md 簡化為「如何用 learn2deck」

### 10.3 長期（v2.0+）

- learn2deck 成為獨立開源專案
- 從 URL 到簡報的完整 pipeline
- 社群可貢獻主題與 builder

---

## 11. 風險與緩解

| 風險 | 嚴重度 | 緩解策略 |
|------|--------|---------|
| Markdown 推斷不準確 | 中 | 信心度標記 + CLI 互動修正 |
| 風格擴展破壞既有版面 | 中 | 完整的視覺回歸測試 |
| 從 1000 行重寫成 skill 後版面跑掉 | 高 | **必須** 8 份簡報逐一比對 |
| python-pptx 版本不相容 | 低 | 固定 1.0.2 + 測試覆蓋 |
| 開發時間超過預期 | 中 | MVP 先求有，後續迭代 |

### 11.1 最重要的驗證標準

> **用 learn2deck 重新產出的 8 份 PPTX，必須在版面、內容、視覺上與現有版本無法區分。**

任何會破壞這個標準的變更都不接受。

---

## 12. 開放問題（請在 review 時回答）

### 12.1 已解決（v1.0 設計階段已定下）

1. ✅ **技能包名稱**：`learn2deck`（見 §2.1）
2. ✅ **v1.1 一定包含 v1.0**（見 §9.0）
3. ✅ **LLM 策略**：選項 B（工具輔助）+ Q3-A（Claude）（見 §9.5 決策 1-4）
4. ✅ **SKILL.md 觸發描述**：双層觸發設計（見 §9.5 決策 1）
5. ✅ **prompt 目錄位置**：`lib/llm/prompts/`（見 §9.5 決策 2）
6. ✅ **A2/A3 prompt 設計**：任務隔離 + 結構化輸出 + 評分重試（見 §9.5 決策 3）
7. ✅ **fallback UX**：三層降級 + 明確告知（見 §9.5 決策 4）

### 12.2 待 review 的問題

1. **優先 MVP 範圍**：v1.0 的 4 個 layer 都要做嗎？還是先聚焦某 2 個？
2. **Markdown 推斷策略**：要互動式（CLI 問）還是全自動（信心中等就自動推斷）？
3. **風格數量**：v1.0 內建 2 個主題是否足夠？還是要先有 4 個？
4. **與 pi-proj 整合時機**：MVP 完成後立即整合？還是並行維護一段時間？
5. **測試投入**：整合測試要全 8 份比對嗎？還是用 1-2 份代表即可？
6. **發佈策略**：純內部使用？還是要發到 PyPI？license 用什麼？

---

## 附錄 A：現有資源盤點

| 資源 | 位置 | 用途 |
|------|------|------|
| `_pptx_helpers.py` | pi-proj/ | 移植為 `pptx_helpers/shapes.py` |
| 8 份 `_make_XX_*.py` | pi-proj/ | 改寫為 `examples/` 與測試案例 |
| 8 份 `.md` | pi-proj/ | 作為測試輸入 |
| 8 份 `.pptx` | pi-proj/ | 作為回歸測試基準 |
| `HANDOFF.md §4.3` | pi-proj/ | 設計規則吸收到 `style-guide.md` |
| 驗證腳本 | pi-proj/ (ad-hoc) | 改寫為 `validators/` |

## 附錄 B：參考資料

- [Claude Code Skills 官方文件](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview)
- [python-pptx 文件](https://python-pptx.readthedocs.io/)
- pi-proj 倉庫：[kcf7012/pi-proj](https://github.com/kcf7012/pi-proj)

## 附錄 C：文件變更紀錄

| 版本 | 日期 | 變更 |
|------|------|------|
| 1.0 | 2026/08 | 初版草案 |
