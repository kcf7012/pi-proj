"""learn2deck.parsers - 內容解析"""
from .frontmatter import parse_frontmatter, FrontmatterResult
from .markdown import parse_markdown
from .inference import (
    infer_slide_type,
    detect_code_blocks,
    detect_markdown_table,
    has_pros_cons_structure,
    count_h3_subsections,
    extract_code_block,
    extract_markdown_table,
    extract_bullet_items,
    extract_paragraph_text,
)


def parse_content(source_path: str) -> "DeckSpec":
    """主入口：從 .md 或 .yaml 檔案建立 DeckSpec

    自動偵測格式（未來支援 .yaml；目前只支援 .md）

    Args:
        source_path: 檔案路徑

    Returns:
        DeckSpec
    """
    from pathlib import Path
    path = Path(source_path)
    if path.suffix in (".yaml", ".yml"):
        # TODO: Phase 6+ 支援 YAML outline
        raise NotImplementedError("YAML outline 解析尚未實作，請用 .md")
    return parse_markdown(path)


__all__ = [
    "parse_content",
    "parse_markdown",
    "parse_frontmatter",
    "FrontmatterResult",
    "infer_slide_type",
    "detect_code_blocks",
    "detect_markdown_table",
    "has_pros_cons_structure",
    "count_h3_subsections",
    "extract_code_block",
    "extract_markdown_table",
    "extract_bullet_items",
    "extract_paragraph_text",
]


# 為了避免循環 import，這裡延遲 import
from ..core import DeckSpec  # noqa: E402
