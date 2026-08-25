# learn2deck 技能包 — Agent 智能體補充規劃

> **目的**：回答「是否需要 Agent 智能體」以及「如何整合」
> **狀態**：草案 v0.1（待 review）
> **建立日期**：2026/08

---

## 0. 為什麼需要 Agent？

目前 spec（`learn2deck-spec.md`）的 4 層架構都是**純規則式**：

| 限制 | 範例 |
|------|------|
| Markdown 推斷靠啟發式 | 「標題含『目標』就算 objectives」— 但如果是「學習目標與注意事項」呢？ |
| 驗證只能「提示」 | 「code 框裝不下」— 但需要人工去改內容 |
| 版型固定 | 使用者要懂 `title_table` vs `title_content` 才能用 |
| 沒有內容理解 | 「這段文字太技術、適合什麼受眾？」— 完全沒考慮 |

**Agent 智能體**可以補這些洞，但要先回答幾個關鍵問題。

---

## 1. 三個關鍵問題

### Q1: Agent 在哪裡介入？

**選項 A — 完全自動化（end-to-end AI）**
```
URL/文件 → [LLM 全程] → PPTX
```
- LLM 讀懂所有內容，自動決定章節、版型、風格、簡化文字
- **優點**：使用者門檻最低
- **缺點**：不可預測、難除錯、成本高

**選項 B — 工具輔助（rule + AI assist）** ← **推薦**
```
URL/文件 → [規則解析] → [AI 增強] → PPTX
              ↓             ↓
          結構骨架      內容優化/版型建議/錯誤修正
```
- 規則式做確定性的工作（解析、版面計算）
- LLM 做需要判斷的工作（內容理解、語意分類、文字優化）
- **優點**：可預測 + 智能、容易除錯、成本可控
- **缺點**：架構稍複雜

**選項 C — 選用性增強（opt-in AI）**
```
URL/文件 → [純規則] → PPTX (預設)
              ↓
           --ai-assist → LLM 協助 (可選)
```
- 預設不呼叫 LLM（純本地、零成本）
- 加 `--ai-assist` 才啟用 AI 功能
- **優點**：最低成本、漸進式採用
- **缺點**：功能分兩套，使用者要理解

### Q2: Agent 做哪些事？

建議的 6 個 Agent 能力（**全部 opt-in**，沒啟用就跟目前 spec 一樣）：

| # | 能力 | 觸發時機 | 預估 LLM call |
|---|------|---------|--------------|
| **A1** | 內容分類 | Markdown 推斷信心度低時 | 1 |
| **A2** | 文字精簡 | 驗證發現「code 框裝不下」 | 1-3 |
| **A3** | 自動選版型 | 使用者沒指定 `slide_type` | 1 |
| **A4** | 風格推薦 | `--theme auto` | 1 |
| **A5** | 章節規劃 | 從「無結構 Markdown」產生簡報大綱 | 1-2 |
| **A6** | 內容審查 | 產出後的品質把關 | 1 |

**A1 內容分類範例**：
```yaml
# 純規則無法判斷的章節
## 配置與測試  # 是「教學步驟」(title_content) 還是「疑難排解」(callout)？
# LLM 可根據後續內容判斷
```

**A2 文字精簡範例**：
```python
# 驗證失敗
"code 框 11 行 @ 10pt 需要 2.07"，但只有 1.85"

# LLM 介入
prompt = f"""
以下 code 框內容塞不下，請精簡到 9 行以內、保持語意完整：
{code_content}
"""
# LLM 回傳精簡版，重新驗證
```

**A5 章節規劃範例**：
```yaml
# 輸入：2000 行的 tutorial.md，無 frontmatter
# 純規則會產生 50+ 張簡報（太多）
# LLM 介入：
prompt = f"""
將以下 Markdown 整理成簡報大綱（最多 20 章節，每章節 3-5 張投影片）：
{markdown_content}
"""
# 輸出 YAML outline，符合 spec 格式
```

### Q3: 用哪個 LLM？

3 個選項：

**選項 A — 整合 Claude Code Agent SDK**
- 直接用 Claude Code 內建的 `claude` CLI / Agent SDK
- **優點**：品質最好、安全性最高、與 Claude Code Skill 整合最自然
- **缺點**：需要 Claude Code 環境、API key
- **推薦用於**：所有 Agent 功能

