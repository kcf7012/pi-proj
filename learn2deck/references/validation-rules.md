# 驗證規則詳解（R1-R5）

> **權威來源**：`learn2deck/lib/validators/`
> **對應**：`docs/learn2deck-spec.md` §3

## 規則總覽

| 規則 | 名稱 | 嚴重度 | 說明 |
|:-----|:-----|:-------|:-----|
| R1 | Code 框容量 | **ERROR** | code 框裝不下內容時報錯 |
| R2 | 元素重疊 | **WARNING** | 兩個元素 bounding box 重疊（教學範本常有設計性重疊，故為 warning） |
| R3 | 品牌列安全 | **WARNING** | 內容超出 y=7.0" 安全區 |
| R5 | 檔案格式 | **ERROR** | 產出檔案不是有效的 PPTX |

> **無 R4**：R4 保留給未來擴充，目前跳過

## R1：Code 框容量（ERROR）

### 規則

```
N 行 × 行高(font_size) + 0.2" margin ≤ 框高
```

若 `所需高度 > 實際框高` → 報 ERROR。

### 偵測邏輯

1. 找出投影片中所有「深色背景矩形」（RGB 三值均 < 64）= code 框背景
2. 找配對的 textbox（位置大小完全相同，排除 AUTO_SHAPE 本身）
3. 從 textbox 計算實際行數（`\n` 數 + 1）與字級（第一個 run）
4. 查表 `LINE_HEIGHTS[font_size]` 取得行高
5. 比對所需高度 vs 實際框高

### 行高對照表（`pptx_helpers.layout.LINE_HEIGHTS`）

| 字級 (pt) | 行高 (inches) |
|:----------|:--------------|
| 8 | 0.155 |
| 9 | 0.175 |
| 10 | 0.195 |
| 11 | 0.215 |
| 12 | 0.235 |
| 14 | 0.275 |

### 自動修正

`title_code` builder 已經內建自動降級字級（12 → 11 → 10 → 9 → 8 pt）。當行數 × 行高 > 5.5" 時自動降級。

### 手動修正建議

- ❌ 程式碼太長 → 拆成多張 slide
- ❌ 有大量空行 → 移除多餘空行
- ❌ 改用 `title_content` 摘要重點

### 範例錯誤訊息

```
[ERROR][R1] Slide 5: Code 框裝不下：18 行 @ 12pt 需要 4.43"，實際 3.80"（不足 -0.63"）
```

## R2：元素重疊（WARNING）

### 規則

兩個非配對元素的 bounding box 有交集（水平 > 0.05" 且垂直 > 0.05"）。

### 排除規則

- **配對元素**：背景矩形 + 同位置 textbox（位置大小相同）
- **完全包含**：A 完全在 B 內（含 0.05" 容忍）
- **裝飾元素**：高度 < 0.2"（頂部 accent line）
- **品牌列**：top ≥ 7.05"

### 為什麼是 WARNING 而非 ERROR

教學型簡報常見「設計性重疊」：
- 箭頭指向 callout 框
- 圖示壓在卡片邊緣
- 標記重疊在內容上

故 v1.0 改為 WARNING，由人工決定是否接受。

### 常見誤判

- ✅ 正常的配對 code 框（深色矩形 + 文字）→ 不報
- ✅ 頂部橘色條（高度 0.15"）→ 不報
- ✅ 卡片內的 icon 與文字（icon 通常是裝飾）→ 不報
- ⚠️ grid_cards 的 desc 太長擠到下一張 card → 會報

### 修正建議

- 縮短 grid_cards 的 desc
- 加大 grid_cards 的間距
- 改用更少欄數（4 → 3）

### 範例錯誤訊息

```
[WARNING][R2] Slide 12: 元素重疊：「Plugin 元件說明」與「「範例程式碼」(1.20" × 0.45")
```

## R3：品牌列安全（WARNING）

### 規則

```
任何內容元素 top + height > 7.0" → WARNING
```

品牌列在 y=7.1"，所有內容應在 7.0" 內（容忍至 7.35"）。

### 偵測邏輯

1. 遍歷所有 shape
2. 計算 `bottom = top + height`（轉 inch）
3. 跳過品牌列本身（7.0 < bottom ≤ 7.45）
4. 若 bottom > 7.0 → 報 warning

