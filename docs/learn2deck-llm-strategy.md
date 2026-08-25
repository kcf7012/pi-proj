# learn2deck — LLM 策略：3.1 vs 3.2 深度分析與建議

> **目的**：回答「是否要支援多家 LLM」的設計決策
> **狀態**：草案 v0.1（待 review）
> **建立日期**：2026/08

---

## 0. 結論先行

**推薦方案：階段性演進，v1.1 鎖定 Claude（3.1），v2.0 再抽象化為 3.2**

理由：
1. v1.0/v1.1 的核心目標是**驗證概念**，品質比彈性重要
2. 抽象化成本（介面設計、相容性測試）很高，**先做一次成功再泛化**
3. 真正需要多家 LLM 的場景是**離線 + 隱私**，這是 v2.0 才有的需求
4. 但**介面設計從一開始就要考慮可擴展**，避免 v2.0 大改

具體策略：
- v1.0：純規則（無 LLM）
- v1.1：**鎖定 Claude**，但介面設計為可替換
- v1.2：仍鎖定 Claude，累積 prompt 經驗
- v2.0：**抽出抽象層**，支援 OpenAI / Ollama / Azure OpenAI

---

## 1. 為什麼不要一開始就做 3.2？

### 1.1 抽象化的真實成本

做 3.2 不只是「多寫幾個 API client」，真正的成本在於：

| 抽象成本 | 具體影響 | 預估工時 |
|---------|---------|---------|
| 介面設計 | 6 個 Agent 方法的統一簽章 | 1-2 週 |
| Prompt 抽象 | 不同 LLM 的 prompt 風格不同 | 2-3 週 |
| Output parsing | 不同 LLM 輸出格式差異 | 2-3 週 |
| 測試覆蓋 | 至少 3 個 LLM × 6 個功能 = 18 種組合 | 2-3 週 |
| 除錯工具 | Token 用量、錯誤追蹤、prompt 版本管理 | 1-2 週 |
| 文檔撰寫 | 使用者要懂每家 LLM 的特性 | 1 週 |
| **總計** | | **10-14 週** |

v1.0 MVP 只要 4-6 週。**先做 3.1 累積經驗**，再做 3.2 才有依據。

### 1.2 Prompt 相容性的真實難度

即使有了抽象層，prompt 在不同 LLM 上表現差異很大：

**同一個 prompt 的可能結果差異**：

```python
# 任務：精簡這段程式碼到 5 行以內
prompt = """請精簡以下 JSON 設定到 5 行以內：

{
  "name": "code-formatter",
  "description": "在保存時自動格式化程式碼",
  "version": "2.1.0",
  "author": { "name": "DevTools Team" },
  "license": "MIT"
}
"""
```

| LLM | 輸出 | 問題 |
|-----|------|------|
| Claude Sonnet 4.5 | 精準 5 行、保留關鍵欄位 | ✅ |
| GPT-4o | 精準 5 行、稍多解釋 | ✅ 但略冗 |
| Claude Haiku 3.5 | 精準 4 行、刪過頭 | ⚠️ 偶爾丟失語意 |
| Ollama Llama 3 8B | 4-6 行、不穩定 | ❌ 需重試 |
| Ollama Qwen 2.5 7B | 中文 prompt 理解差 | ❌ |

**結論**：要保證跨 LLM 品質，需要：
- 多版本 prompt（A/B testing）
- 自動重試 + 品質評分
- 不同 LLM 用不同 prompt 變體

這是**巨大的工程負擔**，不值得 v1.0 投入。

---

## 2. 推薦的階段策略

### 2.1 時程規劃

```
v1.0（4-6 週）
└─ 純規則版，無 LLM
   - 先把工具層做扎實
   - 8 份現有 PPTX 重現為成功標準

v1.1（+2 週，鎖定 Claude）
├─ 介面設計為可替換
├─ 實作 ClaudeAgent
├─ 啟用 A2（精簡） + A3（版型）
└─ 累積 prompt 工程經驗

v1.2（+2 週，仍鎖定 Claude）
├─ A1（分類）+ A4（風格）+ A6（審查）
├─ 完善 prompt 模板庫
└─ 加入 prompt 版本管理

v2.0（+4 週，抽象化）
├─ 抽 BaseLLMClient 抽象層
├─ 實作 OpenAIClient
├─ 實作 OllamaClient
├─ Prompt 適配器
└─ 跨 LLM 測試套件
```

