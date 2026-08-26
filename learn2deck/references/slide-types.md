# 9 種 Slide Type 速查

> **權威來源**：`learn2deck/lib/core/deck.py` (`SlideType` enum)
> **對應**：`docs/learn2deck-spec.md` §4.1

## 1. 版型總覽

learn2deck 定義 **10 種 SlideType**（注意：HANDOFF 與 spec 寫「9 種」是因為 CALLOUT 是後加的特例）：

| Type | enum 值 | 用途 | 何時使用 |
|:-----|:--------|:-----|:---------|
| `cover` | `cover` | 封面 | 簡報第 1 張 |
| `objectives` | `objectives` | 學習目標 | 章節開頭，列出「本章你會學到」 |
| `section` | `section` | 章節分隔 | Part X 開始的大標頁 |
| `summary` | `summary` | 重點回顧 | 簡報末段或 Part 結尾 |
| `callout` | `callout` | 純提示框 | 強調單一重點（少用） |
| `title_content` | `title_content` | 標題+文字 | 預設版型：bullet 列表或段落 |
| `title_table` | `title_table` | 標題+表格 | 對照表、規格、欄位說明 |
| `title_code` | `title_code` | 標題+程式碼 | 程式碼範例 |
| `two_column` | `two_column` | 雙欄對比 | A vs B、優缺點對照 |
| `grid_cards` | `grid_cards` | 網格卡片 | 3-6 個等權重項目 |

> **特殊頁規則**：`cover` 與 `section_divider` 必須透過 `build_full_deck()` 建立，因為它們需要 `Presentation` 物件

## 2. 各版型 body schema

### 2.1 `cover` — 封面

```yaml
type: cover
title: Plugin 開發介紹
subtitle: 從零開始建立 Claude Code Plugin  # optional
body:
  tag: "範例 · #demo"   # optional，左下角小標籤
```

### 2.2 `objectives` — 學習目標

```yaml
type: objectives
title: 本章你會學到   # optional，預設 "本章你會學到"
body:
  items:
    - {icon: "🎯", title: "概念", desc: "核心觀念"}
    - {icon: "🛠", title: "實作", desc: "動手做"}
```

> 結構等同 `grid_cards`，但版面與配色不同

### 2.3 `section` — 章節分隔

```yaml
type: section
title: Part 1: 基礎概念   # 完整大標題
body:
  section_num: "Part 1"          # 顯示用大編號
  section_subtitle: "..."        # optional 副標
```

### 2.4 `summary` — 重點回顧

```yaml
type: summary
title: 下一步
subtitle: 建立你的第一個 Plugin   # optional
body:
  key_points:
    - "建立 .claude-plugin/plugin.json"
    - "翻完 02-plugins.md"
  next_steps:                       # optional
    - "建立 hello-world plugin"
```

### 2.5 `callout` — 純提示框

```yaml
type: callout
title: 注意   # optional
body:
  text: "這是重要提醒..."
  icon: "💡"                      # optional
  style: "info" | "warning" | "success"  # optional, default "info"
```

> 目前較少使用，建議直接用 `title_content` 表達

### 2.6 `title_content` — 標題+文字（最常用）

```yaml
type: title_content
title: 為什麼需要 Plugin
subtitle: 補充說明   # optional
body:
  items:                # 選一個：items 或 text
    - "bullet 1"
    - "bullet 2"
    - "bullet 3"
  # 或
  text: "純文字段落，會自動換行"
```

### 2.7 `title_table` — 標題+表格

```yaml
type: title_table
title: Plugin vs 獨立配置
subtitle: 兩種擴展方式
body:
  headers: ["面向", "獨立配置", "Plugin"]
  rows:
    - ["Skill 名稱", "/hello", "/plugin-name:hello"]
    - ["可用範圍", "僅當前專案", "跨專案、跨團隊"]
    - ["版本管理", "無", "semver 或 git SHA"]
```

> 表格塞不下時自動降級字級（11 → 10 → 9 pt）

### 2.8 `title_code` — 標題+程式碼

```yaml
type: title_code
title: 建立 Plugin
subtitle: hello-world 範例
body:
  code: |
    mkdir hello-plugin
    cd hello-plugin
    mkdir .claude-plugin
    echo '{"name":"hello-plugin"}' > .claude-plugin/plugin.json
  language: "bash"   # optional，僅用於語法標記
```

