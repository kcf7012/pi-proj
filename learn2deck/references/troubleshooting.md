# 疑難排解

> 常見錯誤與解決方案

## Q1: build 失敗 `list index out of range`

**錯誤訊息**：
```
❌ 產出失敗：list index out of range
```

**原因**：Markdown 表格的 column 數不一致，或表格 cell 內有 `|` 沒跳脫。

**解決**：

1. 檢查 Markdown table：
   ```markdown
   | 欄位 A | 欄位 B | 欄位 C |
   |--------|--------|--------|
   | 值 1   | 值 2   |        |  ← 第三欄空了
   ```

2. 若 cell 內容有 `|`，用 `\|` 跳脫：
   ```markdown
   | 指令 | 範例                     |
   |------|--------------------------|
   | filter | `a \| b`              |
   ```

3. 確保所有 row 的 column 數 = headers 數。

**預防**：用 Markdown 編輯器（如 VS Code）開 preview 模式檢查表格對齊。

---

## Q2: 表格塞不下（內容被截斷）

**錯誤訊息**：
```
[WARN][R3] Slide 5: 內容超出安全區...
```

**原因**：表格 row > 7 或 cell 文字太長。

**解決**：

1. **減少 row 數**：拆成多張 slide
2. **縮短 cell 文字**：用縮寫、刪除多餘字
3. **改用 `title_content`**：當只有 2-3 個對比項目時
4. **自動降級**：title_table 自動降級字級（11 → 10 → 9 pt）

**範例**：

```markdown
<!-- ❌ 太長 -->
| Plugin 名稱 | 用途說明（適用於大型團隊、需要版本管理、跨專案共用的複雜情境） | 備註 |
|-------------|--------------------------------------------------------|------|

<!-- ✅ 簡潔 -->
| Plugin 名稱 | 適用情境           | 備註 |
|-------------|-------------------|------|
| team-utils  | 大型團隊、跨專案   | v1.0 |
```

---

## Q3: 重疊 warning (R2)

**警告訊息**：
```
[WARN][R2] Slide 12: 元素重疊：「Plugin 元件說明」與「範例程式碼」
```

**原因**：
- grid_cards 的 desc 太長，擠到下一張卡片
- icon 壓在卡片邊緣
- 設計性重疊（箭頭指向 callout）

**解決**：

1. **縮短 grid_cards 的 desc**（≤ 30 字）
2. **減少 items 數量**（6 → 4）
3. **改用更少欄數**（4 → 3）
4. **接受 warning**：若為設計性重疊，可用 `--strict=false` 略過

**範例**：

```yaml
# ❌ desc 太長
- icon: "📚"
  title: "Skills"
  desc: "可重用的知識庫，透過 /skill-name 觸發，可被 Agent 載入作為上下文，支援 SKILL.md 格式"

# ✅ 簡潔
- icon: "📚"
  title: "Skills"
  desc: "可重用的知識庫 · /skill-name"
```

---

## Q4: Code 框裝不下 (R1)

**錯誤訊息**：
```
[ERROR][R1] Slide 8: Code 框裝不下：25 行 @ 12pt 需要 6.05"，實際 5.50"（不足 -0.55"）
```

**原因**：code 區塊行數過多。

**解決**：

1. **自動降級**：title_code 內建降級（12 → 11 → 10 → 9 → 8 pt）
2. **拆成多張 slide**：每張 ≤ 15 行
3. **移除空行**：合併相鄰 code lines
4. **縮排調整**：減少前導空白

**範例**：

````markdown
<!-- ❌ 太多 -->
```python
def func1():
    pass

def func2():
    pass

def func3():
    pass
```

<!-- ✅ 精簡 -->
```python
def func1(): pass
def func2(): pass
def func3(): pass
```
````

---

## Q5: Markdown 沒被解析（沒產生對應 slide）

**症狀**：build 成功但只有 1 張 slide。

**原因**：
- 沒用 `## ` H2 開頭
- H2 後沒接內容

**解決**：

```markdown
<!-- ❌ 沒用 H2 -->
# 我的主題
內容...

<!-- ✅ 用 H2 區隔章節 -->
# 我的主題

## 第一章

內容...

## 第二章

內容...
```

---

## Q6: 找不到 `learn2deck` 指令

**錯誤訊息**：
```
bash: learn2deck: command not found
```

**原因**：`.pptx-venv/bin/` 不在 PATH 中。

**解決**：

```bash
# 方案 A：用絕對路徑
/home/elan/pi-proj/.pptx-venv/bin/learn2deck build input.md -o output.pptx

# 方案 B：暫時啟用 venv
source /home/elan/pi-proj/.pptx-venv/bin/activate
learn2deck build input.md -o output.pptx

# 方案 C：加進 PATH（永久）
echo 'export PATH="/home/elan/pi-proj/.pptx-venv/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

**驗證**：

```bash
which learn2deck
# 應輸出：/home/elan/pi-proj/.pptx-venv/bin/learn2deck
```

---

## Q7: 主題載入失敗

**錯誤訊息**：
```
❌ ThemeNotFoundError: 主題 'my-theme' 找不到
```

**原因**：
- 主題檔案不存在於 `learn2deck/lib/themes/`
- 主題 YAML 語法錯誤
- 顏色 hex 格式錯誤

**解決**：

```bash
# 1. 列出可用主題
learn2deck theme list

