"""
learn2deck 版面常數與計算工具

提供：
- 簡報尺寸常數（16:9）
- 安全區域定義
- 自動從 theme 讀取版面參數
"""
from __future__ import annotations

from pptx.util import Inches

from ..core import Theme


# === 簡報尺寸（16:9）===
# 這些是預設值，可被 theme.layout 覆寫
DEFAULT_SLIDE_WIDTH = Inches(13.333)
DEFAULT_SLIDE_HEIGHT = Inches(7.5)


# === 版面常數對照表 ===
# key: 邏輯名稱 → default value (inches)
DEFAULT_LAYOUT = {
    "slide_width": 13.333,
    "slide_height": 7.5,
    "content_top": 1.3,
    "content_bottom": 7.0,
    "brand_y": 7.1,
    "title_top": 0.3,
    "title_height": 0.7,
    "subtitle_top": 1.0,
    "subtitle_height": 0.4,
    "content_left": 0.5,
    "content_right_margin": 0.5,
    "column_gap": 0.13,
}


def get_layout_value(theme: Theme | None, key: str) -> float:
    """從 theme 取得版面值，沒設就用預設

    Args:
        theme: Theme 物件（可為 None，自動用預設）
        key: 版面參數名稱

    Returns:
        浮點數值（inches）
    """
    default = DEFAULT_LAYOUT.get(key, 0.0)
    if theme is None:
        return default
    return theme.get_layout_or_default(key, default)


def get_slide_width(theme: Theme | None = None):
    """取得簡報寬度（Inches 物件）"""
    return Inches(get_layout_value(theme, "slide_width"))


def get_slide_height(theme: Theme | None = None):
    """取得簡報高度（Inches 物件）"""
    return Inches(get_layout_value(theme, "slide_height"))


# === 安全區域計算 ===

def safe_top(theme: Theme | None = None) -> float:
    """內容頂部 Y 座標（標題列下方）"""
    return get_layout_value(theme, "content_top")


def safe_bottom(theme: Theme | None = None) -> float:
    """內容底部 Y 座標（品牌列上方）"""
    return get_layout_value(theme, "content_bottom")


def safe_height(theme: Theme | None = None) -> float:
    """內容可用高度"""
    return safe_bottom(theme) - safe_top(theme)


def content_left(theme: Theme | None = None) -> float:
    """內容左邊界"""
    return get_layout_value(theme, "content_left")


def content_width(theme: Theme | None = None) -> float:
    """內容可用寬度"""
    return (get_layout_value(theme, "slide_width")
            - get_layout_value(theme, "content_left")
            - get_layout_value(theme, "content_right_margin"))


# === 字級計算 ===

def get_font_size(theme: Theme | None, key: str, default: int) -> int:
    """從 theme 取得字級，沒設就用傳入的 default"""
    if theme is None:
        return default
    return theme.get_font_size_or_default(key, default)


# === 行高計算（給驗證器用） ===
# 根據字級估算每行的高度（inches）
LINE_HEIGHTS = {
    7: 0.13,
    8: 0.14,
    9: 0.15,
    10: 0.17,
    11: 0.18,
    12: 0.20,
    13: 0.22,
    14: 0.23,
    15: 0.25,
    16: 0.27,
    18: 0.30,
    20: 0.33,
    22: 0.37,
    32: 0.53,
    40: 0.67,
    54: 0.90,
    96: 1.60,
}


def estimate_line_height(font_size: int) -> float:
    """估算給定字級的單行高度（inches）"""
    return LINE_HEIGHTS.get(font_size, font_size / 72 * 1.2)  # fallback: 1.2x font height
