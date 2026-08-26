# Phase 9 視覺驗證檢核清單

> 用途：用 LibreOffice / PowerPoint 並排開新舊 .pptx 時的逐張檢查表。
> 每張投影片印一份，發現問題就記下來，事後統一修 builder。

---

## 使用方式

1. 開 `/tmp/phase9_report.html`（build_html_report.py 產出）
2. 從目錄跳到要檢查的檔案
3. 每張 slide 印一頁（或直接在 HTML 上看完）
4. 用以下檢核表逐項打勾
5. 發現問題就在備註寫清楚哪個 builder 哪個屬性

---

## 通用檢查（每張 slide）

- [ ] **橘色裝飾條** 在頂部（寬度 13.33"、高 0.15"、`#C75A1A`）
- [ ] **底部品牌列** 在 y=7.1"
  - [ ] 左側「Claude Code Plugin 完整學習系列」（橘色粗體）
  - [ ] 右側「📖 來源：<標題>」（灰色）
- [ ] **頁碼** 右上角（格式：`N / TOTAL`）
- [ ] **內容不超出 7.0"**（容忍至 7.35"）
- [ ] **內容不與頂部裝飾條重疊**（title 從 1.3" 開始）
- [ ] **字體**：標題 Calibri Bold、內文 Calibri、code Consolas
- [ ] **顏色**：標題 `#2C2C2C`、副標 `#6B6B6B`、強調 `#C75A1A`

---

## 9 種版型檢查

### Cover（封面 — 00-overview slide 1）
- [ ] 大標題（54pt 粗體 `#C75A1A`）
- [ ] 副標題（22pt `#2C2C2C`）
- [ ] tag 文字（14pt `#6B6B6B`）
- [ ] 橘色裝飾條在 (5.67, 5.6) (2.0 x 0.08)

### Objectives（學習目標 — 罕見，主要在舊版有）
- [ ] 6 個網格卡片對齊
- [ ] icon 在每張卡片左上
- [ ] title + desc 垂直排列
- [ ] 卡片邊框統一

### Section Divider（章節分隔 — Part X）
- [ ] 大編號（96pt，`#C75A1A`）
- [ ] 章節標題 + 副標題
- [ ] 居中對齊

### Title + Content（標題+文字）
- [ ] 標題 28pt 粗體
- [ ] bullets 對齊（左縮排一致）
- [ ] 字級 14pt
- [ ] 行距 1.4

### Title + Table（標題+表格）
- [ ] 標題列橘底白字
- [ ] alternating row bg（白 / `#F3F0E9`）
- [ ] 表格不會超出 4.8" 高度
- [ ] cell 內文字不應再有 `**` 或 `` ` ``
- [ ] 中英文混雜不會斷行

### Title + Code（標題+程式碼）
- [ ] code 框淺灰底
- [ ] 等寬字 Consolas
- [ ] code 框動態高度（行數 × 0.16"）
- [ ] 超過 5.5" 時字級自動降為 10/9/8pt

### Two Column（雙欄對比）
- [ ] 兩個並排卡片
- [ ] 卡片標題列有色背景
- [ ] bullet 對齊
- [ ] 左右兩欄寬度一致

### Grid Cards（網格卡片）
- [ ] 3 欄網格（罕見 2/4 欄）
- [ ] icon + title + desc 垂直排列
- [ ] 卡片大小一致
- [ ] 卡片間距對稱

### Summary（重點回顧）
- [ ] 「下一步」標題
- [ ] 「📌 關鍵要點」section
- [ ] bullets 列表
- [ ] 「下一步行動」section

---

## 每張 slide 紀錄格式

```
檔案: 04-skills.pptx
Slide: 5
版型: title_code
檢查結果:
  ✓ 橘色裝飾條 OK
  ✓ 底部品牌列 OK
  ✗ code 框包含 raw markdown 文字（**讓 Claude 自動叫用**）
  ⚠ code 框高度可能塞不下

備註: extract_code_block 抓到孤兒 ``` 結尾，把整個 SKILL.md 範例當 code
建議: parser 需要過濾 code block 內的 ## 標題（誤判為頂層章節）
```

---

## 已知問題（commit 048ebba 後剩餘）

| 檔案 | Slide | 問題 | 嚴重度 |
|------|-------|------|--------|
| 04-skills | 5 | code 框包含 SKILL.md 範例（**讓 Claude 自動叫用**）| 高 |
| 04-skills | 21 | numbered list 內 raw markdown | 中 |
| 全部 | - | 無 COVER slide（自動插入）| 中 |
| 全部 | - | 無 SECTION_DIVIDER（自動插入）| 中 |
| 多個 | - | grid_cards 推斷被 code 蓋掉 | 低 |

---

## 驗證完成後

1. 將所有發現的問題整理到 `/home/elan/pi-proj/learn2deck/PHASE9_ISSUES.md`
2. 提交給下一個 session 修 builder / parser
3. 修完重產 → 重跑本檢核表
4. 全部通過後進入 Phase 10
