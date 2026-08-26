"""
learn2deck.parsers 單元測試

測試：
- frontmatter 解析
- inference 自動推斷
- markdown 主解析器
- 8 份現有 .md 的解析結果
"""
import re
from pathlib import Path

import pytest

from learn2deck.lib.parsers import (
    parse_content,
    parse_frontmatter,
    parse_markdown,
    infer_slide_type,
    detect_code_blocks,
    detect_markdown_table,
    has_pros_cons_structure,
    count_h3_subsections,
    extract_code_block,
    extract_markdown_table,
    extract_bullet_items,
    extract_paragraph_text,
    strip_markdown_inline,
    FrontmatterResult,
)
from learn2deck.lib.core import (
    DeckSpec, FrontmatterError, ParseError, SlideType,
)


# === Frontmatter ===
class TestFrontmatter:
    def test_no_frontmatter(self):
        """沒有 frontmatter 的內容"""
        content = "# Title\n\nbody"
        result = parse_frontmatter(content)
        assert result.has_frontmatter is False
        assert result.metadata == {}
        assert result.body == content

    def test_simple_frontmatter(self):
        """簡單 frontmatter"""
        content = """---
title: Test
author: Kenny
---

# Body"""
        result = parse_frontmatter(content)
        assert result.has_frontmatter is True
        assert result.metadata == {"title": "Test", "author": "Kenny"}
        assert "Body" in result.body

    def test_nested_frontmatter(self):
        """巢狀結構的 frontmatter"""
        content = """---
deck:
  title: Test
  meta:
    author: Kenny
---

# Body"""
        result = parse_frontmatter(content)
        assert result.metadata["deck"]["title"] == "Test"
        assert result.metadata["deck"]["meta"]["author"] == "Kenny"

    def test_invalid_yaml_raises(self):
        """YAML 錯誤應拋出 FrontmatterError"""
        content = """---
title: [unclosed bracket
---

# Body"""
        with pytest.raises(FrontmatterError):
            parse_frontmatter(content)

    def test_missing_end_marker_raises(self):
        """缺少結尾 --- 應拋出"""
        content = """---
title: Test

# Body without end marker"""
        with pytest.raises(FrontmatterError):
            parse_frontmatter(content)

    def test_empty_frontmatter(self):
        """空 frontmatter"""
        content = """---
---

# Body"""
        result = parse_frontmatter(content)
        assert result.has_frontmatter is True
        assert result.metadata == {}


# === Inference ===
class TestInference:
    def test_objectives_keyword(self):
        """「學習目標」標題應推斷為 OBJECTIVES"""
        slide_type, conf = infer_slide_type("本章你會學到")
        assert slide_type == SlideType.OBJECTIVES
        assert conf >= 0.9

    def test_objectives_english(self):
        """英文 objectives 關鍵字"""
        slide_type, _ = infer_slide_type("Learning Objectives")
        assert slide_type == SlideType.OBJECTIVES

    def test_section_keyword(self):
        """「Part 1」應推斷為 SECTION_DIVIDER"""
        slide_type, conf = infer_slide_type("Part 1: 快速開始")
        assert slide_type == SlideType.SECTION_DIVIDER
        assert conf >= 0.9

    def test_section_chinese(self):
        """「章節 N」應推斷為 SECTION_DIVIDER"""
        slide_type, _ = infer_slide_type("第 3 章節")
        assert slide_type == SlideType.SECTION_DIVIDER

    def test_table_detection(self):
        """有 table 應推斷為 TITLE_TABLE"""
        slide_type, conf = infer_slide_type(
            "Some Title", "",
            has_table=True,
        )
        assert slide_type == SlideType.TITLE_TABLE
        assert conf >= 0.85

    def test_code_block_detection(self):
        """有 code block 應推斷為 TITLE_CODE"""
        slide_type, conf = infer_slide_type(
            "Code Example", "",
            has_code_block=True,
        )
        assert slide_type == SlideType.TITLE_CODE
        assert conf >= 0.85

    def test_grid_cards_3_h3(self):
        """3+ 個 H3 子標題應推斷為 GRID_CARDS"""
        slide_type, conf = infer_slide_type(
            "Some Title", "",
            has_h3_subsections=3,
        )
        assert slide_type == SlideType.GRID_CARDS
        assert 0.5 <= conf < 0.9

    def test_two_column_pros_cons(self):
        """✅/❌ 並列應推斷為 TWO_COLUMN"""
        slide_type, conf = infer_slide_type(
            "Some Title", "",
            has_pros_cons=True,
        )
        assert slide_type == SlideType.TWO_COLUMN
        assert 0.5 <= conf < 0.9

    def test_default_title_content(self):
        """預設是 TITLE_CONTENT"""
        slide_type, conf = infer_slide_type("Some Random Title", "")
        assert slide_type == SlideType.TITLE_CONTENT
        assert conf < 0.7