### 2.2 介面從一開始就要設計成可替換

即使 v1.1 只實作 ClaudeAgent，**介面必須抽象**：

```python
# learn2deck/agent/base.py
from abc import ABC, abstractmethod

class BaseLLMAgent(ABC):
    """所有 LLM Agent 的基底"""
    
    @abstractmethod
    async def complete(self, prompt: str, **kwargs) -> str:
        """最底層：發送 prompt 拿回文字"""
        pass
    
    @abstractmethod
    async def classify(self, content: str, options: list[str]) -> str:
        """多選一分類"""
        pass
    
    # ... 其他高階方法

# v1.1 實作
class ClaudeAgent(BaseLLMAgent):
    def __init__(self, api_key: str = None, model: str = "claude-sonnet-4-5"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
    
    async def complete(self, prompt: str, **kwargs) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=kwargs.get("max_tokens", 2000),
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text

# v2.0 才實作
class OpenAIAgent(BaseLLMAgent):
    """GPT-4o / GPT-4o-mini"""
    pass

class OllamaAgent(BaseLLMAgent):
    """本地 Ollama（Llama 3, Qwen, Mistral...）"""
    pass
```

**重點**：
- v1.1 寫 `BaseLLMAgent` 介面 + `ClaudeAgent` 實作
- v2.0 加 `OpenAIAgent` / `OllamaAgent`，**介面不變**
- 所有 Agent 高階方法（A1-A6）**都用 BaseLLMAgent** 呼叫，**不直接用 ClaudeAgent**

### 2.3 Prompt 模板也要可替換

不同 LLM 需要不同 prompt 風格，這是 3.2 的真正麻煩。

**v1.1 策略**：只寫 Claude 優化版 prompt
**v2.0 策略**：每家 LLM 有自己的 prompt 變體

```python
# learn2deck/agent/prompts.py

CLAUDE_PROMPTS = {
    "simplify_text": """你是簡報內容精簡助手。
...（Claude 優化版）
""",
}

# v2.0 才需要
OPENAI_PROMPTS = {
    "simplify_text": """You are a presentation content simplifier.
...（GPT 優化版）
""",
}

OLLAMA_PROMPTS = {
    "simplify_text": """[簡化角色設定]
...（Ollama 優化版，較短、明確指令）
""",
}
```

**解決方法**：
- v1.1：只有 `CLAUDE_PROMPTS`
- v2.0：加 `OPENAI_PROMPTS`、`OLLAMA_PROMPTS`
- 透過 factory method 動態選擇：

```python
class BaseLLMAgent(ABC):
    def get_prompt(self, task: str) -> str:
        prompts = self._load_prompts()
        return prompts[task]
    
    @abstractmethod
    def _load_prompts(self) -> dict:
        """子類別回傳自己的 prompt 字典"""
        pass

class ClaudeAgent(BaseLLMAgent):
    def _load_prompts(self) -> dict:
        return CLAUDE_PROMPTS

class OllamaAgent(BaseLLMAgent):
    def _load_prompts(self) -> dict:
        return OLLAMA_PROMPTS
```

---

## 3. 環境變數設計（`.env`）

### 3.1 v1.1 簡單版

```bash
# .env（v1.1）
LEARN2DECK_LLM_PROVIDER=claude          # 預設值，固定為 claude
ANTHROPIC_API_KEY=sk-ant-xxxxx
LEARN2DECK_LLM_MODEL=claude-sonnet-4-5  # 可選
LEARN2DECK_AI_MAX_COST=1.0              # USD 上限
```

### 3.2 v2.0 多 LLM 完整版

```bash
# .env（v2.0）
# === LLM 提供商切換 ===
LEARN2DECK_LLM_PROVIDER=claude   # claude | openai | ollama | azure

# === Claude 設定 ===
ANTHROPIC_API_KEY=sk-ant-xxxxx
LEARN2DECK_CLAUDE_MODEL=claude-sonnet-4-5

# === OpenAI 設定 ===
OPENAI_API_KEY=sk-xxxxx
LEARN2DECK_OPENAI_MODEL=gpt-4o

# === Ollama 設定（本地） ===
LEARN2DECK_OLLAMA_HOST=http://localhost:11434
LEARN2DECK_OLLAMA_MODEL=llama3:8b

# === Azure OpenAI 設定（企業） ===
AZURE_OPENAI_API_KEY=xxxxx
AZURE_OPENAI_ENDPOINT=https://xxx.openai.azure.com
LEARN2DECK_AZURE_DEPLOYMENT=gpt-4o

# === 通用設定 ===
LEARN2DECK_AI_MAX_COST=1.0
LEARN2DECK_AI_TIMEOUT=30
LEARN2DECK_AI_RETRY=3
LEARN2DECK_AI_SANITIZE=true        # 自動遮罩敏感資訊
```

