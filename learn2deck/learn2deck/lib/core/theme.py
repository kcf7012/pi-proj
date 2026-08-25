"""
Theme 抽象 - 描述簡報的視覺風格

Theme 從 YAML 檔案載入，包含：
- colors: 顏色字典
- fonts: 字體字典（title/body/mono）
- font_sizes: 字級字典
- layout: 版面尺寸（inches）
- decorations: 裝飾元素（頂部橘條、品牌列等）
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from pptx.dml.color import RGBColor

from .exceptions import ThemeNotFoundError, ThemeValidationError


# 預設內建主題搜尋路徑
def _builtin_themes_dir() -> Path:
    """內建主題目錄（與本檔案同層的 themes/）"""
    return Path(__file__).parent.parent / "themes"


@dataclass
class Theme:
    """完整主題描述

    所有數值單位：
    - 顏色：6 位 hex 字串（"#C75A1A"）
    - 字體：字體名稱（"Calibri"）
    - 字級：pt
    - 版面：inches
    """

    name: str
    description: str = ""

    # 顏色
    colors: dict[str, str] = field(default_factory=dict)

    # 字體
    fonts: dict[str, str] = field(default_factory=dict)

    # 字級
    font_sizes: dict[str, int] = field(default_factory=dict)

    # 版面（inches）
    layout: dict[str, float] = field(default_factory=dict)

    # 裝飾
    decorations: dict[str, Any] = field(default_factory=dict)

    # === 顏色存取 ===
    def get_color(self, name: str) -> RGBColor:
        """取得 RGBColor 物件（給 python-pptx 使用）"""
        hex_str = self.colors.get(name)
        if not hex_str:
            raise ThemeValidationError(
                f"Theme '{self.name}' 缺少顏色 '{name}'。"
                f"可用顏色：{list(self.colors.keys())}"
            )
        return _hex_to_rgbcolor(hex_str)

    def get_color_or_default(self, name: str, default: str = "#000000") -> RGBColor:
        """取得顏色，找不到時用預設值"""
        hex_str = self.colors.get(name, default)
        return _hex_to_rgbcolor(hex_str)

    # === 字體存取 ===
    def get_font(self, name: str) -> str:
        """取得字體名稱"""
        font = self.fonts.get(name)
        if not font:
            raise ThemeValidationError(
                f"Theme '{self.name}' 缺少字體 '{name}'。"
                f"可用字體：{list(self.fonts.keys())}"
            )
        return font

    # === 字級存取 ===
    def get_font_size(self, name: str) -> int:
        """取得字級（pt）"""
        size = self.font_sizes.get(name)
        if size is None:
            raise ThemeValidationError(
                f"Theme '{self.name}' 缺少字級 '{name}'。"
                f"可用字級：{list(self.font_sizes.keys())}"
            )
        return int(size)

    def get_font_size_or_default(self, name: str, default: int) -> int:
        """取得字級，找不到時用預設值"""
        return int(self.font_sizes.get(name, default))

    # === 版面存取 ===
    def get_layout(self, name: str) -> float:
        """取得版面尺寸（inches）"""
        value = self.layout.get(name)
        if value is None:
            raise ThemeValidationError(
                f"Theme '{self.name}' 缺少版面 '{name}'。"
                f"可用版面：{list(self.layout.keys())}"
            )
        return float(value)

    def get_layout_or_default(self, name: str, default: float) -> float:
        """取得版面尺寸，找不到時用預設值"""
        return float(self.layout.get(name, default))


def _hex_to_rgbcolor(hex_str: str) -> RGBColor:
    """hex 字串 → RGBColor

    支援 "#C75A1A" 或 "C75A1A" 格式
    """
    hex_str = hex_str.lstrip("#")
    if len(hex_str) != 6:
        raise ThemeValidationError(
            f"顏色格式錯誤：'{hex_str}' 應為 6 位 hex（如 'C75A1A'）"
        )
    try:
        r = int(hex_str[0:2], 16)
        g = int(hex_str[2:4], 16)
        b = int(hex_str[4:6], 16)
    except ValueError as e:
        raise ThemeValidationError(f"顏色格式錯誤：'{hex_str}' - {e}") from e
    return RGBColor(r, g, b)


# === 載入器 ===
def load_theme(name_or_path: str) -> Theme:
    """載入主題

    Args:
        name_or_path: 主題名稱（"claude-orange"）或 YAML 檔案路徑

    Returns:
        Theme 物件

    Raises:
        ThemeNotFoundError: 找不到主題
        ThemeValidationError: 主題格式錯誤
    """
    # 判斷是路徑還是名稱
    path = Path(name_or_path)
    if path.exists() and path.is_file():
        theme_path = path
    else:
        # 嘗試從內建主題目錄找
        theme_path = _builtin_themes_dir() / f"{name_or_path}.yaml"
        if not theme_path.exists():
            raise ThemeNotFoundError(
                f"找不到主題：'{name_or_path}'。"
                f"已搜尋：{name_or_path} 與 {_builtin_themes_dir() / (name_or_path + '.yaml')}"
            )

    return _load_theme_from_file(theme_path)


def _load_theme_from_file(path: Path) -> Theme:
    """從 YAML 檔案載入主題"""
    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ThemeValidationError(f"主題 YAML 解析失敗：{path} - {e}") from e

    if not isinstance(data, dict):
        raise ThemeValidationError(f"主題 YAML 必須是字典，收到 {type(data)}")

    return Theme(
        name=data.get("name", path.stem),
        description=data.get("description", ""),
        colors=data.get("colors", {}),
        fonts=data.get("fonts", {}),
        font_sizes=data.get("font_sizes", {}),
        layout=data.get("layout", {}),
        decorations=data.get("decorations", {}),
    )


def list_builtin_themes() -> list[str]:
    """列出所有可用的內建主題"""
    themes_dir = _builtin_themes_dir()
    if not themes_dir.exists():
        return []
    return sorted(p.stem for p in themes_dir.glob("*.yaml"))
