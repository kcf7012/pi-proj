"""
Markdown 解析器 - 主入口

從 .md 檔案解析為 DeckSpec。

支援：
1. 純 Markdown（無 frontmatter）— 主要場景
2. 帶 YAML frontmatter
3. 帶「## Slide: <title>」明確標註的章節（spec 4.2.1 格式）
4. 自動推斷 slide_type（用 inference 模組）
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from ..core import (
    DeckSpec, InvalidSlideTypeError, MissingFieldError,
    ParseError, SlideContent, SlideType,
)
from .frontmatter import parse_frontmatter
from .inference import (
    count_h3_subsections, detect_code_blocks, detect_markdown_table,
    extract_bullet_items, extract_code_block, extract_markdown_table,
    extract_paragraph_text, has_pros_cons_structure, infer_slide_type,
    strip_markdown_inline,
)


# 明確標註的章節（spec 4.2.1 格式）
EXPLICIT_SECTION_RE = re.compile(r"^##\s+Slide:\s+(.+)$", re.MULTILINE)


def parse_markdown(source_path: str | Path) -> DeckSpec:
    """從 Markdown 檔案建立 DeckSpec

    Args:
        source_path: .md 檔案路徑

    Returns:
        DeckSpec

    Raises:
        ParseError: 解析失敗
        FileNotFoundError: 檔案不存在
    """
    path = Path(source_path)
    if not path.exists():
        raise FileNotFoundError(f"找不到檔案：{path}")

    content = path.read_text(encoding="utf-8")

    # 1. 解析 frontmatter
    fm = parse_frontmatter(content)
    body = fm.body
    metadata = fm.metadata

    # 2. 從 frontmatter 或檔案內容抽取標題
    title, subtitle, theme_name, source_ref = _extract_deck_metadata(
        metadata, body, path
    )

    # 3. 建立 DeckSpec
    deck = DeckSpec(
        title=title,
        subtitle=subtitle,
        theme=theme_name,
        source_path=str(path.absolute()),
        metadata={
            "has_frontmatter": fm.has_frontmatter,
            "frontmatter_keys": list(metadata.keys()),
        },
    )

    # 4. 解析章節為 slides
    if fm.has_frontmatter and "deck" in metadata:
        # 結構化 frontmatter（spec 4.2.1 風格）— 但目前不支援複雜結構
        # 暫時降級為普通章節解析
        pass

    slides = _parse_sections(body, deck.title)
    for slide in slides:
        deck.add_slide(slide)

    return deck


def _extract_deck_metadata(
    metadata: dict,
    body: str,
    path: Path,
) -> tuple[str, str, str, str | None]:
    """從 frontmatter 與 body 抽取 deck 等級的 metadata

    Returns:
        (title, subtitle, theme, source_ref)
    """
    # 優先從 frontmatter.deck 讀
    deck_meta = metadata.get("deck", {})

    title = deck_meta.get("title", "")
    subtitle = deck_meta.get("subtitle", "")
    theme = deck_meta.get("theme", "claude-orange")
    source_ref = deck_meta.get("source_ref", path.name)

    # 如果 frontmatter 沒有，從 body 第一個 H1 抽 title
    if not title:
        h1_match = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
        if h1_match:
            title = h1_match.group(1).strip()
        else:
            # 從檔名推斷
            title = path.stem

    # 副標題：第一個 H1 後的段落（去除 blockquote）
    if not subtitle:
        # 找到 H1 之後到下一個 H2 之前的內容
        m = re.search(r"^#\s+.+?\n+(.+?)(?=^##\s|\Z)", body, re.MULTILINE | re.DOTALL)
        if m:
            first_para = m.group(1).strip()
            # 移除 blockquote
            first_para = re.sub(r"^>\s*", "", first_para, flags=re.MULTILINE)
            # 移除多餘空行
            first_para = re.sub(r"\n\s*\n+", " ", first_para)
            # 取第一句（≤80 字）
            first_para = first_para.strip()
            if first_para and len(first_para) < 200:
                subtitle = first_para.split("\n")[0][:100]

    return title, subtitle, theme, source_ref


def _parse_sections(body: str, deck_title: str) -> list[SlideContent]:
    """解析 body 為 slides 列表

    策略：
    1. 第一個 H1 是 deck title（已抽過，不產生 slide）
    2. 找到所有 H2（含 ## Slide: prefix 與一般 ##）
    3. 每個 H2 之間的內容是 slide body
    4. 自動推斷 slide_type
    """
    slides: list[SlideContent] = []

    # 切分為章節（H2 為分隔點）
    # 跳過第一個 H1
    sections = _split_into_sections(body)

    for h2_title, h2_body, explicit in sections:
        # 跳過「目錄」章節
        if h2_title.strip() in ("目錄", "Table of Contents", "TOC"):
            continue

        # 跳過「下一步」章節（會在 summary 中處理）
        if h2_title.strip() in ("下一步", "Next Steps"):
            # 視為 summary 的 key_points
            items = extract_bullet_items(h2_body)
            if items:
                slides.append(SlideContent(
                    type=SlideType.SUMMARY,
                    title="下一步",
                    subtitle="延伸閱讀",
                    body={"key_points": items},
                ))
            continue

        slide = _build_slide_from_section(h2_title, h2_body, explicit)
        if slide is not None:
            slides.append(slide)

    return slides


def _split_into_sections(body: str) -> list[tuple[str, str, bool]]:
    """將 body 切分為 (h2_title, h2_body, is_explicit) 的列表

    - 跳過最開頭到第一個 H2 之間的內容（H1 + 副標）
    - 每個 H2 開始一個新章節
    """
    # 移除第一個 H1 與其後的 metadata
    body_without_h1 = re.sub(r"^#\s+.+?\n", "", body, count=1, flags=re.MULTILINE)

    # 找所有 H2 位置
    h2_positions = [(m.start(), m.end(), m.group(1).strip())
                    for m in re.finditer(r"^##\s+(.+)$", body_without_h1, re.MULTILINE)]

    if not h2_positions:
        return []

    sections: list[tuple[str, str, bool]] = []

    for i, (start, end, title) in enumerate(h2_positions):
        # 章節 body = 從這個 H2 結尾到下一個 H2 開頭（或檔案結尾）
        body_start = end
        body_end = h2_positions[i + 1][0] if i + 1 < len(h2_positions) else len(body_without_h1)
        section_body = body_without_h1[body_start:body_end]

        # 判斷是否明確標註的章節（spec 4.2.1 風格「## Slide: <title>」）
        explicit = title.startswith("Slide:")
        if explicit:
            # 移除 "Slide: " prefix
            title = title[7:].strip()

        sections.append((title, section_body, explicit))

    return sections


def _build_slide_from_section(
    title: str, body: str, explicit: bool
) -> SlideContent | None:
    """從一個章節建立 SlideContent

    Args:
        title: H2 標題（已清理 "Slide: " prefix）
        body: 章節內文
        explicit: 是否明確標註（spec 4.2.1 風格，未來支援）

    Returns:
        SlideContent 或 None（如果章節應該被跳過）
    """
    # 結構特徵偵測
    has_code = detect_code_blocks(body)
    has_table = detect_markdown_table(body)
    h3_count = count_h3_subsections(body)
    has_pc = has_pros_cons_structure(body)

    # 自動推斷 slide_type
    body_text = extract_paragraph_text(body)
    inferred_type, confidence = infer_slide_type(
        title=title,
        body_text=body_text,
        has_code_block=has_code,
        has_table=has_table,
        has_h3_subsections=h3_count,
        has_pros_cons=has_pc,
    )

    # 抽取 body 內容
    slide_body = _extract_slide_body(
        inferred_type, title, body,
        has_code=has_code, has_table=has_table,
        h3_count=h3_count, has_pc=has_pc,
    )

    # 副標題：第一段純文字
    subtitle = body_text.split("\n")[0] if body_text else None
    if subtitle and len(subtitle) > 80:
        subtitle = subtitle[:77] + "..."

    return SlideContent(
        type=inferred_type,
        title=strip_markdown_inline(title),
        subtitle=strip_markdown_inline(subtitle) if subtitle else None,
        body=slide_body,
        source_ref=strip_markdown_inline(title),
    )


def _extract_slide_body(
    slide_type: SlideType,
    title: str,
    body: str,
    has_code: bool,
    has_table: bool,
    h3_count: int,
    has_pc: bool,
) -> dict[str, Any]:
    """根據推斷的 slide_type 抽取對應的 body 內容

    Returns:
        body dict（符合該 slide_type 的 schema）
    """
    if slide_type == SlideType.TITLE_TABLE and has_table:
        headers, rows = extract_markdown_table(body)
        return {"headers": headers, "rows": rows}

    if slide_type == SlideType.TITLE_CODE and has_code:
        code = extract_code_block(body)
        # 嘗試從 code 區塊上方的 ``` 標記判斷語言
        lang_match = re.search(r"```(\w+)", body)
        lang = lang_match.group(1) if lang_match else "bash"
        return {"code": code, "language": lang}

    if slide_type == SlideType.GRID_CARDS and h3_count >= 3:
        # 從 H3 子標題抽取
        items = _extract_grid_items_from_h3(body)
        return {"items": items}

    if slide_type == SlideType.TWO_COLUMN and has_pc:
        # 從 ✅/❌ 或 優點/缺點 抽取
        left, right = _extract_pros_cons_columns(body)
        return {
            "left": {"title": left[0], "items": left[1]},
            "right": {"title": right[0], "items": right[1]},
        }

    if slide_type == SlideType.OBJECTIVES:
        # 從 H3 或 bullet 抽取
        items = _extract_objectives_items(body)
        if not items:
            # 從 H3 抽
            items = _extract_grid_items_from_h3(body)
        return {"items": items}

    if slide_type == SlideType.SECTION_DIVIDER:
        # 從標題抽取 "Part N"
        m = re.match(r"(Part\s+\d+|Chapter\s+\d+|Section\s+\d+)", title, re.IGNORECASE)
        section_num = m.group(1) if m else ""
        return {
            "section_num": section_num,
            "section_subtitle": "",  # 可以後續從 H3 抽
        }

    # TITLE_CONTENT（預設）
    items = extract_bullet_items(body)
    if items:
        return {"items": items}
    return {"text": extract_paragraph_text(body)}


def _extract_grid_items_from_h3(body: str) -> list[dict]:
    """從 H3 子標題抽取 grid_cards 項目"""
    items: list[dict] = []
    pattern = re.compile(
        r"^###\s+(.+?)$(.*?)(?=^###\s|\Z)",
        re.MULTILINE | re.DOTALL
    )
    for m in pattern.finditer(body):
        h3_title = strip_markdown_inline(m.group(1).strip())
        h3_body = m.group(2).strip()
        # 描述 = 第一段
        desc = extract_paragraph_text(h3_body).split("\n")[0] if h3_body else ""
        # 找 icon（標題開頭的 emoji）
        icon_match = re.match(r"^([\U0001F300-\U0001F9FF\u2600-\u27BF])", h3_title)
        icon = icon_match.group(1) if icon_match else ""
        if icon:
            h3_title = h3_title[len(icon):].strip()
        items.append({
            "icon": icon,
            "title": h3_title,
            "desc": desc[:100] if desc else "",
        })
    return items


def _extract_objectives_items(body: str) -> list[dict]:
    """從「學習目標」章節抽取 grid 項目

    模式：通常是 bullet list 帶粗體開頭
    """
    items: list[dict] = []
    for line in body.split("\n"):
        match = re.match(r"^\s*[-*]\s+(?:(\S+)\s+)?\*\*(.+?)\*\*\s*[：:]\s*(.+)$", line)
        if match:
            icon = match.group(1) or ""
            title = match.group(2).strip()
            desc = match.group(3).strip()
            # icon 可能是 emoji
            if not icon and re.match(r"^[\U0001F300-\U0001F9FF\u2600-\u27BF]", title):
                icon_match = re.match(r"^([\U0001F300-\U0001F9FF\u2600-\u27BF])\s*(.+)$", title)
                if icon_match:
                    icon = icon_match.group(1)
                    title = icon_match.group(2)
            items.append({"icon": icon, "title": strip_markdown_inline(title), "desc": strip_markdown_inline(desc)})
    return items


def _extract_pros_cons_columns(body: str) -> tuple[list, list]:
    """從優點/缺點並列結構抽取兩欄

    Returns:
        (left, right) — left = [title, items], right = [title, items]
    """
    left: list = ["優點", []]
    right: list = ["缺點", []]

    lines = body.split("\n")
    current = None  # "left" or "right"

    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            continue

        # 切換欄位
        if any(kw in line_stripped for kw in ["✅", "優點", "Pros", "好處"]):
            current = "left"
            # 可能是標題
            if "✅" in line_stripped or line_stripped.startswith("#"):
                continue
        elif any(kw in line_stripped for kw in ["❌", "缺點", "Cons", "壞處"]):
            current = "right"
            if "❌" in line_stripped or line_stripped.startswith("#"):
                continue

        # bullet item
        match = re.match(r"^\s*[-*]\s+(.+)$", line)
        if match and current:
            target = left if current == "left" else right
            target[1].append(match.group(1).strip())

    return left, right