### 3.3 載入方式

```python
# learn2deck/config.py
from pydantic_settings import BaseSettings
from typing import Literal

class LLMConfig(BaseSettings):
    provider: Literal["claude", "openai", "ollama", "azure"] = "claude"
    
    # Claude
    anthropic_api_key: str | None = None
    claude_model: str = "claude-sonnet-4-5"
    
    # OpenAI
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o"
    
    # Ollama
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "llama3:8b"
    
    # Azure OpenAI
    azure_openai_api_key: str | None = None
    azure_openai_endpoint: str | None = None
    azure_deployment: str = "gpt-4o"
    
    # 通用
    max_cost_usd: float = 1.0
    timeout_sec: int = 30
    max_retries: int = 3
    sanitize: bool = True
    
    class Config:
        env_prefix = "LEARN2DECK_"
        env_file = ".env"
        env_file_encoding = "utf-8"

# 使用
config = LLMConfig()
agent = create_agent(config)  # 根據 provider 自動建立對應的 Agent
```

---

## 4. 切換 LLM 的相容性問題與解法

你問的「prompt 對每個 LLM 解析有差異」是對的。**以下是具體的解法**。

### 4.1 問題：相同 prompt 結果不同

**範例**：

```python
# 同一個 prompt
prompt = """從以下 Markdown 章節判斷是哪種投影片版型。

## 學習目標
- 理解 plugin 概念
- 建立第一個 plugin
- 部署 plugin
"""
```

| LLM | 輸出 | 一致性 |
|-----|------|--------|
| Claude Sonnet | `objectives` | ✅ 100% |
| GPT-4o | `objectives` | ✅ 95% |
| GPT-4o-mini | `objectives` / `title_content` | ⚠️ 70% |
| Llama 3 8B (本地) | 各種 | ❌ 50% |
| Qwen 2.5 7B | `objectives` (中文佳) | ⚠️ 80% |

### 4.2 解法 1：Output Parser + Schema

不依賴 LLM 自覺輸出正確格式，用**結構化輸出**：

```python
# v2.0 設計
from pydantic import BaseModel

class LayoutDecision(BaseModel):
    slide_type: Literal["cover", "objectives", "title_table", ...]
    confidence: float
    reasoning: str

# Claude 用 tool_use
# OpenAI 用 function_calling
# Ollama 用 JSON mode
# 統一用 Pydantic 解析

class BaseLLMAgent(ABC):
    @abstractmethod
    async def structured_decide(
        self, 
        prompt: str, 
        schema: type[BaseModel]
    ) -> BaseModel:
        """用結構化輸出做決策"""
        pass
```

### 4.3 解法 2：品質評分 + 自動重試

```python
async def quality_aware_simplify(agent, text, target_lines):
    for attempt in range(3):
        result = await agent.simplify_text(text, target_lines)
        score = evaluate_quality(result, original=text, target=target_lines)
        if score >= 0.8:  # 品質閾值
            return result
        # 品質不夠，把上次的結果丟回去重試
        text = f"上次的結果不夠好（評分 {score:.2f}），請再精簡：\n{result}"
    return result  # 最後一次不管品質都回傳
```

### 4.4 解法 3：模型分層（不同任務用不同模型）

```python
# .env
LEARN2DECK_CLAUDE_MODEL_FAST=claude-haiku-3-5     # 簡單分類
LEARN2DECK_CLAUDE_MODEL_SMART=claude-sonnet-4-5   # 精簡、規劃
LEARN2DECK_CLAUDE_MODEL_SMARTEST=claude-opus-4    # 品質審查

# 不同任務用不同模型
class SmartAgentRouter:
    def __init__(self, config):
        self.fast = ClaudeAgent(model=config.claude_model_fast)
        self.smart = ClaudeAgent(model=config.claude_model_smart)
        self.smartest = ClaudeAgent(model=config.claude_model_smartest)
    
    async def classify(self, content):
        return await self.fast.classify(content)  # 簡單任務用便宜的
    
    async def simplify(self, text, target):
        return await self.smart.simplify(text, target)  # 中等複雜度
    
    async def review(self, deck):
        return await self.smartest.review(deck)  # 需要高品質
```

