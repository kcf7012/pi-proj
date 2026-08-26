"""
TitleCodeBuilder - 標題+程式碼頁

對應 SlideType.TITLE_CODE
body schema: {
    "code": "...",
    "language": "python"  (optional, default "bash")
    "font_size": 11  (optional, default 11)
}
"""
from __future__ import annotations

from pptx.util import Inches

from pptx.slide import Slide

from ..core import MissingFieldError, SlideContent, SlideType
from ..pptx_helpers import add_code_block
from .base import BaseBuilder


class TitleCodeBuilder(BaseBuilder):
    """標題+程式碼 builder"""

    slide_type = SlideType.TITLE_CODE

    def build(
        self,
        slide: Slide,
        content: SlideContent,
        slide_num: int | None = None,
        total: int | None = None,
    ) -> None:
        # 1. 標題列
        self.add_title(slide, content, slide_num=slide_num, total=total)

        # 2. 程式碼
        body = self.require_body(content, "code")
        code = body["code"]
        language = body.get("language", "bash")
        font_size = body.get("font_size", 11)

        # 動態計算高度與字級
        from ..pptx_helpers.layout import LINE_HEIGHTS
        n_lines = code.count("\n") + 1
        max_height = 5.5

        # 依行數自動調整字級
        for try_size in [font_size, 10, 9, 8]:
            line_h = LINE_HEIGHTS.get(try_size, try_size / 72 * 1.2)
            needed = n_lines * line_h + 0.3
            if needed <= max_height:
                font_size = try_size
                height = needed
                break
        else:
            font_size = 8
            line_h = LINE_HEIGHTS[font_size]
            height = max_height

        add_code_block(
            slide, code,
            left=Inches(0.7),
            top=Inches(1.7),
            width=Inches(11.933),
            height=Inches(height),
            language=language,
            font_size=font_size,
            theme=self.theme,
        )
