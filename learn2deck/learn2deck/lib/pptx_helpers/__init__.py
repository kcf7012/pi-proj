"""learn2deck.pptx_helpers - python-pptx 底層封裝"""
from .layout import (
    DEFAULT_LAYOUT,
    DEFAULT_SLIDE_WIDTH,
    DEFAULT_SLIDE_HEIGHT,
    LINE_HEIGHTS,
    get_layout_value,
    get_slide_width,
    get_slide_height,
    safe_top,
    safe_bottom,
    safe_height,
    content_left,
    content_width,
    get_font_size,
    estimate_line_height,
)
from .shapes import (
    new_presentation,
    add_blank_slide,
    set_slide_bg,
    add_title_bar,
    add_text_block,
    add_bullet_list,
    add_code_block,
    add_callout,
    add_comparison_table,
    add_flow_box,
    add_arrow,
)
from .pages import (
    add_cover_slide,
    add_section_divider,
    add_summary_slide,
    add_two_column_compare,
)

__all__ = [
    # layout
    "DEFAULT_LAYOUT", "DEFAULT_SLIDE_WIDTH", "DEFAULT_SLIDE_HEIGHT", "LINE_HEIGHTS",
    "get_layout_value", "get_slide_width", "get_slide_height",
    "safe_top", "safe_bottom", "safe_height",
    "content_left", "content_width", "get_font_size", "estimate_line_height",
    # shapes
    "new_presentation", "add_blank_slide", "set_slide_bg", "add_title_bar",
    "add_text_block", "add_bullet_list", "add_code_block", "add_callout",
    "add_comparison_table", "add_flow_box", "add_arrow",
    # pages
    "add_cover_slide", "add_section_divider", "add_summary_slide", "add_two_column_compare",
]
