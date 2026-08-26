"""
Deck 與 Slide 的資料結構

對應 spec §4.1：
- SlideType: 9 種投影片版型
- SlideContent: 單張投影片內容
- DeckSpec: 整份簡報規格
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class SlideType(str, Enum):
    """投影片版型（字串值，方便 YAML 序列化）

    9 種版型對應 9 種 builder（見 builders/）
    """

    # 特殊頁
    COVER = "cover"                      # 封面
    OBJECTIVES = "objectives"            # 學習目標
    SECTION_DIVIDER = "section"          # 章節分隔
    SUMMARY = "summary"                  # 重點回顧
    CALLOUT = "callout"                  # 純提示框

    # 內容頁
    TITLE_CONTENT = "title_content"      # 標題+文字/bullet
    TITLE_TABLE = "title_table"          # 標題+表格
    TITLE_CODE = "title_code"            # 標題+程式碼
    TWO_COLUMN = "two_column"            # 雙欄對比
    GRID_CARDS = "grid_cards"            # 網格卡片

    @classmethod
    def values(cls) -> list[str]:
        """所有版型名稱（用於驗證或顯示）"""
        return [s.value for s in cls]


# === Slide 內容的 Body 型別定義 ===
# 不同版型需要不同的 body 結構，用 TypedDict 標註（執行期不強制）

# title_content
# body = {
#     "items": ["bullet1", "bullet2", ...]
#     # 或
#     "text": "純文字段落"
# }

# title_table
# body = {
#     "headers": ["col1", "col2", ...],
#     "rows": [
#         ["row1col1", "row1col2", ...],
#         ...
#     ]
# }

# title_code
# body = {
#     "code": "...",
#     "language": "bash"  # optional
# }

# two_column
# body = {
#     "left": {"title": "...", "items": [...]},
#     "right": {"title": "...", "items": [...]}
# }

# grid_cards
# body = {
#     "items": [
#         {"icon": "🎯", "title": "...", "desc": "..."},
#         ...
#     ],
#     "cols": 3  # optional, default 3
# }

# objectives（grid_cards 的特例）
# body = grid_cards 格式

# cover
# body = {
#     "tag": "#02 · Plugin 開發"  # optional
# }

# section_divider
# body = {
#     "section_num": "Part 1",       # 大編號
#     "section_title": "...",         # 標題
#     "section_subtitle": "..."       # 副標題（optional）
# }

# callout
# body = {
#     "text": "...",
#     "icon": "💡",                    # optional
#     "style": "info" | "warning" | "success"  # optional
# }

# summary
# body = {
#     "key_points": ["...", "..."],
#     "next_steps": ["...", "..."]  # optional
# }


@dataclass
class SlideContent:
    """單張投影片的內容規格

    Attributes:
        type: 版型
        title: 標題文字
        subtitle: 副標題（optional）
        body: 內文（依 type 不同結構不同，見上方註解）
        slide_num: 投影片編號（產出時自動填入）
        source_ref: 對應的 Markdown 段落錨點（optional，用於追蹤來源）
        extra: 額外 metadata（builder 專用，optional）
    """

    type: SlideType
    title: str
    subtitle: str | None = None
    body: dict[str, Any] | None = None
    slide_num: int | None = None
    source_ref: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """轉成 dict（方便 YAML/JSON 序列化）"""
        return {
            "type": self.type.value,
            "title": self.title,
            "subtitle": self.subtitle,
            "body": self.body,
            "slide_num": self.slide_num,
            "source_ref": self.source_ref,
            "extra": self.extra,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SlideContent":
        """從 dict 還原（方便 YAML/JSON 解析）"""
        return cls(
            type=SlideType(data["type"]),
            title=data["title"],
            subtitle=data.get("subtitle"),
            body=data.get("body"),
            slide_num=data.get("slide_num"),
            source_ref=data.get("source_ref"),
            extra=data.get("extra", {}),
        )


@dataclass
class DeckSpec:
    """整份簡報的規格

    Attributes:
        title: 簡報主標題
        subtitle: 簡報副標題
        theme: 主題名稱（預設 "claude-orange"）
        source_path: 原始 Markdown 路徑（optional，僅供追蹤）
        slides: 投影片清單
        metadata: 額外 metadata（作者、日期、版本等）
    """

    title: str
    subtitle: str = ""
    theme: str = "claude-orange"
    source_path: str | None = None
    slides: list[SlideContent] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    # === 統計 ===
    @property
    def total_slides(self) -> int:
        return len(self.slides)

    @property
    def slide_types_count(self) -> dict[str, int]:
        """統計各版型數量"""
        count: dict[str, int] = {}
        for s in self.slides:
            key = s.type.value
            count[key] = count.get(key, 0) + 1
        return count

    # === 操作 ===
    def add_slide(self, slide: SlideContent) -> None:
        """新增投影片（會自動編號）"""
        slide.slide_num = len(self.slides) + 1
        self.slides.append(slide)

    def get_slide(self, slide_num: int) -> SlideContent | None:
        """取得指定編號的投影片（1-indexed）"""
        if 1 <= slide_num <= len(self.slides):
            return self.slides[slide_num - 1]
        return None

    # === 序列化 ===
    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "subtitle": self.subtitle,
            "theme": self.theme,
            "source_path": self.source_path,
            "slides": [s.to_dict() for s in self.slides],
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DeckSpec":
        return cls(
            title=data["title"],
            subtitle=data.get("subtitle", ""),
            theme=data.get("theme", "claude-orange"),
            source_path=data.get("source_path"),
            slides=[SlideContent.from_dict(s) for s in data.get("slides", [])],
            metadata=data.get("metadata", {}),
        )

    # === 驗證 ===
    def validate(self) -> list[str]:
        """回傳所有驗證錯誤訊息（空 list 代表 OK）

        這是基本驗證，詳細版面驗證見 validators/
        """
        errors = []
        if not self.title:
            errors.append("DeckSpec.title 不可為空")
        if not self.slides:
            errors.append("DeckSpec.slides 不可為空（至少要有 1 張投影片）")
        for i, slide in enumerate(self.slides, 1):
            if not slide.title:
                errors.append(f"Slide {i}: title 不可為空")
            if slide.type in (SlideType.COVER, SlideType.SECTION_DIVIDER):
                # 這些版型 title 是必要的
                pass
        return errors