# === Detection helpers ===
class TestDetectionHelpers:
    def test_detect_code_blocks(self):
        body = "Some text\n```python\ncode\n```\nMore text"
        assert detect_code_blocks(body) is True

    def test_detect_no_code_blocks(self):
        body = "Just text, no code"
        assert detect_code_blocks(body) is False

    def test_detect_table(self):
        body = """| Col1 | Col2 |
| --- | --- |
| a | b |"""
        assert detect_markdown_table(body) is True

    def test_detect_no_table(self):
        body = "Just text, no |---| line"
        assert detect_markdown_table(body) is False

    def test_has_pros_cons(self):
        body = "✅ Good things\n❌ Bad things"
        assert has_pros_cons_structure(body) is True

    def test_no_pros_cons(self):
        body = "Just regular text"
        assert has_pros_cons_structure(body) is False

    def test_count_h3(self):
        body = "## H2\n### H3a\n### H3b\n## H2b\n### H3c"
        assert count_h3_subsections(body) == 3


# === Extraction helpers ===
class TestExtractionHelpers:
    def test_extract_code_block(self):
        body = "Before\n```python\nprint('hi')\n```\nAfter"
        code = extract_code_block(body)
        assert "print('hi')" in code

    def test_extract_table(self):
        body = """| A | B |
| --- | --- |
| 1 | 2 |
| 3 | 4 |"""
        headers, rows = extract_markdown_table(body)
        assert headers == ["A", "B"]
        assert rows == [["1", "2"], ["3", "4"]]

    def test_extract_bullets(self):
        body = """Some text
- Item 1
- Item 2
* Item 3"""
        items = extract_bullet_items(body)
        assert items == ["Item 1", "Item 2", "Item 3"]

    def test_extract_paragraph(self):
        body = """# Title
> blockquote

text line 1
text line 2
"""
        para = extract_paragraph_text(body)
        # 應包含文字但不包含 # 或 > 標記
        assert "text line 1" in para
        assert "# Title" not in para
        assert ">" not in para


class TestStripMarkdownInline:
    """markdown inline 標記移除"""

    def test_inline_code(self):
        assert strip_markdown_inline("run `ls -la` here") == "run ls -la here"

    def test_bold_double_asterisk(self):
        assert strip_markdown_inline("**bold text**") == "bold text"

    def test_bold_underscore(self):
        assert strip_markdown_inline("__bold text__") == "bold text"

    def test_italic_asterisk(self):
        assert strip_markdown_inline("*italic*") == "italic"

    def test_italic_underscore(self):
        assert strip_markdown_inline("_italic_") == "italic"

    def test_link(self):
        assert strip_markdown_inline("[text](https://example.com)") == "text"

    def test_combined(self):
        assert strip_markdown_inline("**`code-bold`**") == "code-bold"

    def test_table_cell_with_inline(self):
        """表格 cell 文字應被 strip"""
        body = """| A | B |
| --- | --- |
| `**bold**` | plain |"""
        headers, rows = extract_markdown_table(body)
        assert headers == ["A", "B"]
        # `` `**bold**` `` → **bold**（去反引號）→ bold（去 **）
        assert rows == [["bold", "plain"]]

    def test_bullet_with_inline(self):
        body = "- **bold item** with `code`"
        items = extract_bullet_items(body)
        assert items == ["bold item with code"]

    def test_paragraph_with_inline(self):
        body = "Some **bold** text with `code` here"
        para = extract_paragraph_text(body)
        assert para == "Some bold text with code here"


