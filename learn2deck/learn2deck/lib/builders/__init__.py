"""learn2deck.builders - 9 種投影片版型 builder"""
from .base import BaseBuilder, build_slide, build_full_deck
from .cover import CoverBuilder
from .objectives import ObjectivesBuilder
from .section_divider import SectionDividerBuilder
from .title_content import TitleContentBuilder
from .title_table import TitleTableBuilder
from .title_code import TitleCodeBuilder
from .two_column import TwoColumnBuilder
from .grid_cards import GridCardsBuilder
from .summary import SummaryBuilder

__all__ = [
    "BaseBuilder",
    "build_slide",
    "build_full_deck",
    "CoverBuilder",
    "ObjectivesBuilder",
    "SectionDividerBuilder",
    "TitleContentBuilder",
    "TitleTableBuilder",
    "TitleCodeBuilder",
    "TwoColumnBuilder",
    "GridCardsBuilder",
    "SummaryBuilder",
]
