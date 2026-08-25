"""
ObjectivesBuilder - 學習目標頁

對應 SlideType.OBJECTIVES
body schema: {
    "items": [
        {"icon": "🎯", "title": "...", "desc": "..."},
        ...
    ],
    "cols": 3  (optional, default 3)
}

本質上就是 GridCardsBuilder，但標題固定為「本章你會學到」
"""
from __future__ import annotations

from ..core import SlideContent, SlideType
from .grid_cards import GridCardsBuilder


class ObjectivesBuilder(GridCardsBuilder):
    """學習目標 builder（繼承 GridCardsBuilder）"""

    slide_type = SlideType.OBJECTIVES

    def build(
        self,
        slide,
        content: SlideContent,
        slide_num: int | None = None,
        total: int | None = None,
    ) -> None:
        # 直接呼叫父類的 build()，但允許覆寫標題
        if not content.title or content.title.strip() == "":
            content.title = "本章你會學到"

        super().build(slide, content, slide_num=slide_num, total=total)
