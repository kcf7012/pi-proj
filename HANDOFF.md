# Handoff Document — Claude Code Plugin 學習系列

> **交接給下一個任務使用**
> 建立日期：2026/01
> 最後更新：2026/08（完成 4 份新簡報 + 版面修正）
> 對應 GitHub 倉庫：[kcf7012/pi-proj](https://github.com/kcf7012/pi-proj)

---

## 0. 狀態總結（2026/08）

- ✅ 8 份 PPTX 簡報全部完成（277 張投影片，總 ~830 KB）
- ✅ 8 份 Markdown 教材
- ✅ 8 份 build scripts 可重新生成簡報
- ✅ 已修正 21 個 code 框容量不足 + 2 個版面重疊問題
- ❎ 已刪除 3 個失敗工具（`_analyze_*.py`、`_postprocess_fix_overflow.py`）

---

## 1. 目前任務目標

將 Claude Code Plugin 完整學習系列整理成可閱讀、可演講、可版本控制的教材，包含：
- **8 份 Markdown 教學文件**（繁體中文）
- **8 份 PPTX 簡報**（PowerPoint格式，277 張投影片）
- **Python 建置腳本**（可重新生成簡報）
- **Git 版控**（已推送至 GitHub）

---

## 2. 已完成內容

### 2.1 Markdown 教材（8 份，272 KB，6,682 行）
- `00-claude-code-plugins-series.md` — 系列總覽
- `01-plugin-marketplaces.md` — Plugin Marketplaces
- `02-plugins.md` — Plugin 開發入門
- `03-plugins-reference.md` — Plugin 技術參考
- `04-skills.md` — Skills 完整指南
- `05-subagents.md` — Subagents 自訂指南
- `06-hooks.md` — Hooks 自動化指南
- `07-discover-plugins.md` — 探索並安裝 Plugins

### 2.2 PPTX 簡報（8 份，830 KB）
- `00-overview.pptx` — 30 張（系列總覽）
- `01-plugin-marketplaces.pptx` — 35 張（Marketplace）
- `02-plugins.pptx` — 25 張（Plugin 開發）
- `03-plugins-reference.pptx` — 45 張（Plugin 技術參考）
- `04-skills.pptx` — 40 張（Skills）
- `05-subagents.pptx` — 30 張（Subagents）
- `06-hooks.pptx` — 50 張（Hooks）— 修正最多
- `07-discover-plugins.pptx` — 22 張（探索並安裝）

### 2.3 Python 建置腳本
- `_pptx_helpers.py` — 共用 helper（設計系統、helper 函式）
- `_make_00_overview.py` — 生成 00-overview.pptx
- `_make_01_marketplaces.py` — 生成 01-plugin-marketplaces.pptx
- `_make_02_plugins.py` — 生成 02-plugins.pptx
- `_make_03_plugins_reference.py` — 生成 03-plugins-reference.pptx
- `_make_04_skills.py` — 生成 04-skills.pptx
- `_make_05_subagents.py` — 生成 05-subagents.pptx
- `_make_06_hooks.py` — 生成 06-hooks.pptx
- `_make_07_discover_plugins.py` — 生成 07-discover-plugins.pptx

### 2.4 版控歷史
```
bdbfccb fix(layout): 06-hooks 多張投影片底部重疊 + 00-overview Slide 23 箭頭
aa46fc5 fix(layout): fix text overflow on 4 problem slides
39cea39 docs: update author name to Kenny Kang
52cdeb4 build: add Python scripts to regenerate PPTX presentations
73d38f5 feat: add 4 PowerPoint presentations of the learning series
bf1011c docs: add 8 markdown files of the complete Claude Code learning series
8c54682 chore: initial commit with .gitignore and README
```

### 2.5 已修正的版面問題
- **06-hooks.pptx**：19 張版面問題（已完成）
- **00-overview.pptx Slide 23**：箭頭修正（已完成）
- **2026/08 新增 4 份簡報後發現的問題**：
  - 21 個 code 框高度不足 → 調整 code 框高度 / 縮小字體 / 精簡內容
  - 01-S27 標題被 code 框蓋住 → 重新分配版面
  - 01-S16 卡片重疊 → 縮小卡片高度 + 合併 callout
  - 額外修正的 8 個 borderline slides（S30, S31, S10, S18, S20, S21 等）

---

## 3. 關鍵文件和位置

### 3.1 倉庫結構（位於 `/home/elan/pi-proj/`）
```
pi-proj/
├── README.md                    ← 專案說明（必讀）
├── .gitignore                   ← 忽略 .pptx-venv/、__pycache__/ 等
├── 00-07 系列 .md 檔案          ← 8 份教材
├── 00-07 系列 .pptx 共 8 份     ← 簡報
├── _make_*.py + _pptx_helpers.py ← 8 份建置腳本
├── .pptx-venv/                  ← Python 虛擬環境（已 .gitignore）
```

### 3.2 環境建置
```bash
# Python 3.11+ + uv 必要
uv venv .pptx-venv --python 3.11
uv pip install --python .pptx-venv/bin/python python-pptx

# 重新生成所有簡報
.pptx-venv/bin/python _make_00_overview.py
.pptx-venv/bin/python _make_01_marketplaces.py
.pptx-venv/bin/python _make_02_plugins.py
.pptx-venv/bin/python _make_03_plugins_reference.py
.pptx-venv/bin/python _make_04_skills.py
.pptx-venv/bin/python _make_05_subagents.py
.pptx-venv/bin/python _make_06_hooks.py
.pptx-venv/bin/python _make_07_discover_plugins.py
```

### 3.3 GitHub 認證
- 使用 `gh auth login --web` 登入（帳號 kcf7012）
- HTTPS push 已可用
- 主要 branch：`main`

---

## 4. 重要規則和限制

### 4.1 設計系統（`_pptx_helpers.py` 頂部）
- 簡報尺寸：**16:9**（13.333 × 7.5 inch）
- 主色：Claude 橘 `#C75A1A`、深灰 `#2C2C2C`、米白 `#FAF8F3`
- 字體：標題 Calibri Bold、內文 Calibri、程式碼 Consolas
- 標題字級：32pt、副標題 16pt
- 底部品牌列：位於 y=7.1"（所有內容須在 7.0" 以內）
- 頂部標題列：位於 y=0-1.15"（內容須從 1.3" 開始）

### 4.2 Python 限制
- 環境：`.pptx-venv/`（不要 commit）
- 沒有 root 權限（無法 apt install）；用 `uv` 管理套件
- 沒有 `pip` 直接可用，必須透過 `uv pip install`

### 4.3 PPTX 設計陷阱（重要！）
- `add_connector(1, ...)`（直線箭頭）會被 PowerPoint 自動繞路或被圖卡覆蓋
- **箭頭統一用 `MSO_SHAPE.RIGHT_ARROW` 三角形**，不要用 connector
- 文字框 `add_text_block` 不會自動調整高度，**必須手動算空間**
- code block 的字體 9pt 在 3.6" 高度內可裝約 22 行；8pt 約 25 行
- 1.5" 高度的兩欄（`add_two_column_compare`）只能裝 1-2 個 bullet，**至少 1.6" 才能裝 3 個**

### 4.4 修版面問題的標準做法
當發現「字重疊」或「code 框字溢出」：
1. **加大 code 框高度**（必要時 0.3-0.5"）
2. **縮小 code 內字體**（9→8pt 仍可讀）
3. **把後續元素往下挪**
4. **兩欄高度 1.6"+**（1.5" 不夠裝 3 個 bullet）

---

## 5. 已確認結論

1. ✅ **8 份 Markdown 內容完整**，整理自 code.claude.com/docs 官方文件
2. ✅ **8 份 PPTX 可在 Microsoft PowerPoint 2007+ 開啟**（`file xxx.pptx` 確認）
3. ✅ **06-hooks.pptx 修正 19 張版面問題**（已 commit + push）
4. ✅ **00-overview.pptx Slide 23 箭頭修正**（用 RIGHT_ARROW 三角形）
5. ✅ **Git 倉庫**：[kcf7012/pi-proj](https://github.com/kcf7012/pi-proj)
6. ✅ **README 整理人**：「Kenny Kang」
7. ✅ **GitHub 認證**：`gh auth login` 完成（kcf7012）
8. ✅ **4 份新簡報完成**（01/03/05/07）+ 修正 21 個 code 框高度 + 2 個版面重疊

---

## 6. 已完成（2026/08 更新）

- ✅ **剩下 4 份簡報**（01、03、05、07）— 全部完成
- ✅ **01-plugin-marketplaces.md** 對應的 PPTX — 已生成（35 張）
- ✅ **03-plugins-reference.md** 對應的 PPTX — 已生成（45 張）
- ✅ **05-subagents.md** 對應的 PPTX — 已生成（30 張）
- ✅ **07-discover-plugins.md** 對應的 PPTX — 已生成（22 張）
- ✅ **analyze/postprocess 工具**（`_analyze_layout.py`, `_analyze_overflow.py`, `_postprocess_fix_overflow.py`）— **已刪除**
- ✅ **已修正所有發現的版面問題**（見 §2.5）

---

## 7. 不要重複做的事情

### ❌ 不要重建 `_postprocess_fix_overflow.py`
- 它會**誤判版面**（把所有文字框都當溢位）
- 結果是縮小字體或擴大框，反而讓版面變更糟
- 正確做法：直接改 `_make_*.py` 重跑

### ❌ 不要用 connector 畫箭頭
- `add_connector(1, ...)` 在 PowerPoint 中會被自動繞路
- Slide 23 已發生過此問題，已改用 `RIGHT_ARROW` 三角形
- 後續如需箭頭，統一用 `MSO_SHAPE.RIGHT_ARROW`

### ❌ 不要把 `.pptx-venv/` commit
- 已加入 `.gitignore`，但要確認不要用 `git add -f`

### ❌ 不要忘記 .py 與 .pptx 要一起 commit
- PPTX 是 .py 產生的，但每次改完 .py 都會重新生成 .pptx
- 兩者必須**一起**進版控（否則下次重跑會覆蓋掉 PPTX 的修正）

---

## 8. 建議下一步

### 優先 A：做剩下 4 份簡報（01、03、05、07）
參考現有的 4 份 `_make_*.py` 結構，新建模版：
- `_make_01_marketplaces.py`（約 25-35 張）
- `_make_03_plugins_reference.py`（約 40-50 張，技術參考內容多）
- `_make_05_subagents.py`（約 30-35 張）
- `_make_07_discover_plugins.py`（約 20-25 張）

**注意**：建立新簡報時**直接套用既有的版面原則**（避免之後再修版面問題）：
- code 框高度留 0.3" 安全邊距
- 兩欄高度 1.6"+
- 整體底部不超過 7.0"
- 任何 7 張以上 bullet 用 0.3" 間距

### 優先 B：清理工作目錄
```bash
# 刪除早期失敗的工具
rm /home/elan/pi-proj/_analyze_layout.py
rm /home/elan/pi-proj/_analyze_overflow.py
rm /home/elan/pi-proj/_postprocess_fix_overflow.py
```

### 優先 C：在 GitHub 建立 Issues
為「待確認事項」建立對應 issue，方便追蹤。

### 優先 D：定期重整
- 4 份簡報約 3 個月後可以 review 一次（看官方文件是否有更新）
- 簡報內容可以根據實際教學經驗微調

---

## 附錄：常用指令速查

```bash
# 環境
cd /home/elan/pi-proj
source .pptx-venv/bin/activate  # 或直接用 .pptx-venv/bin/python

# 重新生成簡報
.pptx-venv/bin/python _make_00_overview.py
.pptx-venv/bin/python _make_02_plugins.py
.pptx-venv/bin/python _make_04_skills.py
.pptx-venv/bin/python _make_06_hooks.py

# Git 操作
git status
git add -A
git commit -m "feat: ..."
git push
gh auth login --web              # 認證過期時重新登入

# 驗證 PPTX
file *.pptx                       # 確認 PowerPoint 2007+ 格式
.pptx-venv/bin/python -c "from pptx import Presentation; print(len(Presentation('06-hooks.pptx').slides))"  # 確認張數
```

---

**Handoff 結束。下一個任務接手者請從「已完成的狀態」與「本文件後續建議」開始。**
