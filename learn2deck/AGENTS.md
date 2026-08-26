# AGENTS.md — learn2deck 開發者指南

> **給 AI 助手（Claude、GPT 等）與人類貢獻者的工作規則**
>
> 本文件規範 learn2deck 套件的開發流程，包含分支策略、Python 編碼風格、Git commit 規範。

---

## 1. 分支開發工作流

### 1.1 核心原則

> **永遠不要直接在 `main` 分支開發。所有改動必須開分支。**

`main` 分支只保留：
- 已完成且通過 CI 的功能
- 已發佈的版本（v1.0.0、v1.1.0 等）
- 已合併的 PR

### 1.2 分支命名規範

使用 **kebab-case**，前綴表示類型：

| 前綴 | 用途 | 範例 |
|:-----|:-----|:-----|
| `feat/` | 新功能 | `feat/phase-12-agent-integration` |
| `fix/` | Bug 修正 | `fix/grid-cards-overflow-r2` |
| `docs/` | 純文件 | `docs/update-readme-examples` |
| `refactor/` | 重構（不改行為）| `refactor/extract-builder-base-class` |
| `test/` | 測試補強 | `test/add-skill-trigger-edge-cases` |
| `chore/` | 雜務（依賴更新、設定檔）| `chore/bump-pydantic-2.5` |
| `hotfix/` | 緊急修正 main 上的 bug | `hotfix/r5-zip-validation-crash` |

### 1.3 工作流程

```bash
# 1. 確認在 main 且最新
git checkout main
git pull origin main

# 2. 從最新 main 開新分支
git checkout -b feat/<name>

# 3. 開發、commit（見 §3 commit 規範）
git add <files>
git commit -m "feat(learn2deck): <description>"

# 4. 跑完整測試確認沒破壞
/home/elan/pi-proj/.pptx-venv/bin/python -m pytest tests/

# 5. 確認 diff 乾淨
git status
git diff main --stat

# 6. Push 並開 PR（或合併回 main）
git push -u origin feat/<name>
```

### 1.4 完成分支後

```bash
# 合併到 main（推薦用 fast-forward 或 --no-ff 看團隊偏好）
git checkout main
git merge --no-ff feat/<name>
git push origin main

# 刪除本地分支
git branch -d feat/<name>

# 刪除遠端分支（如已 push）
git push origin --delete feat/<name>
```

### 1.5 禁止事項

- ❌ **直接在 main commit**（除非是 hotfix 文件 typo 等極小變更）
- ❌ **commit 大量不相關的改動**（拆分成多個 commit 或多個分支）
- ❌ **使用 force push 改寫已 push 的歷史**（會影響協作者）
- ❌ **把分支留在本地太久**（完成後立即合併或刪除）

---

## 2. Python 編碼規則

### 2.1 環境

- **Python 版本**：≥ 3.11（見 `pyproject.toml` `requires-python`）
- **虛擬環境**：`/home/elan/pi-proj/.pptx-venv/`（已建立）
- **套件管理**：使用 `pip`（目前專案未引入 poetry / uv）
- **指令執行**：用絕對路徑 `/home/elan/pi-proj/.pptx-venv/bin/python` 避免 PATH 問題

### 2.2 程式碼風格