### 4.5 解法 4：Fallback 鏈

```python
class FallbackAgent(BaseLLMAgent):
    """自動 fallback 到次選 LLM"""
    
    def __init__(self, primary: BaseLLMAgent, fallback: BaseLLMAgent):
        self.primary = primary
        self.fallback = fallback
    
    async def complete(self, prompt, **kwargs):
        try:
            return await self.primary.complete(prompt, **kwargs)
        except (RateLimitError, APIError) as e:
            log.warning(f"Primary LLM failed: {e}, using fallback")
            return await self.fallback.complete(prompt, **kwargs)

# 設定
primary = ClaudeAgent(api_key=anthropic_key)
fallback = OllamaAgent(model="llama3:8b")  # 離線 fallback
agent = FallbackAgent(primary, fallback)
```

---

## 5. v2.0 多 LLM 支援的具體實作規劃

### 5.1 抽象介面

```python
# learn2deck/llm/base.py
from abc import ABC, abstractmethod
from typing import Type, TypeVar
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

class BaseLLMClient(ABC):
    """所有 LLM 客戶端的基底"""
    
    provider_name: str
    supports_structured_output: bool
    max_context_tokens: int
    
    @abstractmethod
    async def chat(
        self,
        messages: list[dict],
        *,
        max_tokens: int = 2000,
        temperature: float = 0.0,
        **kwargs
    ) -> str:
        """基本對話"""
        pass
    
    @abstractmethod
    async def structured(
        self,
        messages: list[dict],
        schema: Type[T],
        **kwargs
    ) -> T:
        """結構化輸出（Pydantic schema）"""
        pass
    
    @abstractmethod
    async def count_tokens(self, text: str) -> int:
        pass
    
    @abstractmethod
    def get_prompts(self) -> dict:
        """回傳此 LLM 優化過的 prompt 字典"""
        pass


class BaseLLMAgent(BaseLLMClient):
    """高階 Agent（呼叫 BaseLLMClient + 業務邏輯）"""
    
    async def classify_content(self, content, options) -> str:
        prompts = self.get_prompts()
        messages = [
            {"role": "system", "content": prompts["classify_system"]},
            {"role": "user", "content": f"{prompts['classify_user']}\n\n{content}\n\n選項：{options}"}
        ]
        return await self.chat(messages)
    
    async def simplify_text(self, text, target_lines) -> str:
        # ... 類似
        pass
```

### 5.2 各家實作

```python
# learn2deck/llm/claude.py
class ClaudeClient(BaseLLMClient):
    provider_name = "claude"
    supports_structured_output = True
    max_context_tokens = 200_000
    
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-5"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
    
    async def chat(self, messages, **kwargs):
        # 轉換 messages 格式給 Claude
        response = self.client.messages.create(
            model=self.model,
            max_tokens=kwargs.get("max_tokens", 2000),
            messages=messages,
            temperature=kwargs.get("temperature", 0.0),
        )
        return response.content[0].text
    
    async def structured(self, messages, schema, **kwargs):
        # Claude 用 tool_use 實現
        tool = {
            "name": "structured_output",
            "description": "Output structured data",
            "input_schema": schema.model_json_schema()
        }
        response = self.client.messages.create(
            model=self.model,
            max_tokens=kwargs.get("max_tokens", 2000),
            messages=messages,
            tools=[tool],
            tool_choice={"type": "tool", "name": "structured_output"}
        )
        # 從 tool_use 區塊拿 JSON
        tool_input = response.content[0].input
        return schema(**tool_input)
    
    def get_prompts(self) -> dict:
        return CLAUDE_PROMPTS

# learn2deck/llm/openai.py
class OpenAIClient(BaseLLMClient):
    provider_name = "openai"
    supports_structured_output = True
    max_context_tokens = 128_000
    
    async def chat(self, messages, **kwargs):
        # OpenAI 用 chat.completions
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=kwargs.get("max_tokens", 2000),
            temperature=kwargs.get("temperature", 0.0),
        )
        return response.choices[0].message.content
    
    async def structured(self, messages, schema, **kwargs):
        # OpenAI 用 function_calling 或 json_schema
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            response_format={"type": "json_schema", "json_schema": {
                "name": schema.__name__,
                "schema": schema.model_json_schema()
            }}
        )
        return schema.model_validate_json(response.choices[0].message.content)
    
    def get_prompts(self) -> dict:
        return OPENAI_PROMPTS

# learn2deck/llm/ollama.py
class OllamaClient(BaseLLMClient):
    provider_name = "ollama"
    supports_structured_output = False  # 受限
    max_context_tokens = 32_000
    
    def __init__(self, host: str, model: str):
        self.host = host
        self.model = model
    
    async def chat(self, messages, **kwargs):
        # Ollama 用 /api/chat
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.host}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": kwargs.get("temperature", 0.0),
                        "num_predict": kwargs.get("max_tokens", 2000),
                    }
                }
            ) as resp:
                data = await resp.json()
                return data["message"]["content"]
    
    async def structured(self, messages, schema, **kwargs):
        # Ollama 沒有原生結構化輸出，用 prompt + JSON parse
        result = await self.chat(messages, **kwargs)
        # 嘗試從結果中抽出 JSON
        return self._parse_json_from_text(result, schema)
    
    def get_prompts(self) -> dict:
        # Ollama 需要更明確的指令、更短、更結構化
        return OLLAMA_PROMPTS
```

