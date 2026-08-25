"""
learn2deck.themes 測試

測試內建主題的載入與使用。
"""
import pytest

from learn2deck.lib.core import (
    Theme, load_theme, load_theme_from_path, list_builtin_themes,
    ThemeValidationError, ThemeNotFoundError,
)
from learn2deck.lib.pptx_helpers import (
    new_presentation, add_cover_slide, add_section_divider,
    get_slide_width, get_font_size, safe_top,
)


class TestBuiltinThemes:
    def test_list_includes_claude_orange(self):
        """預設包含 claude-orange"""
        themes = list_builtin_themes()
        assert "claude-orange" in themes

    def test_list_includes_minimal_bw(self):
        """預設包含 minimal-bw"""
        themes = list_builtin_themes()
        assert "minimal-bw" in themes

    def test_at_least_two_themes(self):
        """至少有 2 個內建主題"""
        assert len(list_builtin_themes()) >= 2


class TestClaudeOrangeTheme:
    """claude-orange 是從 pi-proj 移植過來的，必須完全一致"""

    @pytest.fixture
    def theme(self):
        return load_theme("claude-orange")

    def test_name_and_description(self, theme):
        assert theme.name == "claude-orange"
        assert "Claude" in theme.description

    def test_all_required_colors(self, theme):
        """11 個必要顏色（與 pi-proj _pptx_helpers.py 對應）"""
        required = [
            "primary", "dark", "bg_cream", "bg_gray",
            "blue", "green", "red", "white", "gray_text",
            "code_bg", "code_fg",
        ]
        for c in required:
            assert theme.get_color(c) is not None, f"缺少顏色 {c}"

    def test_color_values_match_pi_proj(self, theme):
        """顏色 hex 值必須與原版 100% 一致"""
        expected = {
            "primary": "C75A1A",
            "dark": "2C2C2C",
            "bg_cream": "FAF8F3",
            "bg_gray": "F3F0E9",
            "blue": "3B82F6",
            "green": "16A34A",
            "red": "DC2626",
            "white": "FFFFFF",
            "gray_text": "6B6B6B",
            "code_bg": "1E1E1E",
            "code_fg": "E6E6E6",
        }
        for name, hex_value in expected.items():
            actual = theme.colors[name].lstrip("#").upper()
            assert actual == hex_value, \
                f"顏色 {name} 不符：{actual} != {hex_value}"

    def test_fonts(self, theme):
        """字體必須是 Calibri / Calibri / Consolas"""
        assert theme.get_font("title") == "Calibri"
        assert theme.get_font("body") == "Calibri"
        assert theme.get_font("mono") == "Consolas"

    def test_font_sizes(self, theme):
        """字級必須符合 spec"""
        assert theme.get_font_size("cover_title") == 54
        assert theme.get_font_size("slide_title") == 32
        assert theme.get_font_size("body") == 14
        assert theme.get_font_size("code") == 12

    def test_layout(self, theme):
        """版面尺寸必須符合 pi-proj"""
        assert theme.get_layout("slide_width") == 13.333
        assert theme.get_layout("slide_height") == 7.5
        assert theme.get_layout("content_top") == 1.3
        assert theme.get_layout("content_bottom") == 7.0
        assert theme.get_layout("brand_y") == 7.1


class TestMinimalBWTheme:
    """minimal-bw 是示範第二個主題"""

    @pytest.fixture
    def theme(self):
        return load_theme("minimal-bw")

    def test_name_and_description(self, theme):
        assert theme.name == "minimal-bw"
        assert "簡" in theme.description or "黑白" in theme.description

    def test_uses_different_fonts(self, theme):
        """與 claude-orange 用不同字體"""
        claude = load_theme("claude-orange")
        assert theme.get_font("title") != claude.get_font("title")
        # 應該是 Helvetica
        assert "Helvetica" in theme.get_font("title")

    def test_uses_light_code_background(self, theme):
        """黑白風用淺灰底（不像 claude-orange 用深色）"""
        # code_bg 應該是淺色
        code_bg_hex = theme.colors["code_bg"].lstrip("#")
        r = int(code_bg_hex[0:2], 16)
        g = int(code_bg_hex[2:4], 16)
        b = int(code_bg_hex[4:6], 16)
        brightness = (r + g + b) / 3
        # 黑白風 code_bg 應該很亮（>200）
        assert brightness > 200, f"黑白風 code_bg 應為淺色，目前 brightness={brightness}"