# === Markdown parser ===
class TestParseMarkdown:
    def test_basic_parse(self, tmp_path):
        """基本 Markdown 解析"""
        md = tmp_path / "test.md"
        md.write_text("""# Test Title

副標題說明

## Section 1

Content here

## Section 2

More content
""")
        deck = parse_markdown(md)
        assert deck.title == "Test Title"
        # 3 slides: COVER (auto-inserted) + Section 1 + Section 2
        assert len(deck.slides) == 3
        assert deck.slides[0].type == SlideType.COVER
        assert deck.slides[1].title == "Section 1"
        assert deck.slides[2].title == "Section 2"

    def test_objectives_section(self, tmp_path):
        """「學習目標」標題應推斷為 objectives"""
        md = tmp_path / "test.md"
        md.write_text("""# Test

## 本章你會學到

- 🎯 **Concept**: Basic idea
- 📦 **Tool**: How to use
- 🧪 **Test**: Verify
""")
        deck = parse_markdown(md)
        # slides[0] = COVER (auto), slides[1] = 本章你會學到
        obj = deck.slides[1]
        assert obj.type == SlideType.OBJECTIVES
        assert "items" in obj.body
        assert len(obj.body["items"]) >= 2

    def test_auto_cover_inserted(self, tmp_path):
        """沒 cover 時自動插入 COVER"""
        md = tmp_path / "test.md"
        md.write_text("""# My Title

> My subtitle

## First

content
""")
        deck = parse_markdown(md)
        assert deck.slides[0].type == SlideType.COVER
        assert deck.slides[0].title == "My Title"
        assert deck.slides[0].subtitle == "My subtitle"
        assert deck.slides[1].title == "First"

    def test_cover_tag_from_filename(self, tmp_path):
        """從檔名推斷 cover tag（例如 00-xxx.md → 「#00 · xxx」）"""
        md = tmp_path / "00-overview.md"
        md.write_text("""# Overview

## A

content
""")
        deck = parse_markdown(md)
        cover = deck.slides[0]
        assert cover.type == SlideType.COVER
        # tag 應該是「#0 · overview」（num 去前導 0）
        assert "overview" in cover.body.get("tag", "")

    def test_explicit_cover_not_duplicated(self, tmp_path):
        """如果有 explicit cover，不該重複插入"""
        md = tmp_path / "test.md"
        md.write_text("""# Title

## Slide: Cover

some content

## Section 1

content
""")
        deck = parse_markdown(md)
        cover_count = sum(1 for s in deck.slides if s.type == SlideType.COVER)
        assert cover_count == 1

    def test_skip_toc_section(self, tmp_path):
        """目錄章節應被跳過"""
        md = tmp_path / "test.md"
        md.write_text("""# Test

## 目錄

1. [First](#first)
2. [Second](#second)

## First

content

## Second

content
""")
        deck = parse_markdown(md)
        # 不應包含「目錄」
        assert not any(s.title == "目錄" for s in deck.slides)
        # 應有 First 與 Second
        titles = [s.title for s in deck.slides]
        assert "First" in titles
        assert "Second" in titles

    def test_summary_from_next_steps(self, tmp_path):
        """「下一步」章節應變成 summary"""
        md = tmp_path / "test.md"
        md.write_text("""# Test

## 下一步

- Read more
- Try it
""")
        deck = parse_markdown(md)
        summary = next((s for s in deck.slides if s.type == SlideType.SUMMARY), None)
        assert summary is not None
        assert "key_points" in summary.body
        assert "Read more" in summary.body["key_points"]

    def test_table_section(self, tmp_path):
        """含 table 的章節應推斷為 title_table"""
        md = tmp_path / "test.md"
        md.write_text("""# Test

## Comparison

| A | B |
| --- | --- |
| 1 | 2 |
""")
        deck = parse_markdown(md)
        # slides[0] = COVER (auto), slides[1] = Comparison
        comp = deck.slides[1]
        assert comp.type == SlideType.TITLE_TABLE
        assert "headers" in comp.body
        assert "rows" in comp.body

    def test_code_section(self, tmp_path):
        """含 code 的章節應推斷為 title_code"""
        md = tmp_path / "test.md"
        md.write_text("""# Test

## Example

```python
print('hello')
print('world')
print('!')
```
""")
        deck = parse_markdown(md)
        # slides[0] = COVER (auto), slides[1] = Example
        ex = deck.slides[1]
        assert ex.type == SlideType.TITLE_CODE
        assert "print('hello')" in ex.body["code"]

    def test_with_frontmatter(self, tmp_path):
        """有 frontmatter 的 Markdown"""
        md = tmp_path / "test.md"
        md.write_text("""---
deck:
  title: Custom Title
  subtitle: Custom Subtitle
  theme: minimal-bw
---

# Should be ignored

## Section 1

Content
""")
        deck = parse_markdown(md)
        assert deck.title == "Custom Title"
        assert deck.subtitle == "Custom Subtitle"
        assert deck.theme == "minimal-bw"

    def test_file_not_found_raises(self):
        """不存在的檔案應拋出 FileNotFoundError"""
        with pytest.raises(FileNotFoundError):
            parse_markdown("/nonexistent/path.md")