### 5.3 Factory

```python
# learn2deck/llm/factory.py
def create_llm_client(config: LLMConfig) -> BaseLLMClient:
    provider = config.provider
    
    if provider == "claude":
        if not config.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY required for claude provider")
        return ClaudeClient(
            api_key=config.anthropic_api_key,
            model=config.claude_model
        )
    
    elif provider == "openai":
        if not config.openai_api_key:
            raise ValueError("OPENAI_API_KEY required for openai provider")
        return OpenAIClient(
            api_key=config.openai_api_key,
            model=config.openai_model
        )
    
    elif provider == "ollama":
        return OllamaClient(
            host=config.ollama_host,
            model=config.ollama_model
        )
    
    elif provider == "azure":
        return AzureOpenAIClient(
            api_key=config.azure_openai_api_key,
            endpoint=config.azure_openai_endpoint,
            deployment=config.azure_deployment
        )
    
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")
```

---

## 6. Prompt 適配器（解決「LLM 解析差異」）

### 6.1 問題

同一個任務的 prompt 在不同 LLM 上效果差異大：

```python
# 對 Claude 有效的 prompt
CLAUDE_PROMPT = """你是簡報內容精簡助手。

任務：將以下內容精簡到 {target_lines} 行以內，同時：
1. 保留所有關鍵技術資訊
2. 移除冗餘的修飾語
3. 如果是程式碼：保留語意但縮短註解

原始內容：
{text}

請只回傳精簡後的內容，不要加任何說明。"""

# 對 Llama 3 (Ollama) 效果差，因為：
# - 不理解「任務」、「請只回傳」等禮貌用語
# - 容易加解釋、廢話
# - 對 JSON 格式指令遵循度低
```

### 6.2 解法：每家 LLM 有自己的 Prompt 庫

```python
# learn2deck/llm/prompts/claude.py
CLAUDE_PROMPTS = {
    "simplify_text": """你是簡報內容精簡助手。

任務：將以下內容精簡到 {target_lines} 行以內，同時：
1. 保留所有關鍵技術資訊（API 名稱、版本、參數）
2. 移除冗餘的修飾語和重複資訊
3. 如果是程式碼：保留語意但縮短註解和換行

原始內容：
```
{text}
```

請只回傳精簡後的內容，不要加任何說明。""",

    "classify_layout": """你是簡報版型顧問。

內容：
{content}

選項：{options}

請只回傳一個選項名稱，不要加說明。""",
}

# learn2deck/llm/prompts/openai.py
OPENAI_PROMPTS = {
    "simplify_text": """You are a presentation content simplifier.

Task: Reduce the following content to {target_lines} lines or less while:
1. Preserving all key technical information
2. Removing redundant modifiers
3. For code: keep semantics but shorten comments

Original:
{text}

Return only the simplified content.""",

    "classify_layout": """Classify this content into one of these slide types: {options}

Content:
{content}

Return only the type name.""",
}

# learn2deck/llm/prompts/ollama.py
OLLAMA_PROMPTS = {
    "simplify_text": """TASK: Simplify text to {target_lines} lines.
KEEP: API names, versions, parameters.
REMOVE: redundant words, explanations.
OUTPUT: ONLY the simplified text. NO intro, NO explanation.

TEXT:
{text}

SIMPLIFIED:""",

    "classify_layout": """CLASSIFY into one type: {options}
CONTENT: {content}
TYPE:""",
}
```