**選項 B — 支援多家 LLM（OpenAI / Anthropic / 本地）**
- 用 LiteLLM 或 LangChain 抽象層
- **優點**：彈性高、可離線使用 Ollama
- **缺點**：品質不一致、設定複雜
- **推薦用於**：v2.0+ 進階功能

**選項 C — 完全本地（Ollama / llama.cpp）**
- 完全離線、零 API 成本
- **優點**：隱私、成本
- **缺點**：品質較弱、需要硬體
- **推薦用於**：特殊場景（v2.0+）

**推薦 v1.0 用 A，v2.0 加 B 為選項**

---

## 2. 推薦方案：選項 B（工具輔助）+ Q3-A（Claude）

### 2.1 架構擴充

把目前的 4 層架構擴充為 5 層：

```
┌─────────────────────────────────────────┐
│  Layer 5: Agent Layer (智能體)          │  ← 新增：opt-in
│  - 內容分類 / 文字精簡 / 版型選擇       │
│  - 章節規劃 / 風格推薦 / 品質審查       │
├─────────────────────────────────────────┤
│  Layer 4: Style Themes (風格主題)        │
├─────────────────────────────────────────┤
│  Layer 3: Slide Builders (投影片建構)    │
├─────────────────────────────────────────┤
│  Layer 2: Content Model (內容模型)       │
├─────────────────────────────────────────┤
│  Layer 1: Validation (品質驗證)          │
└─────────────────────────────────────────┘
```

### 2.2 Agent 介面設計

```python
# learn2deck/agent/base.py
from abc import ABC, abstractmethod
from typing import Optional, List
from dataclasses import dataclass

@dataclass
class AgentContext:
    deck_spec: DeckSpec
    markdown_content: str
    validation_report: Optional[ValidationReport] = None
    available_themes: List[str] = None
    user_preferences: dict = None  # 受眾、長度、風格偏好

class BaseAgent(ABC):
    """所有 Agent 的基底類別"""
    
    @abstractmethod
    async def classify_content(self, context: AgentContext) -> dict:
        """A1: 分類不明確的章節"""
        pass
    
    @abstractmethod
    async def simplify_text(self, text: str, target_lines: int) -> str:
        """A2: 精簡文字到指定行數"""
        pass
    
    @abstractmethod
    async def suggest_layout(self, content: str) -> SlideType:
        """A3: 為內容建議最適版型"""
        pass
    
    @abstractmethod
    async def recommend_theme(self, content_summary: str) -> str:
        """A4: 推薦風格主題"""
        pass
    
    @abstractmethod
    async def plan_outline(self, markdown: str, max_slides: int) -> DeckSpec:
        """A5: 從無結構 Markdown 規劃簡報大綱"""
        pass
    
    @abstractmethod
    async def review_quality(self, deck_spec: DeckSpec) -> List[str]:
        """A6: 內容品質審查（不只是版面）"""
        pass
```

### 2.3 實作：ClaudeAgent

```python
# learn2deck/agent/claude.py
import anthropic

class ClaudeAgent(BaseAgent):
    """使用 Claude API 的 Agent 實作"""
    
    def __init__(self, api_key: str = None, model: str = "claude-sonnet-4-5"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
    
    async def simplify_text(self, text: str, target_lines: int) -> str:
        prompt = f"""你是簡報內容精簡助手。

任務：將以下內容精簡到 {target_lines} 行以內（保持 markdown 格式），同時：
1. 保留所有關鍵技術資訊（API 名稱、版本、參數）
2. 移除冗餘的修飾語和重複資訊
3. 如果是程式碼：保留語意但縮短註解和換行
4. 如果是表格：合併相似列

原始內容：
```
{text}
```

請只回傳精簡後的內容，不要加任何說明。"""
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    
    async def suggest_layout(self, content: str) -> SlideType:
        prompt = f"""你是簡報版型顧問。根據以下內容，建議最適合的投影片版型。

版型選項：
- cover: 封面
- objectives: 學習目標
- section: 章節分隔
- title_content: 標題+純文字/bullet
- title_table: 標題+表格
- title_code: 標題+程式碼
- two_column: 雙欄對比
- grid_cards: 網格卡片
- callout: 純提示框
- summary: 重點回顧

內容：
{content[:2000]}

請只回傳一個版型名稱（例如：title_table），不要加說明。"""
        # ... call Claude API
```

