"""
learn2deck.validators.base - 所有 validator 的基底

定義統一介面與報告結構。
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING

from ..core import ValidationError, ValidationRuleError

if TYPE_CHECKING:
    from pptx import Presentation


class Severity(str, Enum):
    """問題嚴重度"""

    ERROR = "error"           # 必須修正
    WARNING = "warning"       # 建議修正
    SUGGESTION = "suggestion"  # 可改進


@dataclass
class Issue:
    """單一驗證問題"""

    rule: str           # 例 "R1", "R2"
    severity: Severity
    slide_num: int | None = None  # 第幾張投影片（1-indexed），None = 全域
    message: str = ""   # 人類可讀訊息
    details: dict = field(default_factory=dict)  # 額外資訊（可選）

    def __str__(self) -> str:
        loc = f"slide {self.slide_num}" if self.slide_num else "global"
        return f"[{self.rule}/{self.severity.value}] {loc}: {self.message}"


@dataclass
class ValidationReport:
    """驗證報告

    Attributes:
        pptx_path: 被驗證的 PPTX 檔案路徑
        passed: 是否有任何 ERROR
        issues: 所有問題（包含 errors/warnings/suggestions）
        stats: 統計資訊（投影片數、code 框數等）
    """

    pptx_path: str
    passed: bool
    issues: list[Issue] = field(default_factory=list)
    stats: dict = field(default_factory=dict)

    @property
    def errors(self) -> list[Issue]:
        return [i for i in self.issues if i.severity == Severity.ERROR]

    @property
    def warnings(self) -> list[Issue]:
        return [i for i in self.issues if i.severity == Severity.WARNING]

    @property
    def suggestions(self) -> list[Issue]:
        return [i for i in self.issues if i.severity == Severity.SUGGESTION]

    def to_dict(self) -> dict:
        """序列化為 dict（方便 JSON 輸出）"""
        return {
            "pptx_path": self.pptx_path,
            "passed": self.passed,
            "issues": [
                {
                    "rule": i.rule,
                    "severity": i.severity.value,
                    "slide_num": i.slide_num,
                    "message": i.message,
                    "details": i.details,
                }
                for i in self.issues
            ],
            "stats": self.stats,
        }

    def print_human(self) -> str:
        """人類可讀格式"""
        lines = [f"📋 Validation Report: {self.pptx_path}"]
        lines.append(f"   Status: {'✅ PASSED' if self.passed else '❌ FAILED'}")
        lines.append(f"   Total slides: {self.stats.get('total_slides', '?')}")

        if self.issues:
            lines.append(f"   Issues: {len(self.issues)}")
            for issue in self.issues:
                lines.append(f"     {issue}")

        return "\n".join(lines)


class BaseValidator(ABC):
    """所有 validator 的基底類別

    子類別需要：
    - 設定 rule_id（如 "R1"）
    - 實作 validate(prs) 方法
    """

    rule_id: str = ""  # 子類別覆寫

    @abstractmethod
    def validate(self, prs: "Presentation") -> list[Issue]:
        """檢查 PPTX，回傳所有問題

        Args:
            prs: python-pptx Presentation 物件

        Returns:
            Issue 列表（可能為空）
        """
        raise NotImplementedError

    # === 便利方法 ===

    def make_issue(
        self,
        severity: Severity,
        message: str,
        slide_num: int | None = None,
        **details,
    ) -> Issue:
        """建立 Issue 的便利方法"""
        return Issue(
            rule=self.rule_id,
            severity=severity,
            slide_num=slide_num,
            message=message,
            details=details,
        )

    def make_error(self, message: str, slide_num: int | None = None, **details) -> Issue:
        return self.make_issue(Severity.ERROR, message, slide_num, **details)

    def make_warning(self, message: str, slide_num: int | None = None, **details) -> Issue:
        return self.make_issue(Severity.WARNING, message, slide_num, **details)

    def make_suggestion(self, message: str, slide_num: int | None = None, **details) -> Issue:
        return self.make_issue(Severity.SUGGESTION, message, slide_num, **details)