# === Real 8 .md 檔案 ===
class TestRealMarkdownFiles:
    """用實際 8 份 .md 測試解析器

    確保能正確處理各種真實的章節結構。
    """

    @pytest.fixture
    def md_dir(self):
        return Path("/home/elan/pi-proj")

    @pytest.mark.parametrize("filename,expected_min,expected_max", [
        ("00-claude-code-plugins-series.md", 25, 35),  # 30 slides（含 cover + 5 section + 24 content）
        ("01-plugin-marketplaces.md", 30, 40),  # 35 slides（對齊舊版）
        ("02-plugins.md", 20, 30),  # 25 slides（對齊舊版 02-plugins.pptx）
        ("03-plugins-reference.md", 5, 25),
        ("04-skills.md", 15, 40),
        ("05-subagents.md", 8, 25),
        ("06-hooks.md", 10, 30),
        ("07-discover-plugins.md", 10, 30),
    ])
    def test_parses_real_files(self, md_dir, filename, expected_min, expected_max):
        """8 份真實檔案都能解析且張數合理"""
        path = md_dir / filename
        deck = parse_markdown(path)
        assert expected_min <= deck.total_slides <= expected_max, \
            f"{filename}: {deck.total_slides} slides, expected {expected_min}-{expected_max}"
        # 至少有 title
        assert deck.title
        # 至少有一張不是 summary
        has_content = any(s.type != SlideType.SUMMARY for s in deck.slides)
        assert has_content, f"{filename} 沒有內容 slide"

    def test_all_real_files_have_valid_types(self, md_dir):
        """所有真實檔案的 slide_type 都是有效的 enum"""
        valid_types = set(SlideType)
        for filename in [
            "00-claude-code-plugins-series.md",
            "02-plugins.md",
            "04-skills.md",
            "06-hooks.md",
        ]:
            deck = parse_markdown(md_dir / filename)
            for slide in deck.slides:
                assert slide.type in valid_types, \
                    f"{filename}: 無效的 slide_type: {slide.type}"

    @pytest.mark.parametrize("filename", [
        "00-claude-code-plugins-series.md",
        "01-plugin-marketplaces.md",
        "02-plugins.md",
        "03-plugins-reference.md",
        "04-skills.md",
        "05-subagents.md",
        "06-hooks.md",
        "07-discover-plugins.md",
    ])
    def test_end_to_end_build_all_files(self, md_dir, filename, tmp_path):
        """8 份 .md 都能完整 parse + build 成 PPTX"""
        from learn2deck.lib.builders import build_full_deck

        deck = parse_markdown(md_dir / filename)
        out = tmp_path / f"{filename.replace('.md', '.pptx')}"
        build_full_deck(deck, str(out))
        assert out.exists()
        assert out.stat().st_size > 0


# === parse_content 主入口 ===
class TestParseContent:
    def test_parse_md(self, tmp_path):
        """parse_content 處理 .md"""
        md = tmp_path / "test.md"
        md.write_text("# Test\n\n## Section\n\ncontent")
        deck = parse_content(str(md))
        assert isinstance(deck, DeckSpec)
        assert deck.total_slides >= 1

    def test_parse_yaml_not_implemented(self, tmp_path):
        """parse_content 對 .yaml 拋出 NotImplementedError"""
        yaml = tmp_path / "test.yaml"
        yaml.write_text("title: Test")
        with pytest.raises(NotImplementedError):
            parse_content(str(yaml))

    def test_parse_nonexistent_raises(self):
        """不存在的檔案拋出 FileNotFoundError"""
        with pytest.raises(FileNotFoundError):
            parse_content("/tmp/does-not-exist.md")
