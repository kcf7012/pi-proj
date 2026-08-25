# Handoff Document — Claude Code Plugin 學習系列

> **交接給下一個任務使用**
> 建立日期：2026/01
> 最後更新：2026/08（完成 4 份新簡報 + 版面修正 + 已推送 GitHub）
> 對應 GitHub 倉庫：[kcf7012/pi-proj](https://github.com/kcf7012/pi-proj)
> 對應 main branch commit：`2ae41d9`

---

## 0. 狀態總結（2026/08 最終版）

- ✅ **8 份 PPTX 簡報全部完成**（277 張投影片，總 ~830 KB）
- ✅ **8 份 Markdown 教材**（繁體中文，272 KB / 6,682 行）
- ✅ **8 份 build scripts**（可重新生成所有簡報）
- ✅ **已修正所有版面問題**（21 個 code 框容量 + 2 個重疊 + 8 個 borderline）
- ✅ **已刪除 3 個失敗工具**
- ✅ **已推送至 GitHub**（commit `2ae41d9`）

**本系列已完整、可閱讀、可演講、可版本控制。**

---

## 1. 目前任務目標

將 Claude Code Plugin 完整學習系列整理成可閱讀、可演講、可版本控制的教材，包含：
- **8 份 Markdown 教學文件**（繁體中文）
- **8 份 PPTX 簡報**（PowerPoint 格式，277 張投影片）
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

### 2.2 PPTX 簡報（8 份，~830 KB，277 張投影片）
| 編號 | 檔案 | 張數 | 對應 |
|:----:|:-----|:----:|:-----|
| 00 | `00-overview.pptx` | 30 | 系列總覽 |
| 01 | `01-plugin-marketplaces.pptx` | 35 | Plugin Marketplaces |
| 02 | `02-plugins.pptx` | 25 | Plugin 開發 |
| 03 | `03-plugins-reference.pptx` | 45 | Plugin 技術參考 |
| 04 | `04-skills.pptx` | 40 | Skills 完整指南 |
| 05 | `05-subagents.pptx` | 30 | Subagents 自訂指南 |
| 06 | `06-hooks.pptx` | 50 | Hooks 自動化 |
| 07 | `07-discover-plugins.pptx` | 22 | 探索並安裝 Plugins |

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
2ae41d9 feat: add 4 new PPTX presentations (01/03/05/07) + layout fixes
bdbfccb fix(layout): 06-hooks 多張投影片底部重疊 + 00-overview Slide 23 箭頭
aa46fc5 fix(layout): fix text overflow on 4 problem slides
39cea39 docs: update author name to Kenny Kang
52cdeb4 build: add Python scripts to regenerate PPTX presentations
73d38f5 feat: add 4 PowerPoint presentations of the learning series
bf1011c docs: add 8 markdown files of the complete Claude Code learning series
8c54682 chore: initial commit with .gitignore and README
```

### 2.5 已修正的版面問題
**2026/01（初版）**：
- **06-hooks.pptx**：19 張版面問題（已完成）
- **00-overview.pptx Slide 23**：箭頭修正（用 RIGHT_ARROW 三角形）

**2026/08（新增 4 份簡報時）**：
- **21 個 code 框高度不足** → 調整 code 框高度 / 縮小字體 / 精簡內容
- **01-S27** 標題被 code 框蓋住 → 重新分配版面
- **01-S16** 卡片重疊 → 縮小卡片高度 + 合併 callout
- **額外修正的 8 個 borderline slides**（S30, S31, S10, S18, S20, S21 等）

---

## 3. 關鍵文件和位置

### 3.1 倉庫結構（位於 `/home/elan/pi-proj/`）
```
pi-proj/
├── README.md                    ← 專案說明（必讀）
├── HANDOFF.md                   ← 本文件
├── .gitignore                   ← 忽略 .pptx-venv/、__pycache__/ 等
├── 00-claude-code-plugins-series.md
├── 01-plugin-marketplaces.md
├── 02-plugins.md
├── 03-plugins-reference.md
├── 04-skills.md
├── 05-subagents.md
├── 06-hooks.md
├── 07-discover-plugins.md
├── 00-overview.pptx
├── 01-plugin-marketplaces.pptx
├── 02-plugins.pptx
├── 03-plugins-reference.pptx
├── 04-skills.pptx
├── 05-subagents.pptx
├── 06-hooks.pptx
├── 07-discover-plugins.pptx
├── _pptx_helpers.py
├── _make_00_overview.py
├── _make_01_marketplaces.py
├── _make_02_plugins.py
├── _make_03_plugins_reference.py
├── _make_04_skills.py
├── _make_05_subagents.py
├── _make_06_hooks.py
├── _make_07_discover_plugins.py
└── .pptx-venv/                  ← Python 虛擬環境（已 .gitignore）
```

### 3.2 環境建置
```bash
# Python 3.11+ + uv 必要
uv venv .pptx-venv --python 3.11
uv pip install --python .pptx-venv/bin/python python-pptx
```

### 3.3 重新生成所有簡報
```bash
cd /home/elan/pi-proj
.pptx-venv/bin/python _make_00_overview.py
.pptx-venv/bin/python _make_01_marketplaces.py
.pptx-venv/bin/python _make_02_plugins.py
.pptx-venv/bin/python _make_03_plugins_reference.py
.pptx-venv/bin/python _make_04_skills.py
.pptx-venv/bin/python _make_05_subagents.py
.pptx-venv/bin/python _make_06_hooks.py
.pptx-venv/bin/python _make_07_discover_plugins.py
```

### 3.4 GitHub 認證
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

### 4.2 Python 環境限制
- 環境：`.pptx-venv/`（不要 commit，已在 .gitignore）
- 沒有 root 權限（無法 apt install）；用 `uv` 管理套件
- 沒有 `pip` 直接可用，必須透過 `uv pip install`

### 4.3 PPTX 設計陷阱（重要！）

**必須遵守的設計原則**：
- 箭頭統一用 `MSO_SHAPE.RIGHT_ARROW` 三角形，**不要用 `add_connector(1, ...)`**
- 文字框 `add_text_block` **不會自動調整高度**，必須手動算空間
- code block 字體大小與可容納行數（基於實際測試）：
  - 12pt → 約 0.20"/行
  - 11pt → 約 0.18"/行
  - 10pt → 約 0.17"/行
  - 9pt → 約 0.15"/行
  - 8pt → 約 0.14"/行
- 公式：**所需高度 = N × 行高 + 0.2"（上下 margin）**
- 兩欄（`add_two_column_compare`）至少 1.6" 才能裝 3 個 bullet

**驗證 code 框容量的腳本模式**：
```python
from pptx import Presentation
LINE_HEIGHTS = {12: 0.20, 11: 0.18, 10: 0.17, 9: 0.15, 8: 0.14, 7: 0.13, 13: 0.22}
prs = Presentation('xxx.pptx')
for slide in prs.slides:
    for shape in slide.shapes:
        # 找出黑色矩形配對的 textbox
        # 計算 n_lines × line_height + 0.2 vs 實際 height
        # 若 actual < needed，則需要修正
```

### 4.4 修版面問題的標準做法

當發現「字重疊」或「code 框字溢出」時，依序嘗試：
1. **加大 code 框高度**（必要時 0.3-0.5"）
2. **縮小 code 內字體**（10→9pt 仍可讀；8pt 為下限）
3. **把後續元素往下挪**
4. **精簡內容**（刪除次要 metadata、合併陣列為單行）
5. **兩欄高度 1.6"+**（1.5" 不夠裝 3 個 bullet）

### 4.5 版面重疊問題的常見原因
- 上下元素的 `top + height` 與下一個元素的 `top` 重疊
- 解決方法：先計算所有元素的 bottom，找出重疊處，然後下移後者

---

## 5. 已確認結論

1. ✅ **8 份 Markdown 內容完整**，整理自 code.claude.com/docs 官方文件
2. ✅ **8 份 PPTX 可在 Microsoft PowerPoint 2007+ 開啟**（`file xxx.pptx` 確認）
3. ✅ **06-hooks.pptx 修正 19 張版面問題**（已 commit `bdbfccb`）
4. ✅ **00-overview.pptx Slide 23 箭頭修正**（用 RIGHT_ARROW 三角形）
5. ✅ **Git 倉庫**：[kcf7012/pi-proj](https://github.com/kcf7012/pi-proj)，main branch 最新 commit `2ae41d9`
6. ✅ **README 整理人**：「Kenny Kang」
7. ✅ **GitHub 認證**：`gh auth login` 完成（kcf7012）
8. ✅ **4 份新簡報完成**（01/03/05/07）+ 修正 21 個 code 框高度 + 2 個版面重疊 + 8 個 borderline
9. ✅ **失敗工具已刪除**（`_analyze_*.py` / `_postprocess_fix_overflow.py`）

---

## 6. 已完成項目（2026/08）

### 6.1 4 份新簡報
- ✅ `01-plugin-marketplaces.md` 對應 PPTX（35 張）
- ✅ `03-plugins-reference.md` 對應 PPTX（45 張）
- ✅ `05-subagents.md` 對應 PPTX（30 張）
- ✅ `07-discover-plugins.md` 對應 PPTX（22 張）

### 6.2 版面修正
- ✅ 21 個 code 框高度不足（見 §2.5）
- ✅ 01-S27 標題被蓋（重分配版面）
- ✅ 01-S16 卡片重疊（縮小 + 合併 callout）

### 6.3 工具清理
- ✅ 刪除 `_analyze_layout.py`
- ✅ 刪除 `_analyze_overflow.py`
- ✅ 刪除 `_postprocess_fix_overflow.py`

### 6.4 文檔更新
- ✅ README.md 加入 4 份新 PPTX 條目
- ✅ HANDOFF.md（本文）反映最終狀態

---

## 7. 不要重複做的事情

### ❌ 不要重建 `_postprocess_fix_overflow.py`
- 它會**誤判版面**（把所有文字框都當溢位）
- 結果是縮小字體或擴大框，反而讓版面變更糟
- 正確做法：直接改 `_make_*.py` 重跑

### ❌ 不要用 connector 畫箭頭
- `add_connector(1, ...)` 在 PowerPoint 中會被自動繞路
- 00-overview Slide 23 已發生過此問題，已改用 `RIGHT_ARROW` 三角形
- 後續如需箭頭，統一用 `MSO_SHAPE.RIGHT_ARROW`

### ❌ 不要把 `.pptx-venv/` commit
- 已加入 `.gitignore`，但要確認不要用 `git add -f`

### ❌ 不要分開 commit .py 與 .pptx
- PPTX 是 .py 產生的，但每次改完 .py 都會重新生成 .pptx
- 兩者必須**一起**進版控（否則下次重跑會覆蓋掉 PPTX 的修正）

### ❌ 不要在沒驗證版面就 commit 新簡報
- 新增簡報前先看 §4.3 設計原則
- 跑完 `.py` 後用 python-pptx 驗證每個 code 框容量（見 §4.3 驗證腳本）
- 必要時開啟 PowerPoint 視覺確認

---

## 8. 未來維護建議

### 8.1 內容更新（每 3-6 個月）
- Claude Code 官方文件持續更新，Markdown 內容可能過時
- 建議每 3 個月 review 一次：
  - 對照 `https://code.claude.com/docs/zh-TW/` 官方文件
  - 檢查 `v2.1.x` 版本號是否需要更新
  - 同步更新 Markdown 與 PPTX

### 8.2 簡報更新流程
1. 修改對應的 `_make_XX_*.py`
2. 跑 `.pptx-venv/bin/python _make_XX_*.py` 重新生成
3. **必須視覺驗證**（用 LibreOffice 或 PowerPoint 開啟）
4. 確認無誤後 commit（`.py` 與 `.pptx` 一起）

### 8.3 新增系列（未來如需）
- 在 `_pptx_helpers.py` 已建立的 helper 上擴充
- 套用 §4 設計原則
- 跑驗證腳本檢查 code 框容量
- 視覺驗證後 commit

### 8.4 在 GitHub 建立 Issues（建議）
- 為「未來更新計劃」建立對應 issue，方便追蹤
- 例如：「追蹤 Claude Code v2.2 變更」「新增教學影片連結」

---

## 附錄：常用指令速查

### 環境與簡報生成
```bash
# 環境
cd /home/elan/pi-proj
source .pptx-venv/bin/activate  # 或直接用 .pptx-venv/bin/python

# 重新生成單一簡報
.pptx-venv/bin/python _make_01_marketplaces.py

# 驗證 PPTX
file *.pptx                       # 確認 PowerPoint 2007+ 格式
.pptx-venv/bin/python -c "from pptx import Presentation; print(len(Presentation('06-hooks.pptx').slides))"

# 驗證 code 框容量
.pptx-venv/bin/python <<'EOF'
from pptx import Presentation
LINE_HEIGHTS = {12: 0.20, 11: 0.18, 10: 0.17, 9: 0.15, 8: 0.14, 7: 0.13}
prs = Presentation('xxx.pptx')
# ... (見 §4.3 驗證腳本)
EOF
```

### Git 操作
```bash
git status
git add -A                          # 注意：.pptx-venv 已在 .gitignore
git commit -m "feat: ..."
git push
gh auth login --web                 # 認證過期時重新登入
```

---

**Handoff 結束。** 本系列已完整交付，所有目標達成。下一個任務接手者可從「未來維護建議」（§8）或 GitHub Issues 開始。