**關鍵差異**：
- Claude：自然語言、禮貌、複雜指令
- OpenAI：英文、直接、明確
- Ollama：極簡、命令式、明確分隔 input/output

### 6.3 Prompt 測試套件

```python
# tests/test_prompts.py
import pytest

# 每個 prompt × 每個 LLM = 測試案例
PROMPT_TEST_CASES = [
    # (task, input, expected_output_pattern)
    ("simplify_text", "很長的程式碼...", r"\{[\s\S]*\}"),
    ("classify_layout", "## 學習目標\n- ..", r"objectives"),
]

@pytest.mark.parametrize("task,input_text,expected_pattern", PROMPT_TEST_CASES)
@pytest.mark.parametrize("llm_class", [ClaudeClient, OpenAIClient, OllamaClient])
async def test_prompt_quality(llm_class, task, input_text, expected_pattern):
    """每個 prompt 對每個 LLM 都要有測試"""
    client = llm_class(test_api_key, test_model)
    prompts = client.get_prompts()
    messages = [{"role": "user", "content": prompts[task].format(...)}]
    result = await client.chat(messages)
    
    # 品質檢查
    assert re.search(expected_pattern, result), f"LLM {llm_class.__name__} failed for {task}"
    
    # 速度檢查
    # 成本檢查
```

---

## 7. 推薦最終方案

### 7.1 階段 1（v1.0）：純規則
- 完全不涉及 LLM
- 把工具做扎實

### 7.2 階段 2（v1.1）：**鎖定 Claude**
- 介面抽象（BaseLLMAgent）但只實作 Claude
- prompt 庫只寫 Claude 優化版
- 6 個 Agent 功能中只實作 A2 + A3（最實用）
- 累積 prompt 工程經驗

### 7.3 階段 3（v2.0）：**抽象化多家 LLM**
- 抽出 BaseLLMClient 介面
- 實作 OpenAI、Ollama、Azure OpenAI
- 每家 LLM 有自己的 prompt 變體
- 跨 LLM 測試套件
- Fallback 鏈
- 模型分層（fast/smart/smartest）

### 7.4 為什麼不直接做 v2.0 設計？

| 考量 | 鎖定 Claude（推薦） | 直接做 3.2 |
|------|-------------------|----------|
| 開發時間 | v1.1 2 週可上線 | 至少 10-14 週 |
| 品質穩定性 | 高（只測 1 家） | 中（跨家測試） |
| 使用者選擇 | 鎖定 Claude | 多家可選 |
| 彈性 | 低 | 高 |
| 除錯難度 | 低 | 高 |
| **適用情境** | **驗證概念、單一 LLM 足夠** | **離線/隱私/多雲需求** |

**v1.1 鎖定 Claude 的 v2.0 抽象化是最佳的「先求有再求好」策略**。

---

## 8. 開放問題（請 review）

1. **同意分階段**嗎？v1.1 鎖定 Claude，v2.0 再支援多家？
2. **如果 v1.1 用戶強烈要求 OpenAI 支援**，要 (a) 等 v2.0 / (b) 提早做 / (c) 開放 plugin 介面讓社群貢獻？
3. **Prompt 抽象成本**：要不要 v1.1 就先做 prompt 介面（雖然只有 Claude prompt）？
4. **Fallback 機制**：v1.1 就要做 fallback chain 嗎？還是等真的出問題再加？
5. **Azure OpenAI**：企業用戶常見，要不要列為 v2.0 優先？
6. **Ollama 優先度**：v2.0 內 3 個新 LLM（OpenAI/Ollama/Azure）哪個優先？

---

## 9. 結論

**最終推薦**：

✅ **v1.1 採用 3.1（鎖定 Claude）**，但介面設計為可替換
✅ **v2.0 升級為 3.2（多家 LLM）**，提供 fallback 鏈與模型分層
✅ **環境變數用 `.env`**，從 v1.1 就開始設計（即使只有 Claude 設定）
✅ **Prompt 從一開始就抽象化**，v1.1 只寫 Claude 版本，v2.0 加其他家

這樣可以：
- v1.1 快速上線、驗證概念
- v2.0 平滑升級、不大改
- 使用者有清晰的遷移路徑

**請確認此方案**。如果同意，我會把這個 LLM 策略整合到 `learn2deck-spec.md` 主文件，並開始 v1.0 純規則版實作。
