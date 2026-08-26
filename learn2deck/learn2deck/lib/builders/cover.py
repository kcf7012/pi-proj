"""
CoverBuilder - 封面頁

對應 SlideType.COVER
body schema: {"tag": "..."}  (optional)

注意：封面通常由 build_full_deck() 用 add_cover_slide() 直接建立
這個 builder 主要是介面完整性（實務上很少用 build()）
"""
from __future__ import annotations

from pptx.slide import Slide

from ..core import BuildError, SlideContent, SlideType
from .base import BaseBuilder


class CoverBuilder(BaseBuilder):
    """封面頁 builder"""

    slide_type = SlideType.COVER

    def build(
        self,
        slide: Slide,
        content: SlideContent,
        slide_num: int | None = None,
        total: int | None = None,
    ) -> None:
        """封面必須透過 build_full_deck() 建立（需要 Presentation 而非 Slide）"""
        raise BuildError(
            "Cover 必須透過 build_full_deck() 處理。"
            "因為 add_cover_slide() 需要 Presentation 物件而非 Slide。"
        )
