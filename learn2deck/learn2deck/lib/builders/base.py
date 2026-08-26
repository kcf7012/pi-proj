"""
learn2deck builders.base - 所有 builder 的基底

定義統一介面與共用工具。
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from pptx.slide import Slide

from ..core import (
    BuildError, MissingFieldError, SlideContent, Theme,
    SlideType,
)

if TYPE_CHECKING:
    from ..core import DeckSpec


class BaseBuilder(ABC):
    """所有 builder 的基底類別

    每個 builder 對應一種 SlideType，負責把 SlideContent 轉成實際的投影片內容。
    """

    # 這個 builder 對應的 SlideType（子類別覆寫）
    slide_type: SlideType = None  # type: ignore

    def __init__(self, theme: Theme | None = None):
        self.theme = theme

    @abstractmethod
    def build(
        self,
        slide: Slide,
        content: SlideContent,
        slide_num: int | None = None,
        total: int | None = None,
    ) -> None:
        """在 slide 上繪製對應版型

        Args:
            slide: python-pptx 的 Slide 物件
            content: SlideContent 規格（包含 title、body 等）
            slide_num: 投影片編號（1-indexed）
            total: 總投影片數
        """
        raise NotImplementedError

    # === 共用工具 ===

    def add_title(
        self,
        slide: Slide,
        content: SlideContent,
        slide_num: int | None = None,
        total: int | None = None,
    ) -> None:
        """加入標題列（如果有 source 自動填入）"""
        from ..pptx_helpers import add_title_bar

        if not content.title:
            raise MissingFieldError(
                f"Slide #{slide_num or '?'} 缺少 title 欄位"
            )

        add_title_bar(
            slide,
            title_text=content.title,
            subtitle_text=content.subtitle,
            slide_num=slide_num,
            total=total,
            source=content.source_ref,
            theme=self.theme,
        )

    def require_body(self, content: SlideContent, key: str | None = None) -> dict:
        """取得 body 並驗證存在

        Args:
            content: SlideContent
            key: 若指定，body 必須包含此 key

        Returns:
            body 字典
        """
        if content.body is None:
            raise MissingFieldError(
                f"Slide '{content.title}' 缺少 body 欄位"
            )
        if key and key not in content.body:
            raise MissingFieldError(
                f"Slide '{content.title}' 的 body 缺少 '{key}' 欄位"
            )
        return content.body

    def get_str(self, body: dict, key: str, default: str = "") -> str:
        """安全取得字串欄位"""
        value = body.get(key, default)
        return str(value) if value is not None else default

    def get_list(self, body: dict, key: str) -> list:
        """安全取得 list 欄位"""
        value = body.get(key, [])
        return value if isinstance(value, list) else []


def build_slide(
    slide: Slide,
    content: SlideContent,
    theme: Theme | None = None,
    slide_num: int | None = None,
    total: int | None = None,
) -> None:
    """便利函式：根據 content.type 自動選擇對應的 builder

    這是給 build_deck() 用的入口函式。
    """
    from .cover import CoverBuilder
    from .objectives import ObjectivesBuilder
    from .section_divider import SectionDividerBuilder
    from .summary import SummaryBuilder
    from .title_content import TitleContentBuilder
    from .title_table import TitleTableBuilder
    from .title_code import TitleCodeBuilder
    from .two_column import TwoColumnBuilder
    from .grid_cards import GridCardsBuilder

    # type → builder 對應表
    builder_map = {
        SlideType.COVER: CoverBuilder,
        SlideType.OBJECTIVES: ObjectivesBuilder,
        SlideType.SECTION_DIVIDER: SectionDividerBuilder,
        SlideType.SUMMARY: SummaryBuilder,
        SlideType.CALLOUT: TitleContentBuilder,  # callout 用 title_content
        SlideType.TITLE_CONTENT: TitleContentBuilder,
        SlideType.TITLE_TABLE: TitleTableBuilder,
        SlideType.TITLE_CODE: TitleCodeBuilder,
        SlideType.TWO_COLUMN: TwoColumnBuilder,
        SlideType.GRID_CARDS: GridCardsBuilder,
    }

    builder_cls = builder_map.get(content.type)
    if builder_cls is None:
        raise BuildError(f"找不到對應的 builder: {content.type}")

    builder = builder_cls(theme=theme)
    builder.build(slide, content, slide_num=slide_num, total=total)


def build_full_deck(
    deck_spec: "DeckSpec",
    output_path: str,
) -> None:
    """從 DeckSpec 產生完整 PPTX

    Args:
        deck_spec: 完整簡報規格
        output_path: 輸出 .pptx 檔案路徑
    """
    from pathlib import Path

    from ..core import load_theme
    from ..pptx_helpers import add_cover_slide, new_presentation

    # 載入主題
    theme = load_theme(deck_spec.theme) if deck_spec.theme else None

    # 建立簡報
    prs = new_presentation(theme)
    total = deck_spec.total_slides

    for i, slide_content in enumerate(deck_spec.slides, start=1):
        if slide_content.type == SlideType.COVER:
            # 封面（特殊處理，create_presentation 自動加）
            body = slide_content.body or {}
            add_cover_slide(
                prs,
                title=slide_content.title,
                subtitle=slide_content.subtitle or "",
                tag=body.get("tag", ""),
                theme=theme,
            )
        elif slide_content.type == SlideType.SECTION_DIVIDER:
            # 章節分隔（同上）
            body = slide_content.body or {}
            from ..pptx_helpers import add_section_divider
            # 從 title 移除「Part X:」prefix，因為 section_num 已經顯示
            import re as _re
            section_title = _re.sub(
                r"^(Part\s+\d+|Chapter\s+\d+|Section\s+\d+)\s*[::]?\s*",
                "",
                slide_content.title,
                flags=_re.IGNORECASE,
            ).strip()
            add_section_divider(
                prs,
                section_num=body.get("section_num", ""),
                section_title=section_title,
                section_subtitle=body.get("section_subtitle", ""),
                theme=theme,
            )
        else:
            # 一般投影片
            from ..pptx_helpers import add_blank_slide
            slide = add_blank_slide(prs)
            build_slide(
                slide, slide_content,
                theme=theme,
                slide_num=i,
                total=total,
            )

    # 儲存
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(output_path))