# 2. 驗證主題檔案
learn2deck theme validate /path/to/theme.yaml

# 3. 常見 YAML 錯誤：
#    - 縮排不一致（用 2 空格）
#    - 顏色忘了 # 號（"#C75A1A" 而非 "C75A1A"）
#    - 字串沒引號包（含特殊字元時）
```

---

## Q8: YAML 大綱解析失敗

**錯誤訊息**：
```
NotImplementedError: YAML outline 解析尚未實作，請用 .md
```

**原因**：v1.0 主要支援 .md，YAML outline 解析尚未實作。

**解決**：

- 使用 .md 檔（推薦）
- 或先用 .md 試作，再用 `learn2deck init` 產生的 outline.yaml 作為未來格式參考
- v1.1+ 才會完整支援 YAML

**替代方案**：在 Markdown 內用 H2/H3 結構表達，parser 會自動推斷版型。

---

## Q9: 中文標點在 code 框被截斷

**症狀**：code 框內含中文全形標點（如 `，。！？`)時，最後一個字元被截掉。

**原因**：中文字寬估算偏差。

**解決**（暫時）：

1. code 框內盡量用半形標點（`,.!?`）
2. 或在中文標點後加空格
3. 或拆成多張 slide

**範例**：

````markdown
<!-- ❌ 可能被截斷 -->
```bash
echo "你好，世界。"
```

<!-- ✅ 加空格 -->
```bash
echo "你好， 世界 。"
```
````

**追蹤**：見 HANDOFF.md §6 待確認事項

---

## Q10: `04-skills.md` 部分 slide 有 raw markdown

**症狀**：build 成功，但某些 slide 顯示 `**bold**` 或 `` `code` `` 而非格式化文字。

**原因**：inline markdown 沒被解析（parser bug）。

**已知發生位置**：04-skills.md slide 5/21

**解決**：

1. 確認 builder 呼叫了 `strip_markdown_inline()`（`learn2deck/lib/parsers/markdown.py`）
2. 或在 .md 用 HTML 標籤替代 markdown：
   ```markdown
   <!-- ❌ -->
   使用 **bold** 與 `code`
   
   <!-- ✅ -->
   使用 <b>bold</b> 與 <code>code</code>
   ```

---

## Q11: 視覺風格與舊版 PPTX 不一致

**症狀**：build 成功、validate pass，但看起來與 00-07*.pptx 不一樣。

**原因**：
- 主題不是 `claude-orange`
- 用了不同 builder（如 `title_table` vs `title_content`）

**解決**：

```bash
# 確認主題
learn2deck build input.md -o output.pptx --theme claude-orange --validate

# 比較結構
python tools/diff_pptx.py old.pptx output.pptx
python tools/structural_report.py
```

**視覺驗證**：在本機用 LibreOffice / PowerPoint 並排開啟新舊 PPTX。

---

## Q12: build 後 `validate --strict` 失敗

**錯誤訊息**：
```
❌ 1 error, 0 warnings
[ERROR][R1] ...
exit code 1
```

**原因**：`--strict` 把 warning 也視為錯誤。

**解決**：

```bash
# 方案 A：修正問題（推薦）
# 根據錯誤訊息調整 .md

# 方案 B：只用 --validate（warning 不擋 exit code）
learn2deck build input.md -o output.pptx --validate

# 方案 C：略過驗證
learn2deck build input.md -o output.pptx
```

---

## Q13: 想看 build 過程的詳細資訊

```bash
# 預設模式（顯示解析、產生、驗證進度）
learn2deck build input.md -o output.pptx

# 顯示更多結構資訊
python tools/inspect_deck.py input.md
python tools/inspect_pptx.py output.pptx

# 結構比對
python tools/structural_report.py
```

---

## Q14: 想自訂主題但不知道從哪開始

**步驟**：

```bash
# 1. 複製現有主題
learn2deck theme new my-theme --base claude-orange

# 2. 編輯 themes/my-theme.yaml
vim themes/my-theme.yaml

# 3. 驗證主題
learn2deck theme validate themes/my-theme.yaml

# 4. 測試套用
learn2deck build input.md -o output.pptx --theme my-theme

# 5. 視覺確認
```

**參考**：見 `references/style-guide.md` 了解每個顏色/字級的用途。

---

## Q15: 怎麼把 8 份 .md 一次轉成 8 份 PPTX？

```bash
cd /home/elan/pi-proj/learn2deck

for md in ../0?-*.md; do
  base=$(basename "$md" .md)
  echo "🔄 處理 $base..."
  /home/elan/pi-proj/.pptx-venv/bin/learn2deck build "$md" \
    -o "/tmp/new_${base}.pptx" --validate -q
done

echo "✅ 全部完成，新檔位於 /tmp/new_*.pptx"
```

---

## 還有問題？

1. 查 `references/` 5 個檔案
2. 跑 `python tools/layout_check.py /tmp/new_*.pptx`
3. 看 HANDOFF.md §6 待確認事項
4. 開 issue：https://github.com/kcf7012/pi-proj/issues

## 參考資源

- HANDOFF.md §6：已知待確認事項
- tools/：視覺驗證工具集
- examples/minimal-plugin/：完整範例
