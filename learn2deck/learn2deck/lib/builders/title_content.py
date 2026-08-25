"""
TitleContentBuilder - 標題+內容頁

對應 SlideType.TITLE_CONTENT
也用於 SlideType.CALLOUT（單一提示框）

body schema: {
    "text": "...",               # 純文字段落
    # 或
    "items": ["...", "..."],     # bullet list
    # 或
    "text": "...", "icon": "💡"  # callout 風格
}
"""
from __future__ import annotations

from pptx.util import Inches

from pptx.slide import Slide

from ..core import MissingFieldError, SlideContent, SlideType
from ..pptx_helpers import (
    add_bullet_list, add_callout, add_text_block,
)
from .base import BaseBuilder


class TitleContentBuilder(BaseBuilder):
    """標題+內容（純文字 / bullet / callout）"""

    slide_type = SlideType.TITLE_CONTENT

    def build(
        self,
        slide: Slide,
        content: SlideContent,
        slide_num: int | None = None,
        total: int | None = None,
    ) -> None:
        # 1. 標題列
        self.add_title(slide, content, slide_num=slide_num, total=total)

        # 2. 內容
        body = content.body or {}

        # callout 風格
        if content.type == SlideType.CALLOUT:
            self._draw_callout(slide, body)
            return

        # bullet list
        if "items" in body:
            self._draw_bullets(slide, body)
            return

        # 純文字
        if "text" in body:
            self._draw_text(slide, body)
            return

        # 兩者都沒有：畫一個空的 placeholder
        raise MissingFieldError(
            f"TitleContent '{content.title}' 的 body 缺少 text 或 items"
        )

    def _draw_text(self, slide: Slide, body: dict) -> None:
        text = self.get_str(body, "text")
        bold = body.get("bold", False)
        italic = body.get("italic", False)
        font_size = body.get("font_size", 16)
        color_name = body.get("color", "dark")

        # 用 theme 取得顏色
        if self.theme is not None:
            from ..pptx_helpers.shapes import _color
            color = _color(self.theme, color_name, "#2C2C2C")
        else:
            from pptx.dml.color import RGBColor
            color = RGBColor(0x2C, 0x2C, 0x2C)

        add_text_block(
            slide, text,
            Inches(0.5), Inches(1.7), Inches(12.333), Inches(4.8),
            font_size=font_size, bold=bold, italic=italic, color=color,
            theme=self.theme,
        )

    def _draw_bullets(self, slide: Slide, body: dict) -> None:
        items = self.get_list(body, "items")
        font_size = body.get("font_size", 16)

        add_bullet_list(
            slide, items,
            Inches(0.7), Inches(1.8), Inches(12), Inches(4.8),
            font_size=font_size, theme=self.theme,
        )

    def _draw_callout(self, slide: Slide, body: dict) -> None:
        text = self.get_str(body, "text")
        icon = self.get_str(body, "icon", "💡")
        style = body.get("style", "info")  # info / warning / success

        # 根據 style 選擇邊框顏色
        if self.theme is not None:
            from ..pptx_helpers.shapes import _color
            bg_color = _color(self.theme, "bg_gray", "#F3F0E9")
            if style == "warning":
                border_color = _color(self.theme, "red", "#DC2626")
            elif style == "success":
                border_color = _color(self.theme, "green", "#16A34A")
            else:
                border_color = _color(self.theme, "primary", "#C75A1A")
        else:
            from pptx.dml.color import RGBColor
            bg_color = RGBColor(0xF3, 0xF0, 0xE9)
            border_color = RGBColor(0xC7, 0x5A, 0x1A)

        # callout 沒有標題列（用滿版 callout）
        add_callout(
            slide, text,
            Inches(0.5), Inches(2.5), Inches(12.333), Inches(2.5),
            bg_color=bg_color, border_color=border_color,
            icon=icon, font_size=18,
            theme=self.theme,
        )
