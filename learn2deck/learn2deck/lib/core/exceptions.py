"""
learn2deck 自訂例外

所有例外繼承自 Learn2deckError，方便上層統一捕捉。
"""


class Learn2deckError(Exception):
    """所有 learn2deck 例外的基底類別"""
    pass


# === 解析階段 ===
class ParseError(Learn2deckError):
    """解析 Markdown / YAML 輸入時失敗"""
    pass


class FrontmatterError(ParseError):
    """YAML frontmatter 格式錯誤"""
    pass


class InvalidSlideTypeError(ParseError):
    """未知的 slide_type"""
    pass


# === 主題階段 ===
class ThemeError(Learn2deckError):
    """主題相關錯誤"""
    pass


class ThemeNotFoundError(ThemeError):
    """找不到指定主題"""
    pass


class ThemeValidationError(ThemeError):
    """主題 YAML 格式驗證失敗"""
    pass


# === 建構階段 ===
class BuildError(Learn2deckError):
    """建構投影片時失敗"""
    pass


class MissingFieldError(BuildError):
    """SlideContent 缺少必要欄位"""
    pass


# === 驗證階段 ===
class ValidationError(Learn2deckError):
    """驗證階段發現錯誤"""
    pass


class ValidationRuleError(ValidationError):
    """單一驗證規則失敗"""
    pass


# === 輸出階段 ===
class OutputError(Learn2deckError):
    """寫入 PPTX 檔案失敗"""
    pass


# === Agent 階段（v1.1+） ===
class AgentError(Learn2deckError):
    """Agent 相關錯誤"""
    pass


class CostLimitExceeded(AgentError):
    """超過 LLM 成本上限"""
    pass


class LLMUnavailable(AgentError):
    """LLM 無法使用（API 錯誤、額度用盡等）"""
    pass