> 行數過多時自動降級字級（12 → 11 → 10 → 9 → 8 pt）

### 2.9 `two_column` — 雙欄對比

```yaml
type: two_column
title: Plugin 優缺點
body:
  left:
    title: 優點
    items: ["跨專案共用", "版本管理"]
    color: "green"     # optional，theme color name
  right:
    title: 缺點
    items: ["需要維護", "學習成本"]
    color: "red"       # optional
```

### 2.10 `grid_cards` — 網格卡片

```yaml
type: grid_cards
title: Plugin 的 3 種元件
body:
  cols: 3   # optional, default 3（自動判斷也可）
  items:
    - {icon: "📚", title: "Skills",  desc: "可重用的知識庫"}
    - {icon: "🤖", title: "Agents",  desc: "隔離的子任務"}
    - {icon: "🪝", title: "Hooks",   desc: "事件驅動腳本"}
```

> items 數建議 3-6 個（多了會塞不下）

## 3. Markdown 對應規則

`learn2deck/parsers/markdown.py` 會把 .md 自動轉成版型：

| Markdown 模式 | SlideType | 範例 |
|:--------------|:----------|:-----|
| H1（首張） | `cover` | `# Plugin 開發介紹` |
| `## Part X: 標題` | `section` | `## Part 1: 基礎概念` |
| `## 標題` + table | `title_table` | `## Plugin vs 獨立配置` 後接 markdown table |
| `## 標題` + ```code``` | `title_code` | `## 安裝步驟` 後接 fenced code block |
| `## 標題` + 3+ ### H3 | `grid_cards` | H2 後接 3+ 個 H3 |
| `## 下一步` / `## 總結` | `summary` | 關鍵字匹配 |
| `## 標題` + bullets | `title_content` | 預設 |
| 第一張 H2 之後自動 | `objectives` | 自動插入（可關閉） |

## 4. 版型選擇決策樹

```
要展示什麼？
│
├─ 簡報標題 → cover
├─ 學習目標清單 → objectives
├─ Part X 章節 → section_divider
│
├─ 單一重點提醒 → callout（少用）
├─ bullet 列表 → title_content
├─ 純文字段落 → title_content (text)
│
├─ 結構化資料 → title_table
├─ 程式碼範例 → title_code
│
├─ 兩個選項對比 → two_column
└─ 多個等權重項目（3-6 個） → grid_cards

最後一頁總結 → summary
```

## 5. 各版型的常見錯誤

### 5.1 `title_content`

- ❌ items 太多（>8 個會塞不下）
- ❌ 文字太長沒換行
- ✅ 控制在 5-7 個 bullet，每個 ≤ 2 行

### 5.2 `title_table`

- ❌ 欄位數不一致（會 `list index out of range`）
- ❌ row > 10 個（塞不下）
- ❌ cell 內放 `|` 沒跳脫為 `\|`
- ✅ row ≤ 7、cell 文字 ≤ 30 字

### 5.3 `title_code`

- ❌ code 區塊有大量空行（浪費空間）
- ❌ 程式碼太長（>30 行）會降級到 8pt
- ✅ 精簡到 ≤ 20 行

### 5.4 `two_column`

- ❌ 左右內容長度差太多（會不平衡）
- ❌ icon 數量不一致
- ✅ 兩側 items 數量接近

### 5.5 `grid_cards`

- ❌ items 太多（>6 個）會擠壓
- ❌ desc 太長（>50 字）會跑出框
- ✅ 3-4 個最理想，desc ≤ 30 字

## 6. 版型速查表（給 Claude 用）

```python
# 從 core.deck 載入
from learn2deck.lib.core.deck import SlideType

# 列出所有版型
SlideType.values()  # ['cover', 'objectives', 'section', ...]

# 字串轉 enum
slide_type = SlideType("title_content")
```

## 7. 參考資源

- enum 定義：`learn2deck/lib/core/deck.py`
- builder 實作：`learn2deck/lib/builders/`
- 解析器：`learn2deck/lib/parsers/markdown.py`
- 規格書：`docs/learn2deck-spec.md` §4.1