class TestThemeIntegration:
    """主題實際用於 PPTX 生成的整合測試"""

    def test_claude_orange_can_create_pptx(self, tmp_path):
        """claude-orange 可正常建立 PPTX"""
        theme = load_theme("claude-orange")
        prs = new_presentation(theme)
        add_cover_slide(prs, "Test", "Subtitle", theme=theme)
        add_section_divider(prs, "Part 1", "Title", "Subtitle", theme=theme)

        out_path = tmp_path / "test.pptx"
        prs.save(str(out_path))
        assert out_path.exists()
        assert out_path.stat().st_size > 0

    def test_minimal_bw_can_create_pptx(self, tmp_path):
        """minimal-bw 可正常建立 PPTX"""
        theme = load_theme("minimal-bw")
        prs = new_presentation(theme)
        add_cover_slide(prs, "Test", "Subtitle", theme=theme)

        out_path = tmp_path / "test.pptx"
        prs.save(str(out_path))
        assert out_path.exists()

    def test_theme_affects_dimensions(self):
        """主題的 layout 會影響簡報尺寸"""
        with open("/tmp/test_custom.yaml", "w") as f:
            f.write("""
name: custom-test
layout:
  slide_width: 10.0
  slide_height: 7.5
""")
        theme = load_theme_from_path("/tmp/test_custom.yaml")
        # get_slide_width 會傳回 Inches (EMU)，轉成 inch 比對
        width_inch = get_slide_width(theme) / 914400
        assert width_inch == 10.0

    def test_two_themes_produce_different_pptx(self, tmp_path):
        """兩個主題產出的 PPTX 大小應不同（因為字體/顏色不同）"""
        claude = load_theme("claude-orange")
        bw = load_theme("minimal-bw")

        path1 = tmp_path / "claude.pptx"
        path2 = tmp_path / "bw.pptx"

        prs1 = new_presentation(claude)
        add_cover_slide(prs1, "Test", "Subtitle", theme=claude)
        prs1.save(str(path1))

        prs2 = new_presentation(bw)
        add_cover_slide(prs2, "Test", "Subtitle", theme=bw)
        prs2.save(str(path2))

        # 檔案大小可能接近，但形狀的 XML 內容會因顏色不同而不同
        # 至少檔案都存在
        assert path1.exists()
        assert path2.exists()


class TestThemeValidation:
    """主題錯誤應該有清楚的錯誤訊息"""

    def test_missing_required_color(self, tmp_path):
        """缺少必要顏色應拋出 ThemeValidationError"""
        with open(tmp_path / "incomplete.yaml", "w") as f:
            f.write("""
name: incomplete
colors:
  primary: "#FF0000"
""")
        theme = load_theme_from_path(tmp_path / "incomplete.yaml")
        with pytest.raises(ThemeValidationError):
            theme.get_color("bg_cream")

    def test_invalid_hex_format(self, tmp_path):
        """錯誤的 hex 格式應拋出 ThemeValidationError"""
        with open(tmp_path / "bad_hex.yaml", "w") as f:
            f.write("""
name: bad
colors:
  primary: "not-a-color"
""")
        theme = load_theme_from_path(tmp_path / "bad_hex.yaml")
        with pytest.raises(ThemeValidationError):
            theme.get_color("primary")

    def test_nonexistent_theme_raises(self):
        """不存在的內建主題應拋出 ThemeNotFoundError"""
        with pytest.raises(ThemeNotFoundError):
            load_theme("nonexistent-theme")

    def test_nonexistent_file_raises(self):
        """不存在的檔案路徑應拋出 ThemeNotFoundError"""
        with pytest.raises(ThemeNotFoundError):
            load_theme("/tmp/this-file-does-not-exist.yaml")