### 設計容忍區

| 區域 | Y 範圍 | 說明 |
|:-----|:-------|:-----|
| 內容區 | 1.3" - 7.0" | 主要版面（高度 5.7"） |
| 容忍下緣 | 7.0" - 7.35" | 超出會出 R3 warning |
| 品牌列 | 7.1" - 7.4" | 底部品牌標（不檢查） |
| 投影片底 | 7.5" | 投影片總高 |

### 常見原因

- grid_cards 的 desc 太長，導致卡片底部超過 7.0"
- title_content 的 bullet 太多（>8 個）
- code 框過高（>5.5"）

### 修正建議

- 縮短 desc 文字
- 拆成多張 slide
- 減少 items 數

### 範例錯誤訊息

```
[WARNING][R3] Slide 7: 內容超出安全區：'安裝步驟詳述...' 底部 y=7.18"（超出 0.18"）
```

## R5：檔案格式（ERROR）

### 規則

產出檔案必須是有效的 Microsoft PowerPoint 2007+ 格式。

### 檢查項目

1. ✅ 副檔名為 `.pptx`
2. ✅ 檔案存在
3. ✅ 是有效的 ZIP（PPTX 內部用 ZIP 容器）
4. ✅ 包含必要檔案：
   - `[Content_Types].xml`
   - `ppt/presentation.xml`
5. ✅ 能被 python-pptx 重新讀取

### 偵測邏輯

```python
# 1. 副檔名檢查
if path.suffix.lower() != ".pptx":
    return ERROR

# 2. ZIP 檢查
if not zipfile.is_zipfile(path):
    return ERROR

# 3. 內部結構檢查
with zipfile.ZipFile(path, "r") as zf:
    names = zf.namelist()
    required = ["[Content_Types].xml", "ppt/presentation.xml"]
    missing = [r for r in required if r not in names]
    if missing:
        return ERROR
```

### 常見失敗原因

- ❌ 寫入時磁碟空間不足 → ZIP 損壞
- ❌ 程式異常中斷 → 檔案不完整
- ❌ 手動改檔名 → 副檔名錯誤

### 範例錯誤訊息

```
[ERROR][R5] 副檔名錯誤：.PPTX（應為 .pptx）
[ERROR][R5] 不是有效的 PPTX（ZIP 格式錯誤）：/tmp/output.pptx
[ERROR][R5] PPTX 內部結構不完整，缺少：ppt/presentation.xml
```

## 執行驗證

### CLI 自動驗證

```bash
# build 時自動驗證
learn2deck build input.md -o output.pptx --validate

# 單獨驗證
learn2deck validate output.pptx
```

### 程式化驗證

```python
from learn2deck.lib.validators import run_validators
from pptx import Presentation

prs = Presentation("output.pptx")
issues = run_validators(prs, rules=["R1", "R2", "R3"])

for issue in issues:
    print(f"[{issue.severity.upper()}][{issue.rule}] {issue.message}")
```

### 規則選擇

預設執行 R1, R2, R3（R5 是檔案層級，CLI 自動檢查）。可在 `validators/__init__.py` 的 `BUILTIN_VALIDATORS` 註冊新規則。

## 驗證結果解讀

### 全部通過

```
✨ No issues found
```

代表通過所有啟用的驗證規則。

### 只有 warning

```
⚠️ 0 errors, 2 warnings
[WARN][R2] Slide 5: 元素重疊：...
[WARN][R3] Slide 7: 內容超出安全區：...
```

可選擇接受或修正。warning 不阻擋 build 成功。

### 有 error

```
❌ 1 error, 0 warnings
[ERROR][R1] Slide 5: Code 框裝不下：...
[ERROR][R5] 副檔名錯誤：...
```

**會阻擋 build 成功**（`--validate` 模式下回傳非零 exit code）。

## 參考資源

- 規則實作：`learn2deck/lib/validators/{rule}.py`
- Issue 結構：`learn2deck/lib/validators/base.py`
- 規格書：`docs/learn2deck-spec.md` §3
- 工具：`tools/layout_check.py`（批次版面檢查）