### 2.4 整合進 build 流程

```python
# learn2deck/build.py
def build_deck(
    source: str,
    output: str,
    theme: str = "claude-orange",
    agent: Optional[BaseAgent] = None,  # ← 沒給就完全本地
    ai_assist: bool = False,             # ← CLI 旗標
):
    # 1. 解析內容（純規則）
    deck = parse_content(source)
    
    # 2. 驗證（純規則）
    issues = validate(deck)
    
    # 3. AI 增強（如果有 agent 且 ai_assist=True）
    if agent and ai_assist:
        deck = _ai_enhance(deck, agent, issues)
    
    # 4. 產出 PPTX
    pptx = render_to_pptx(deck, theme)
    
    # 5. 最終驗證
    final_issues = validate(pptx)
    return pptx, final_issues


def _ai_enhance(deck, agent, issues):
    """用 Agent 自動修正內容問題"""
    for issue in issues:
        if issue.rule == "R1" and issue.type == "code_overflow":
            # LLM 精簡 code 框內容
            new_content = await agent.simplify_text(
                issue.content, 
                target_lines=issue.suggested_lines
            )
            issue.slide.update_body(new_content)
        
        elif issue.rule == "R4" and issue.type == "low_confidence_layout":
            # LLM 推薦版型
            new_type = await agent.suggest_layout(issue.content)
            issue.slide.type = new_type
    
    return deck
```

### 2.5 CLI 整合

```bash
# 預設：純本地，無 LLM
learn2deck build input.md -o output.pptx

# 啟用 AI 增強
learn2deck build input.md -o output.pptx --ai-assist

# 指定 AI 處理特定問題
learn2deck build input.md -o output.pptx --ai-assist --ai-tasks simplify,layout

# 完整 AI 規劃（從無結構 Markdown 自動產生大綱）
learn2deck build unstructured.md -o output.pptx --ai-plan

# AI 品質審查
learn2deck build input.md -o output.pptx --ai-review
```

### 2.6 成本與效能預估

| 任務 | LLM 輸入 | LLM 輸出 | 預估時間 | 預估成本 (Claude Sonnet) |
|------|---------|---------|---------|------------------------|
| A1 分類 | ~2K tokens | ~50 tokens | 2-3s | $0.01 |
| A2 精簡 | ~1K tokens | ~500 tokens | 3-5s | $0.015 |
| A3 版型 | ~2K tokens | ~10 tokens | 1-2s | $0.005 |
| A4 風格 | ~500 tokens | ~10 tokens | 1-2s | $0.003 |
| A5 章節規劃 | ~10K tokens | ~2K tokens | 10-15s | $0.10 |
| A6 審查 | ~5K tokens | ~500 tokens | 5-8s | $0.03 |

**一張 35 投影片的簡報如果全部啟用 AI**：約 $0.5-1.0，10-30 秒

---

## 3. 在 Claude Code Skill 系統中如何運作？

### 3.1 Skill 描述

```yaml
---
name: learn2deck
description: |
  從結構化 Markdown 或 YAML 大綱產生符合設計風格的 PPTX 簡報。
  
  智慧功能（需啟用）：
  - 自動內容分類與版型選擇
  - 文字自動精簡（code 框裝不下時）
  - 章節規劃（從無結構 Markdown 產生大綱）
  - 風格推薦
  
  Use when: 使用者要從 Markdown 教材、學習筆記、技術文件產生簡報
allowed-tools: Bash, Read, Write, Edit, WebFetch
model: claude-sonnet-4-5
---

# learn2deck

## 快速使用
```bash
learn2deck build input.md -o output.pptx
```

## 智慧增強
```bash
# 啟用 AI 增強（需要 ANTHROPIC_API_KEY 環境變數）
learn2deck build input.md -o output.pptx --ai-assist

# 自動章節規劃
learn2deck build tutorial.md -o output.pptx --ai-plan
```

## 智慧判斷與過濾的時機
...
```

### 3.2 對話觸發範例

使用者：「幫我把這份 tutorial 變成簡報，但太長了，重點就好」

Claude（skill 觸發）：
1. 讀取 tutorial.md
2. 判斷需要 `A5 章節規劃`（太長、需要挑重點）
3. 呼叫 LLM：「這份 5000 行的 tutorial，請規劃成 20 張投影片的大綱」
4. 拿到 outline → 用規則式 build → 驗證
5. 如果有 code 框裝不下 → 呼叫 A2 精簡
6. 產出 PPTX，告訴使用者：「已自動挑選 8 個重點章節、code 框自動精簡 3 處」

