"""
TitleTableBuilder - 標題+表格頁

對應 SlideType.TITLE_TABLE
body schema: {
    "headers": ["Col1", "Col2", ...],
    "rows": [
        ["row1col1", "row1col2", ...],
        ...
    ],
    "font_size": 11  (optional)
}
"""
from __future__ import annotations

from pptx.util import Inches

from pptx.slide import Slide

from ..core import MissingFieldError, SlideContent, SlideType
from ..pptx_helpers import add_comparison_table
from .base import BaseBuilder


class TitleTableBuilder(BaseBuilder):
    """標題+表格 builder"""

    slide_type = SlideType.TITLE_TABLE

    def build(
        self,
        slide: Slide,
        content: SlideContent,
        slide_num: int | None = None,
        total: int | None = None,
    ) -> None:
        # 1. 標題列
        self.add_title(slide, content, slide_num=slide_num, total=total)

        # 2. 表格
        body = self.require_body(content, "headers")
        headers = body["headers"]
        rows = body.get("rows", [])
        font_size = body.get("font_size", 11)

        if not isinstance(headers, list):
            raise MissingFieldError(f"Slide '{content.title}' 的 headers 應為 list")
        if not isinstance(rows, list):
            raise MissingFieldError(f"Slide '{content.title}' 的 rows 應為 list")

        add_comparison_table(
            slide,
            headers=headers,
            rows=rows,
            left=Inches(0.5),
            top=Inches(1.7),
            width=Inches(12.333),
            height=Inches(4.8),
            font_size=font_size,
            theme=self.theme,
        )
