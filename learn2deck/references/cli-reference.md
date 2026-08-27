# CLI 完整參考

> **權威來源**：`learn2deck/cli.py`
> **底層**：[typer](https://typer.tiangolo.com/) + [rich](https://rich.readthedocs.io/)

## 全域語法

```bash
learn2deck [COMMAND] [OPTIONS] [ARGS]
```

支援的指令：
- `build` — 從 .md / .yaml 產生 PPTX
- `validate` — 驗證已產出的 PPTX
- `theme` — 主題管理（list/show/new/validate）
- `init` — 初始化新 deck 專案
- `version` — 顯示版本

```bash
learn2deck --help              # 主說明
learn2deck <command> --help    # 各指令說明
learn2deck --version           # 版本資訊
```

## 1. `learn2deck build`

從 Markdown 或 YAML 產生 PPTX 簡報。

### 語法

```bash
learn2deck build <INPUT> -o <OUTPUT> [OPTIONS]
```

### 參數

| 參數 | 必填 | 說明 |
|:-----|:----:|:-----|
| `INPUT` | ✅ | 輸入的 .md 或 .yaml 檔案路徑 |
| `-o, --output` | ✅ | 輸出的 .pptx 檔案路徑 |
| `-t, --theme` | ❌ | 主題名稱（預設 `claude-orange`） |
| `--validate` | ❌ | 產出後自動跑驗證（R1-R5） |
| `--strict` | ❌ | 嚴格模式（警告也視為錯誤，exit code 1） |
| `-q, --quiet` | ❌ | 安靜模式（不輸出進度） |

### 範例

```bash
# 基本
learn2deck build input.md -o output.pptx

# 指定主題
learn2deck build input.md -o output.pptx --theme minimal-bw

# 自動驗證
learn2deck build input.md -o output.pptx --validate

# 嚴格模式（CI/CD）
learn2deck build input.md -o output.pptx --validate --strict

# 批次處理（無輸出）
for md in *.md; do
  learn2deck build "$md" -o "/tmp/new_${md%.md}.pptx" -q
done
```

### Exit Code

| 情境 | exit code |
|:-----|:----------|
| 成功 | 0 |
| 輸入檔不存在 | 1 |
| 解析失敗 | 1 |
| 產出失敗 | 1 |
| 驗證有 error | 1 |
| `--strict` + 有 warning | 1 |

### 輸出格式

```
📄 解析 input.md...
✓ 解析成功：30 張投影片
   主題：claude-orange
   版型：title_content:18, title_table:8, grid_cards:3, summary:1
🎨 產生 output.pptx...
✅ 簡報產生完成：output.pptx (123,456 bytes, 30 slides)

🔍 驗證中...
✨ No issues found
```

## 2. `learn2deck validate`

驗證已產出的 PPTX 簡報。

### 語法

```bash
learn2deck validate <PPTX> [OPTIONS]
```

### 參數

| 參數 | 必填 | 說明 |
|:-----|:----:|:-----|
| `PPTX` | ✅ | 要驗證的 .pptx 檔案路徑 |
| `-r, --rules` | ❌ | 指定規則（逗號分隔，如 `R1,R2,R5`）。預設全部 |
| `--strict` | ❌ | 嚴格模式 |
| `--json` | ❌ | 以 JSON 格式輸出（CI/CD 用） |
| `-q, --quiet` | ❌ | 安靜模式（只輸出最終結果） |

### 範例

```bash
# 基本驗證
learn2deck validate output.pptx

# 只驗證特定規則
learn2deck validate output.pptx --rules R1,R5

# 嚴格模式
learn2deck validate output.pptx --strict

# JSON 輸出（給 CI/CD）
learn2deck validate output.pptx --json > report.json

# 安靜模式（只回傳 exit code）
learn2deck validate output.pptx -q && echo "PASS" || echo "FAIL"
```

### 輸出格式（人類可讀）

```
🔍 驗證 output.pptx
──────────────────────────────────────────────────
✓ R5: PPTX 格式正確
✓ R1: Code 框容量 OK（0 張裝不下）
⚠ R2: 元素重疊（2 個 warning）
⚠ R3: 內容超出安全區（1 個 warning）
──────────────────────────────────────────────────
✨ No errors, 3 warnings
```

### 輸出格式（JSON）

```json
{
  "passed": true,
  "total_issues": 3,
  "errors": 0,
  "warnings": 3,
  "issues": [
    {
      "rule": "R2",
      "severity": "warning",
      "slide_num": 5,
      "message": "元素重疊：...",
      "details": {...}
    }
  ]
}
```

## 3. `learn2deck theme`

管理主題（內建 + 自訂）。

### 3.1 `learn2deck theme list`

列出所有可用主題。

```bash
learn2deck theme list
```

輸出：

```
              🎨 可用主題
┌────────────────┬──────────────────────┐
│ 名稱            │ 說明                  │
├────────────────┼──────────────────────┤
│ claude-orange  │ Claude 品牌橘 + 米白    │
│ minimal-bw     │ 極簡黑白風格            │
└────────────────┴──────────────────────┘
```

### 3.2 `learn2deck theme show <NAME>`

顯示主題詳細資訊（顏色/字體/字級/版面）。

```bash
learn2deck theme show claude-orange
```

輸出：

```
🎨 claude-orange
   說明：Claude 品牌橘 + 米白背景

   顏色 (11)：
     • primary: #C75A1A
     • bg_cream: #FAF8F3
     ...

   字體：
     • title: Calibri
     • body: Calibri
     • code: Consolas

   字級：
     • cover_title: 44pt
     ...

   版面：
     • content_top: 1.3"
     ...
```

### 3.3 `learn2deck theme new <NAME>`

從現有主題複製建立新主題。

```bash
# 基於 claude-orange 建立 my-theme（輸出到 themes/my-theme.yaml）
learn2deck theme new my-theme --base claude-orange

# 自訂輸出路徑
learn2deck theme new my-theme --base minimal-bw -o ~/my-themes/my-theme.yaml
```

建立後編輯 YAML，再驗證：

```bash
learn2deck theme validate my-theme.yaml
```

### 3.4 `learn2deck theme validate <PATH>`

驗證自訂主題檔案。

```bash
learn2deck theme validate my-theme.yaml
```

## 4. `learn2deck init`

初始化新 deck 專案（含範本檔案）。

### 語法

```bash
learn2deck init [DIRECTORY]
```

`DIRECTORY` 預設為 `my-deck`。

### 範例

```bash
learn2deck init my-deck/
learn2deck init ~/projects/my-slides
```

會建立以下檔案：

```
my-deck/
├── outline.yaml    # 結構化大綱（精確控制每張投影片）
├── content.md      # Markdown 內容（自動推斷版型）
└── README.md       # 使用說明
```

### 下一步

```bash
learn2deck build my-deck/content.md -o my-deck/output.pptx
```

## 5. `learn2deck version`

顯示版本資訊。

```bash
learn2deck version
# 或
learn2deck --version
```

輸出：`learn2deck v1.0.0`

## 6. 環境變數

目前無強制環境變數。若 `learn2deck` 指令不在 PATH 中：

```bash
# 確認指令可用
which learn2deck

# 若不可用，改用 python -m 形式
python -m learn2deck build input.md -o output.pptx

# 或確認套件已安裝
pip show learn2deck
```

### 安裝

```bash
# 正式版（從 PyPI，推薦一般使用者）
pip install learn2deck

# 開發版（從原始碼，需先取得套件原始碼）
git clone https://github.com/kcf7012/pi-proj.git
cd pi-proj/learn2deck
pip install -e .
```

## 7. 常用工作流

### 7.1 單檔轉換

```bash
learn2deck build my-slides.md -o output.pptx --validate
```

### 7.2 批次處理 8 份文件

```bash
for md in 0?-*.md; do
  base=$(basename "$md" .md)
  learn2deck build "$md" -o "/tmp/new_${base}.pptx" --validate -q
done
```

### 7.3 CI/CD 整合

```bash
#!/bin/bash
set -e

learn2deck build content.md -o output.pptx --validate --strict
learn2deck validate output.pptx --json > report.json

# 從 JSON 取錯誤數
errors=$(jq '.errors' report.json)
if [ "$errors" -gt 0 ]; then
  echo "❌ Build failed: $errors errors"
  exit 1
fi
```

### 7.4 切換主題測試

```bash
for theme in claude-orange minimal-bw; do
  learn2deck build content.md -o "output-${theme}.pptx" --theme "$theme" -q
done
```

## 8. 參考資源

- CLI 實作：`learn2deck/cli.py`
- 主題管理：`learn2deck/lib/themes/`
- 驗證規則：`learn2deck/lib/validators/`
- 規格書：`docs/learn2deck-spec.md` §7
