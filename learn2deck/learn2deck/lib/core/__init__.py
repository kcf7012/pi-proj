"""learn2deck.core - 核心資料結構"""
from .exceptions import (
    Learn2deckError,
    ParseError,
    FrontmatterError,
    InvalidSlideTypeError,
    ThemeError,
    ThemeNotFoundError,
    ThemeValidationError,
    BuildError,
    MissingFieldError,
    ValidationError,
    ValidationRuleError,
    OutputError,
    AgentError,
    CostLimitExceeded,
    LLMUnavailable,
)
from .theme import Theme, load_theme, load_theme_from_path, list_builtin_themes
from .deck import SlideType, SlideContent, DeckSpec

__all__ = [
    # 例外
    "Learn2deckError",
    "ParseError",
    "FrontmatterError",
    "InvalidSlideTypeError",
    "ThemeError",
    "ThemeNotFoundError",
    "ThemeValidationError",
    "BuildError",
    "MissingFieldError",
    "ValidationError",
    "ValidationRuleError",
    "OutputError",
    "AgentError",
    "CostLimitExceeded",
    "LLMUnavailable",
    # 資料結構
    "Theme",
    "load_theme",
    "load_theme_from_path",
    "list_builtin_themes",
    "SlideType",
    "SlideContent",
    "DeckSpec",
]
