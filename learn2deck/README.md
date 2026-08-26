# learn2deck

> 純規則版的 Claude Code Plugin → PPTX 轉換器

`learn2deck` 是一個 Python 套件，把 Markdown 教材轉成視覺一致的 PPTX 簡報。
適用於 Claude Code Plugin 文件、學習教材、技術簡報。

## 特色

- 🎨 **9 種版型**：cover、section divider、grid cards、title table、title code 等
- 📐 **設計系統**：claude-orange 主題（橘色裝飾條、米白背景、Calibri 字體）
- ⚡ **自動推斷**：從 markdown 章節自動判斷 slide_type
- ✅ **4 條驗證規則**：R1 code 容量、R2 重疊、R3 安全區、R5 檔案格式
- 🛠️ **CLI**：4 個指令（build / validate / theme / init）
- 📊 **277/277 slides 對齊**：與原始 _make_XX.py 腳本產出的 .pptx 完全對齊

## 安裝

```bash
pip install -e .
```

或在開發模式：

```bash
cd learn2deck
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## 快速開始

### 1. 建立簡報

```bash
learn2deck build input.md -o output.pptx
```

### 2. 驗證輸出

```bash
learn2deck validate output.pptx
```

### 3. 列出可用主題

```bash
learn2deck theme list
```

### 4. 建立範本專案

```bash
learn2deck init my-project
cd my-project
```

## Markdown 語法對應

每個 H2 章節自動產生 1 張 slide，slide_type 由內容推斷：

| Markdown 結構 | Slide Type |
|:--------------|:-----------|
| `# H1` + 第一個 H2 | `cover`（自動插入）|
| `## Part X: 標題` | `section_divider` |
| `## 標題` + 表格 | `title_table` |
| `## 標題` + ```code block``` | `title_code` |
| `## 標題` + 3+ 個 `### H3` | `grid_cards` |
| `## 標題` + ✅/❌ | `two_column` |
| `## 下一步` | `summary` |
| `## 標題` + bullets | `title_content`（預設）|

### 範例

```markdown
## Part 1: 基礎概念

理解 Skill 是什麼

## 什麼是 Skill？

Skill 是一個 SKILL.md 檔案

### Skills

可重用的知識庫

### Agents

隔離的子任務

### Hooks

事件驅動腳本
```

會產生：
- 1 張 `section_divider`（Part 1）
- 1 張 `title_content`（什麼是 Skill？）
- 1 張 `grid_cards`（3 個 H3 → 3 個卡片）

## 完整範例

8 份 .md 已經全部對齊：

| 檔案 | Slides | 對齊狀態 |
|:-----|-------:|:---------|
| 00-claude-code-plugins-series.md | 30 | ✅ |
| 01-plugin-marketplaces.md | 35 | ✅ |
| 02-plugins.md | 25 | ✅ |
| 03-plugins-reference.md | 45 | ✅ |
| 04-skills.md | 40 | ✅ |
| 05-subagents.md | 30 | ✅ |
| 06-hooks.md | 50 | ✅ |
| 07-discover-plugins.md | 22 | ✅ |

## 開發

### 執行測試

```bash
pytest tests/
```

### 結構

```
learn2deck/
├── learn2deck/
│   ├── cli.py
│   └── lib/
│       ├── core/        # 資料結構
│       ├── pptx_helpers/ # 低階 helper
│       ├── themes/       # 主題
│       ├── builders/     # 9 種 builder
│       ├── parsers/      # markdown → DeckSpec
│       └── validators/   # 4 條驗證規則
├── tests/                # 233 個單元測試
└── tools/                # Phase 9 視覺驗證工具
```

## 文件

- [HANDOFF.md](./HANDOFF.md) — 接手者完整導引
- [MD_RESTRUCTURING_GUIDE.md](./MD_RESTRUCTURING_GUIDE.md) — 把 .md 改寫成投影片大綱的指南
- [examples/](./examples/) — 範本專案
- [tools/](./tools/) — 視覺驗證工具（轉 PNG、HTML 報告）

## 授權

整理自 Claude Code 官方文件 · 繁體中文教學用途
