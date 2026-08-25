"""
Slide type 自動推斷

根據 Markdown 章節的標題與內容，啟發式推斷 SlideType。
對應 spec §4.4。
"""
from __future__ import annotations

import re
from typing import TYPE_CHECKING

from ..core import SlideType

if TYPE_CHECKING:
    pass


# === 標題關鍵字（高信心度）===

OBJECTIVES_KEYWORDS = [
    "學習目標", "你會學到", "本章目標", "Objectives",
    "Goals", "目標", "What you'll learn", "Learning objectives",
]

SECTION_KEYWORDS = [
    "Part ", "Part 1", "Part 2", "Part 3", "Part 4", "Part 5",
    "章節", "Section", "Chapter",
]

# 純 Markdown 開頭 H1 + 副標的標記（用於推斷 cover）
COVER_INDICATORS = [
    "# ",  # Markdown 開頭就是 H1
]


def infer_slide_type(
    title: str,
    body_text: str = "",
    has_code_block: bool = False,
    has_table: bool = False,
    has_h3_subsections: int = 0,
    has_pros_cons: bool = False,
) -> tuple[SlideType, float]:
    """推斷 slide_type

    Args:
        title: 章節標題（不含 ## 前綴）
        body_text: 章節內文（純文字，已移除 code/table 標記）
        has_code_block: 是否包含 ```code block```
        has_table: 是否包含 Markdown table
        has_h3_subsections: H3 子標題數量
        has_pros_cons: 是否有「✅/❌/優點/缺點」並列結構

    Returns:
        (SlideType, confidence) — confidence 0.0-1.0
    """
    title_clean = title.strip()

    # === 高信心度：明確關鍵字 ===

    # OBJECTIVES
    if _matches_any(title_clean, OBJECTIVES_KEYWORDS):
        return SlideType.OBJECTIVES, 0.95

    # SECTION_DIVIDER
    if _matches_any(title_clean, SECTION_KEYWORDS):
        return SlideType.SECTION_DIVIDER, 0.95

    # === 高信心度：明確結構特徵 ===

    if has_table:
        return SlideType.TITLE_TABLE, 0.90

    if has_code_block:
        return SlideType.TITLE_CODE, 0.90

    # === 中信心度：組合特徵 ===

    if has_pros_cons:
        return SlideType.TWO_COLUMN, 0.70

    if has_h3_subsections >= 3:
        return SlideType.GRID_CARDS, 0.65

    # === 預設：title_content ===
    return SlideType.TITLE_CONTENT, 0.50


# === 輔助函式 ===

def _matches_any(text: str, keywords: list[str]) -> bool:
    """檢查 text 是否包含任何 keywords"""
    text_lower = text.lower()
    for kw in keywords:
        if kw.lower() in text_lower:
            return True
    return False


def _count_code_lines(body_text: str) -> int:
    """計算 code block 的行數

    body_text 已經是純文字（code 區塊可能已被移除）
    這裡是個 fallback 估計
    """
    # 簡單啟發式：計算 ``` 出現次數（每對 ``` 之間算一個 code block）
    return body_text.count("```") // 2


def has_pros_cons_structure(body_text: str) -> bool:
    """檢查是否有「✅/❌/優點/缺點」並列結構"""
    pros_keywords = ["✅", "優點", "Pros", "advantage", "好處"]
    cons_keywords = ["❌", "缺點", "Cons", "disadvantage", "壞處"]

    has_pros = any(kw in body_text for kw in pros_keywords)
    has_cons = any(kw in body_text for kw in cons_keywords)
    return has_pros and has_cons


def count_h3_subsections(body_text: str) -> int:
    """計算 H3 子標題數量"""
    return len(re.findall(r"^###\s+", body_text, re.MULTILINE))


def detect_code_blocks(body_text: str) -> bool:
    """檢測是否有 code block"""
    return "```" in body_text


def detect_markdown_table(body_text: str) -> bool:
    """檢測是否有 Markdown table

    特徵：
    - 包含 | --- | 形式
    - 或第二行有 | :--- |
    """
    lines = body_text.split("\n")
    for i, line in enumerate(lines):
        # 找形如 | --- | 或 |:---| 的行
        if re.match(r"^\s*\|?\s*:?-+:?\s*\|", line):
            # 確認下一行也有 |（表格內容）
            if i + 1 < len(lines) and "|" in lines[i + 1]:
                return True
            if i > 0 and "|" in lines[i - 1]:
                return True
    return False


def extract_code_block(body_text: str) -> str:
    """從 body 中提取第一個 code block 的內容

    Returns:
        code block 內容（不含 ``` 標記），如果沒有則回傳 ""
    """
    match = re.search(r"```(\w*)\n(.*?)```", body_text, re.DOTALL)
    if match:
        return match.group(2).rstrip("\n")
    return ""


def extract_markdown_table(body_text: str) -> tuple[list[str], list[list[str]]]:
    """從 body 中提取第一個 Markdown table

    處理跳過的 \|（如 string\|object）

    Returns:
        (headers, rows) — 沒有則 ([], [])
    """
    lines = body_text.split("\n")
    headers: list[str] = []
    rows: list[list[str]] = []

    def split_row(line: str) -> list[str]:
        """分割一行 table，處理跳過的 \|"""
        placeholder = "\x00PIPE\x00"
        line = line.replace("\\|", placeholder)
        cells = line.split("|")
        cells = [c.strip() for c in cells]
        # 移除首尾的空單元格
        if cells and cells[0] == "":
            cells = cells[1:]
        if cells and cells[-1] == "":
            cells = cells[:-1]
        cells = [c.replace(placeholder, "|") for c in cells]
        return cells

    for i, line in enumerate(lines):
        # 找到標題列（包含 |）
        if "|" in line and i + 1 < len(lines):
            stripped = lines[i + 1].strip()
            # 檢查下一行是否是 separator（|:---| 或 | --- |）
            if re.match(r"^\|?(\s*:?-+:?\s*\|)+\s*:?-+:?\s*\|?$", stripped):
                # 解析標題
                headers = split_row(line)
                # 解析後續的資料列
                for j in range(i + 2, len(lines)):
                    if "|" not in lines[j]:
                        break
                    row = split_row(lines[j])
                    if row:
                        rows.append(row)
                break

    return headers, rows


def extract_bullet_items(body_text: str) -> list[str]:
    """從 body 中提取 bullet items（- 開頭的項目）

    Returns:
        bullet items list
    """
    items: list[str] = []
    for line in body_text.split("\n"):
        # 匹配 "- " 或 "* " 開頭
        match = re.match(r"^\s*[-*]\s+(.+)$", line)
        if match:
            items.append(match.group(1).strip())
    return items


def extract_paragraph_text(body_text: str) -> str:
    """提取純段落文字（移除 code/table/headers/bullets）"""
    lines = []
    in_code = False
    for line in body_text.split("\n"):
        # 追蹤 code block 邊界
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        # 跳過 H1/H2/H3/H4 標題
        if re.match(r"^\s*#{1,6}\s+", line):
            continue
        # 跳過 table（含 | 的行）
        if "|" in line and re.match(r"^\s*\|", line):
            continue
        # 跳過 bullets
        if re.match(r"^\s*[-*]\s+", line):
            continue
        # 跳過 blockquote
        if re.match(r"^\s*>\s*", line):
            continue
        # 跳過空行
        if not line.strip():
            continue
        lines.append(line.strip())

    return "\n".join(lines)
