"""
learn2deck.core 單元測試

測試核心資料結構（SlideType, SlideContent, DeckSpec, Theme）。
"""
import pytest

from learn2deck.lib.core import (
    SlideType, SlideContent, DeckSpec, Theme,
    load_theme, list_builtin_themes,
    ThemeNotFoundError, ThemeValidationError, Learn2deckError,
    ParseError, BuildError,
)


# === SlideType ===
class TestSlideType:
    def test_values(self):
        """所有 10 種版型都應該列舉出來"""
        expected = [
            "cover", "objectives", "section", "summary", "callout",
            "title_content", "title_table", "title_code",
            "two_column", "grid_cards",
        ]
        assert set(SlideType.values()) == set(expected)

    def test_string_compatibility(self):
        """SlideType 應該可以直接當字串用（str Enum）"""
        assert SlideType.COVER == "cover"
        assert SlideType("cover") == SlideType.COVER

    def test_unknown_raises(self):
        """未知的版型應該 ValueError"""
        with pytest.raises(ValueError):
            SlideType("unknown_type")


# === SlideContent ===
class TestSlideContent:
    def test_minimal_creation(self):
        """最小建構只需 type 與 title"""
        s = SlideContent(type=SlideType.COVER, title="My Title")
        assert s.type == SlideType.COVER
        assert s.title == "My Title"
        assert s.subtitle is None
        assert s.body is None
        assert s.slide_num is None
        assert s.source_ref is None
        assert s.extra == {}

    def test_full_creation(self):
        """完整建構"""
        s = SlideContent(
            type=SlideType.TITLE_TABLE,
            title="Comparison",
            subtitle="vs Other",
            body={"headers": ["A", "B"], "rows": [["1", "2"]]},
            slide_num=3,
            source_ref="## Comparison",
            extra={"lang": "zh-TW"},
        )
        assert s.subtitle == "vs Other"
        assert s.body == {"headers": ["A", "B"], "rows": [["1", "2"]]}
        assert s.slide_num == 3

    def test_serialization_roundtrip(self):
        """序列化與反序列化應保持一致"""
        original = SlideContent(
            type=SlideType.TITLE_CODE,
            title="Code",
            body={"code": "print('hi')", "language": "python"},
        )
        data = original.to_dict()
        restored = SlideContent.from_dict(data)
        assert restored.type == original.type
        assert restored.title == original.title
        assert restored.body == original.body


# === DeckSpec ===
class TestDeckSpec:
    def test_minimal_creation(self):
        d = DeckSpec(title="Test")
        assert d.title == "Test"
        assert d.subtitle == ""
        assert d.theme == "claude-orange"
        assert d.slides == []
        assert d.total_slides == 0

    def test_add_slide_auto_numbers(self):
        """add_slide 應自動編號（1-indexed）"""
        d = DeckSpec(title="Test")
        d.add_slide(SlideContent(type=SlideType.COVER, title="A"))
        d.add_slide(SlideContent(type=SlideType.OBJECTIVES, title="B"))
        d.add_slide(SlideContent(type=SlideType.SUMMARY, title="C"))
        assert d.slides[0].slide_num == 1
        assert d.slides[1].slide_num == 2
        assert d.slides[2].slide_num == 3
        assert d.total_slides == 3

    def test_get_slide(self):
        d = DeckSpec(title="Test")
        d.add_slide(SlideContent(type=SlideType.COVER, title="A"))
        d.add_slide(SlideContent(type=SlideType.OBJECTIVES, title="B"))
        assert d.get_slide(1).title == "A"
        assert d.get_slide(2).title == "B"
        assert d.get_slide(3) is None
        assert d.get_slide(0) is None

    def test_slide_types_count(self):
        d = DeckSpec(title="Test")
        d.add_slide(SlideContent(type=SlideType.COVER, title="A"))
        d.add_slide(SlideContent(type=SlideType.OBJECTIVES, title="B"))
        d.add_slide(SlideContent(type=SlideType.OBJECTIVES, title="C"))
        d.add_slide(SlideContent(type=SlideType.SUMMARY, title="D"))
        assert d.slide_types_count == {
            "cover": 1,
            "objectives": 2,
            "summary": 1,
        }

    def test_serialization_roundtrip(self):
        d = DeckSpec(
            title="Test",
            subtitle="Sub",
            theme="minimal-bw",
            source_path="test.md",
        )
        d.add_slide(SlideContent(type=SlideType.COVER, title="A"))
        data = d.to_dict()
        restored = DeckSpec.from_dict(data)
        assert restored.title == d.title
        assert restored.subtitle == d.subtitle
        assert restored.theme == d.theme
        assert restored.source_path == d.source_path
        assert len(restored.slides) == 1
        assert restored.slides[0].title == "A"

    def test_validate_empty_deck(self):
        d = DeckSpec(title="")
        errors = d.validate()
        assert "DeckSpec.title 不可為空" in errors
        assert any("slides 不可為空" in e for e in errors)

    def test_validate_valid_deck(self):
        d = DeckSpec(title="Valid")
        d.add_slide(SlideContent(type=SlideType.COVER, title="A"))
        d.add_slide(SlideContent(type=SlideType.OBJECTIVES, title="B"))
        assert d.validate() == []


