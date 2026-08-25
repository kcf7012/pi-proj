"""
SectionDividerBuilder - 章節分隔頁

對應 SlideType.SECTION_DIVIDER
body schema: {
    "section_num": "Part 1",
    "section_subtitle": "...",  (optional)
}
"""
from __future__ import annotations

from pptx.slide import Slide

from ..core import BuildError, SlideContent, SlideType
from .base import BaseBuilder


class SectionDividerBuilder(BaseBuilder):
    """章節分隔頁 builder"""

    slide_type = SlideType.SECTION_DIVIDER

    def build(
        self,
        slide: Slide,
        content: SlideContent,
        slide_num: int | None = None,
        total: int | None = None,
    ) -> None:
        """章節分隔必須透過 build_full_deck() 建立"""
        raise BuildError(
            "Section divider 必須透過 build_full_deck() 處理。"
            "因為 add_section_divider() 需要 Presentation 物件。"
        )