- **Linter**：[ruff](https://docs.astral.sh/ruff/)（見 `pyproject.toml` §tool.ruff）
- **行長上限**：100 字元（已忽略 E501，由 formatter 控制）
- **Lint 規則**：`E`, `F`, `W`, `I`, `N`, `UP`（pycodestyle + pyflakes + isort + pep8-naming + pyupgrade）
- **型別標註**：建議加，但非強制（CLI 與 builder 入口必加）
- **文件字串**：模組、class、public function 都建議寫（中文或英文皆可，與專案其他部分一致）

```bash
# 跑 linter
/home/elan/pi-proj/.pptx-venv/bin/python -m ruff check learn2deck/

# 自動修正
/home/elan/pi-proj/.pptx-venv/bin/python -m ruff check --fix learn2deck/
```

### 2.3 命名規範

| 對象 | 規範 | 範例 |
|:-----|:-----|:-----|
| 模組 | snake_case | `code_capacity.py` |
| Class | PascalCase | `CodeCapacityValidator` |
| Function | snake_case | `validate_deck()` |
| 變數 | snake_case | `slide_num` |
| 常數 | UPPER_SNAKE | `SAFE_BOTTOM = 7.0` |
| 私有 | _leading_underscore | `_check_slide()` |
| Enum value | UPPER_SNAKE | `SlideType.TITLE_TABLE` |
| Enum 字串值 | snake_case（與 YAML 對應）| `SlideType.TITLE_TABLE.value == "title_table"` |

### 2.4 型別標註風格

```python
# ✅ 推薦：使用 | 表示 union（Python 3.10+）
def find_skill_dir() -> Path | None:
    ...

# ✅ 推薦：泛型用 builtin
def get_items() -> list[str]:
    ...

# ✅ 推薦：Optional 用 | None
def install_skill(target: Path | None = None) -> Path:
    ...

# ✅ 推薦：dataclass + field(default_factory=...)
@dataclass
class Issue:
    rule: str
    severity: Severity = Severity.ERROR
    details: dict[str, Any] = field(default_factory=dict)
```

### 2.5 Docstring 風格

```python
def validate(self, prs: "Presentation") -> list[Issue]:
    """驗證 PPTX 投影片

    Args:
        prs: 已載入的 Presentation 物件

    Returns:
        Issue 清單（空 list 代表 OK）
    """
```

- **第一行**：簡短一句話總結
- **Args**：參數說明（每個一行）
- **Returns**：回傳值說明
- **Raises**：例外說明（選用）

### 2.6 測試規範

- **測試框架**：[pytest](https://docs.pytest.org/) ≥ 7.0
- **測試檔案命名**：`test_<module>.py`
- **測試函式命名**：`test_<functionality>` 或 `test_<scenario>`
- **測試 class 命名**：`Test<X>`（如 `TestR1CodeCapacity`）
- **目標覆蓋率**：核心模組 ≥ 80%
- **必須跑的測試**：commit 前必跑

```bash
# 跑全部測試
/home/elan/pi-proj/.pptx-venv/bin/python -m pytest tests/

# 跑特定檔案
/home/elan/pi-proj/.pptx-venv/bin/python -m pytest tests/test_validators.py

# 跑特定測試
/home/elan/pi-proj/.pptx-venv/bin/python -m pytest tests/test_validators.py::TestR1CodeCapacity

# 顯示 verbose
/home/elan/pi-proj/.pptx-venv/bin/python -m pytest tests/ -v
```

### 2.7 設計原則（不要違反）

來源：HANDOFF.md §2.3、§7

- ❌ **不要**用全域顏色常數（已移除）→ 從 `theme.get_color()` 取
- ❌ **不要**把 COVER/SECTION_DIVIDER 改為可在 `build()` 內建立 → 必須透過 `build_full_deck()`
- ❌ **不要**保留 `add_shape()` 回傳的參考長期使用 → 每次從 `slide.shapes` 重拿
- ❌ **不要**把 `lib/` 加進 `.gitignore` → package code 在 `lib/` 下
- ❌ **不要**在 builder 內建新 `SlideType` → 10 種已固定，要新增需先改 spec

---

## 3. Git Commit 規範

### 3.1 Conventional Commits

本專案使用 [Conventional Commits](https://www.conventionalcommits.org/) 風格：

```
<type>(<scope>): <subject>

<body>

<footer>
```

### 3.2 Type（必填）

| Type | 用途 | 範例 |
|:-----|:-----|:-----|
| `feat` | 新功能 | `feat(learn2deck): add Phase 11 skill integration` |
| `fix` | Bug 修正 | `fix(learn2deck): R5 false positive on empty pptx` |
| `docs` | 純文件（不改程式碼）| `docs(learn2deck): update HANDOFF Phase 11 status` |
| `refactor` | 重構（不改行為）| `refactor(learn2deck): extract theme loader to core` |
| `test` | 測試補強 | `test(learn2deck): add skill trigger edge cases` |
| `chore` | 雜務 | `chore(learn2deck): bump pydantic 2.5` |
| `release` | 版本發佈 | `release: v1.1.0 - skill integration` |
| `perf` | 效能改進 | `perf(learn2deck): cache theme parse` |
| `style` | 格式（不改語意）| `style(learn2deck): apply ruff fixes` |

### 3.3 Scope（選用但推薦）

| Scope | 對象 |
|:------|:-----|
| `learn2deck` | 套件本體（CLI、core、builders、parsers、validators）|
| `learn2deck-spec` | 規格文件 |
| `learn2deck-skill` | SKILL.md、references/、templates/（Phase 11+）|
| （省略） | 多個範圍或不相關時 |

### 3.4 Subject（必填）

- 用祈使句（"add" 而非 "added"）
- 不大寫開頭（首字母小寫）
- 不加句號
- 50 字以內

```bash
# ✅ 好
feat(learn2deck): add skill install command
fix(learn2deck): R5 false positive on empty pptx
docs(learn2deck): update HANDOFF Phase 11 status

# ❌ 不好
feat: Added a new feature.        # 被動、大寫、句號
feat(learn2deck): 修正 bug          # 中文（subject 建議英文）
```

### 3.5 Body（選用）

- 解釋「為什麼」改這個，而非「改了什麼」
- 72 字自動換行
- 與 subject 隔一空行

### 3.6 Footer（選用）

- 引用 issue：`Refs #123`、`Closes #456`
- Breaking change：`BREAKING CHANGE: <說明>`

### 3.7 完整範例

```bash
git commit -m "feat(learn2deck): Phase 11 - Claude skill integration

Phase 11 wraps learn2deck v1.0 CLI as a Claude Code skill with
trigger-based activation, enabling content creators to produce
PPTX decks from natural language requests.

## Deliverables

- SKILL.md (152 lines): Double-layer trigger strategy with 19
  explicit patterns + intent-based fallback
- references/ (1,503 lines total):
  - style-guide.md: Claude orange design system
  - slide-types.md: 10 SlideType quick reference
  - validation-rules.md: R1-R5 detailed rules
  - cli-reference.md: Complete CLI commands and flags
  - troubleshooting.md: 15 FAQ with code examples
- templates/ (521 lines total)
- tests/test_skill_trigger.py (204 lines)

## Test Results

- 243 tests pass
- Trigger matrix: 19/19 cases pass

🤖 Generated with Claude Code

Co-Authored-By: Claude <noreply@anthropic.com>"
```

### 3.8 禁止事項

- ❌ **`git commit --amend` 改寫已 push 的 commit**
- ❌ **合併多個不相關的改動到一個 commit**
- ❌ **commit 訊息用中文 subject**（用英文更通用；body 可中英混用）
- ❌ **空白 commit（無改動）**
- ❌ **commit 包含機密資訊（API key、密碼）**

---

## 4. 開發檢查清單

每次完成一個工作項目，commit 前確認：

- [ ] 在正確的分支上（不是 main）
- [ ] 所有 Python 檔案通過 ruff
- [ ] 所有測試通過（`pytest tests/`）
- [ ] 沒有引入新的依賴（除非必要，且更新 `pyproject.toml`）
- [ ] 新功能有對應測試
- [ ] CHANGELOG 或 HANDOFF.md 更新（如適用）
- [ ] commit 訊息遵循 §3 規範
- [ ] 沒有 `print()` 除錯輸出殘留
- [ ] 沒有 TODO / FIXME 未處理（除非有對應 issue）

---

## 5. 緊急狀況處理

### 5.1 在 main 上 commit 了怎麼辦？

```bash
# 撤銷最後一個 commit（保留改動在工作目錄）
git reset --soft HEAD~1

# 撤銷並清空改動（⚠️ 危險）
git reset --hard HEAD~1

# 如果已 push：用 revert 而非 reset
git revert HEAD
git push origin main
```

### 5.2 merge 衝突

```bash
git fetch origin
git merge origin/main  # 或 git rebase origin/main

# 解衝突後
git add <resolved-files>
git commit   # 完成 merge
```

### 5.3 不小心刪除分支

```bash
# 從 reflog 找回
git reflog
git checkout -b feat/<name> <commit-sha>
```

---

## 6. 給 AI 助手的特別指示

如果你正在讀這份文件的 AI 助手（Claude、GPT 等），請遵守：

1. **永遠先確認分支**：用 `git branch --show-current` 檢查，目前在 main 就要先問使用者要不要開新分支
2. **修改前先看 AGENTS.md 與 HANDOFF.md**：了解專案慣例與歷史決策
3. **不要自動 push**：除非使用者明確要求
4. **不要 force push**：除非使用者明確要求
5. **保留使用者意圖**：使用者說「先這樣」就停下，不要自作主張繼續做
6. **小步提交**：完成一個邏輯單元就 commit，不要累積大量改動
7. **保留 context**：在 commit 訊息詳述「為什麼」這樣改，方便未來 review

---

## 7. 參考資源

- HANDOFF.md — 接手者導引、開發計劃
- README.md — 套件使用說明
- pyproject.toml — 套件設定（依賴、lint、test 配置）
- docs/learn2deck-spec.md — 完整規格書
- https://www.conventionalcommits.org/ — Conventional Commits 規範
- https://docs.astral.sh/ruff/ — Ruff linter 文件