---

## 4. 安全與控制

### 4.1 預設行為

- **不啟用 AI**：所有 LLM call 都需 `--ai-assist` 或 `--ai-plan` 明示開啟
- **成本上限**：每次 build 最多 N 次 LLM call（預設 5 次，可設）
- **內容隔離**：LLM 看不到整個專案，只看到傳入的 prompt 內容
- **錯誤降級**：LLM 失敗時自動 fallback 到純規則

### 4.2 使用者控制

```bash
# 完全關閉 AI（預設）
learn2deck build input.md -o output.pptx

# 只在驗證失敗時用 AI 修正
learn2deck build input.md -o output.pptx --ai-assist --ai-on-validation-error

# 設定成本上限
learn2deck build input.md -o output.pptx --ai-assist --max-llm-cost 0.50

# 用本地 Ollama
learn2deck build input.md -o output.pptx --ai-assist --llm ollama:llama3
```

### 4.3 Prompt 安全

- 內容中若含敏感資訊（API key、密碼），可加 `--sanitize` 自動遮罩
- 輸出會過濾掉 prompt injection 嘗試

---

## 5. 開發階段（更新版）

### v1.0 MVP（4-6 週）— 純規則版
- 4 層架構（無 Agent）
- 8 份現有 PPTX 重現為成功標準

### v1.1（+2 週）— 加入基本 Agent
- 實作 `ClaudeAgent`
- 啟用 A2 文字精簡（最實用）
- 啟用 A3 版型選擇（次實用）
- CLI 旗標 `--ai-assist`

### v1.2（+2 週）— 加入進階 Agent
- 啟用 A1 內容分類
- 啟用 A4 風格推薦
- 啟用 A6 品質審查

### v2.0（+4 週）— 完整 Pipeline
- 啟用 A5 章節規劃（從 URL/Markdown 自動產生簡報）
- 支援多家 LLM
- 加入 prompt 安全機制

---

## 6. 對原本 spec 的影響

需要更新 `learn2deck-spec.md` 的部分：

| 位置 | 變更 |
|------|------|
| §1.2 目標 | 新增「智慧增強（opt-in）」 |
| §2.2 範圍分層 | 新增 Layer 5 Agent |
| §4.2 輸入格式 | 說明 LLM 可補完無結構輸入 |
| §5 Builders | 說明 LLM 可協助選版型 |
| §6 Themes | 新增 A4 風格推薦 |
| §7 CLI | 新增 `--ai-assist` 等旗標 |
| §8 程式碼組織 | 新增 `agent/` 模組 |
| §9 開發階段 | 拆分 MVP/Agent 兩個時程 |

---

## 7. 開放問題（請 review）

1. **整合深度**：選項 A/B/C 中選哪個？推薦 B（工具輔助）
2. **預設行為**：v1.1 預設啟用 AI 還是 opt-in？推薦 opt-in（保守）
3. **LLM 選擇**：v1.1 鎖定 Claude 還是多家？推薦鎖定 Claude（最簡單）
4. **優先功能**：A1-A6 中哪個最重要？推薦先做 A2（精簡）和 A3（版型）
5. **成本控制**：是否需要 `--max-llm-cost` 旗標？推薦有
6. **隱私**：是否需要 `--sanitize` 自動遮罩敏感資訊？v2.0 再說

---

## 8. 結論

**加 Agent 是對的決定**，原因：
- 大幅降低使用者門檻
- 處理目前純規則無法處理的灰色地帶
- 讓 spec 從「工具」進化為「助手」
- 為未來 v2.0 的端到端 pipeline 鋪路

**但要分階段**，不要 v1.0 就想做完所有事。建議：

```
v1.0：純規則（先把工具做扎實）
v1.1：+ A2 精簡 + A3 版型（最實用）
v1.2：+ A1 分類 + A4 風格 + A6 審查
v2.0：+ A5 章節規劃 + 多 LLM 支援
```

**請確認是否採納此補充規劃**。如果同意，我會：
1. 把內容整合到 `learn2deck-spec.md` 主文件
2. 重新分章節
3. 開始 v1.0 純規則版實作
