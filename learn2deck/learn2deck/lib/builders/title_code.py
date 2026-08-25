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

        add_code_block(
            slide, code,
            left=Inches(0.7),
            top=Inches(1.7),
            width=Inches(11.933),
            height=Inches(4.8),
            language=language,
            font_size=font_size,
            theme=self.theme,
        )