# === Theme ===
class TestTheme:
    def test_builtin_list_not_empty(self):
        """內建主題目錄應至少有幾個主題（Phase 4 後變非空）"""
        themes = list_builtin_themes()
        assert len(themes) >= 2
        assert "claude-orange" in themes

    def test_load_nonexistent_raises(self):
        """不存在的路徑應拋出 ThemeNotFoundError"""
        with pytest.raises(ThemeNotFoundError) as exc_info:
            load_theme("/nonexistent/path.yaml")
        assert "找不到主題" in str(exc_info.value)

    def test_load_name_not_found(self):
        """找不到的內建主題應拋出 ThemeNotFoundError"""
        with pytest.raises(ThemeNotFoundError):
            load_theme("nonexistent-theme")


# === 例外階層 ===
class TestExceptionHierarchy:
    def test_all_inherit_from_base(self):
        """所有 learn2deck 例外都應繼承自 Learn2deckError"""
        from learn2deck.lib.core.exceptions import (
            ParseError, FrontmatterError, InvalidSlideTypeError,
            ThemeError, ThemeNotFoundError, ThemeValidationError,
            BuildError, MissingFieldError,
            ValidationError, ValidationRuleError,
            OutputError, AgentError, CostLimitExceeded, LLMUnavailable,
        )
        exceptions = [
            ParseError, FrontmatterError, InvalidSlideTypeError,
            ThemeError, ThemeNotFoundError, ThemeValidationError,
            BuildError, MissingFieldError,
            ValidationError, ValidationRuleError,
            OutputError, AgentError, CostLimitExceeded, LLMUnavailable,
        ]
        for exc in exceptions:
            assert issubclass(exc, Learn2deckError), \
                f"{exc.__name__} 應該繼承自 Learn2deckError"

    def test_catch_all_with_base(self):
        """用 Learn2deckError 應該能捕捉所有 learn2deck 例外"""
        try:
            raise ThemeNotFoundError("test")
        except Learn2deckError as e:
            assert "test" in str(e)


# === 主題載入（mock YAML 測試） ===
class TestThemeLoading:
    def test_load_from_temp_yaml(self, tmp_path):
        """從臨時 YAML 檔案載入主題"""
        yaml_content = """
name: test-theme
description: A test theme

colors:
  primary: "#FF0000"
  dark: "#000000"
  bg_cream: "#FFFFFF"
  bg_gray: "#EEEEEE"

fonts:
  title: "Arial"
  body: "Arial"
  mono: "Courier New"

font_sizes:
  cover_title: 50
  slide_title: 30
  body: 14

layout:
  slide_width: 13.333
  slide_height: 7.5
  content_top: 1.3
  content_bottom: 7.0

decorations:
  top_accent_bar:
    enabled: true
    height: 0.15
"""
        yaml_path = tmp_path / "test-theme.yaml"
        yaml_path.write_text(yaml_content)

        theme = load_theme(str(yaml_path))
        assert theme.name == "test-theme"
        assert theme.description == "A test theme"
        assert theme.get_color("primary") is not None
        assert theme.get_font("title") == "Arial"
        assert theme.get_font_size("cover_title") == 50
        assert theme.get_layout("slide_width") == 13.333

    def test_get_missing_color_raises(self, tmp_path):
        yaml_content = """
name: incomplete
colors:
  primary: "#FF0000"
"""
        yaml_path = tmp_path / "incomplete.yaml"
        yaml_path.write_text(yaml_content)

        theme = load_theme(str(yaml_path))
        with pytest.raises(ThemeValidationError):
            theme.get_color("nonexistent_color")

    def test_hex_format_validation(self, tmp_path):
        """錯誤的 hex 格式應拋出 ThemeValidationError"""
        yaml_content = """
name: bad-hex
colors:
  primary: "not-a-color"
"""
        yaml_path = tmp_path / "bad-hex.yaml"
        yaml_path.write_text(yaml_content)

        theme = load_theme(str(yaml_path))
        with pytest.raises(ThemeValidationError):
            theme.get_color("primary")
