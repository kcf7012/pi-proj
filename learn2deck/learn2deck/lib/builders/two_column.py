"""
TwoColumnBuilder - 雙欄對比頁

對應 SlideType.TWO_COLUMN
body schema: {
    "left": {"title": "...", "items": ["...", "..."]},
    "right": {"title": "...", "items": ["...", "..."]},
    "left_color": "blue"  (optional, theme color name)
    "right_color": "primary"  (optional, theme color name)
}
"""
from __future__ import annotations

from pptx.util import Inches

from pptx.slide import Slide
from pptx.dml.color import RGBColor

from ..core import MissingFieldError, SlideContent, SlideType
from ..pptx_helpers import add_two_column_compare
from .base import BaseBuilder


class TwoColumnBuilder(BaseBuilder):
    """雙欄對比 builder"""

    slide_type = SlideType.TWO_COLUMN

    def build(
        self,
        slide: Slide,
        content: SlideContent,
        slide_num: int | None = None,
        total: int | None = None,
    ) -> None:
        # 1. 標題列
        self.add_title(slide, content, slide_num=slide_num, total=total)

        # 2. 雙欄
        body = self.require_body(content)

        if "left" not in body or "right" not in body:
            raise MissingFieldError(
                f"TwoColumn '{content.title}' 缺少 left 或 right"
            )

        left = body["left"]
        right = body["right"]
        left_title = left.get("title", "")
        left_items = left.get("items", [])
        right_title = right.get("title", "")
        right_items = right.get("items", [])

        if not left_title or not right_title:
            raise MissingFieldError(
                f"TwoColumn '{content.title}' 的 left/right 缺少 title"
            )

        # 顏色從 theme 取得
        left_color = self._get_color(body.get("left_color", "blue"), "#3B82F6")
        right_color = self._get_color(body.get("right_color", "primary"), "#C75A1A")

        add_two_column_compare(
            slide,
            left_title=left_title,
            left_content=left_items,
            right_title=right_title,
            right_content=right_items,
            top=Inches(1.7),
            height=Inches(5.0),
            left_color=left_color,
            right_color=right_color,
            theme=self.theme,
        )

    def _get_color(self, color_name: str, fallback_hex: str) -> RGBColor:
        """從 theme 取得顏色"""
        if self.theme is not None:
            from ..pptx_helpers.shapes import _color
            return _color(self.theme, color_name, fallback_hex)
        # fallback
        hex_str = fallback_hex.lstrip("#")
        return RGBColor(
            int(hex_str[0:2], 16),
            int(hex_str[2:4], 16),
            int(hex_str[4:6], 16),
        )
