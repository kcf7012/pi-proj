"""
SummaryBuilder - 重點回顧頁

對應 SlideType.SUMMARY
body schema: {
    "key_points": ["...", "..."],
    "next_steps": ["...", "..."]  (optional)
}
"""
from __future__ import annotations

from pptx.slide import Slide

from ..core import SlideContent, SlideType
from ..pptx_helpers import add_summary_slide
from .base import BaseBuilder


class SummaryBuilder(BaseBuilder):
    """重點回顧頁 builder"""

    slide_type = SlideType.SUMMARY

    def build(
        self,
        slide: Slide,
        content: SlideContent,
        slide_num: int | None = None,
        total: int | None = None,
    ) -> None:
        body = self.require_body(content)

        key_points = self.get_list(body, "key_points")
        next_steps = self.get_list(body, "next_steps")

        # 至少要有一個
        if not key_points and not next_steps:
            from ..core import MissingFieldError
            raise MissingFieldError(
                f"Summary '{content.title}' 需要 key_points 或 next_steps"
            )

        add_summary_slide(
            slide,
            title=content.title,
            key_points=key_points or None,
            next_steps=next_steps or None,
            source=content.source_ref,
            theme=self.theme,
        )
