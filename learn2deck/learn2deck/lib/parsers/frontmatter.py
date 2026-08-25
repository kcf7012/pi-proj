"""
Frontmatter 解析

支援兩種 frontmatter 格式：
1. 標準 YAML frontmatter（`---\\nkey: value\\n---\\n`）
2. 沒有 frontmatter（純內容）
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import yaml

from ..core import FrontmatterError


@dataclass
class FrontmatterResult:
    """Frontmatter 解析結果

    Attributes:
        metadata: frontmatter 內容（dict），沒有則為空 dict
        body: 移除 frontmatter 後的內文（str）
        has_frontmatter: 是否有 frontmatter
    """

    metadata: dict[str, Any]
    body: str
    has_frontmatter: bool


def parse_frontmatter(content: str) -> FrontmatterResult:
    """解析 Markdown 內容的 YAML frontmatter

    Args:
        content: 完整 Markdown 內容

    Returns:
        FrontmatterResult

    Raises:
        FrontmatterError: frontmatter 格式錯誤
    """
    if not content.startswith("---"):
        return FrontmatterResult(metadata={}, body=content, has_frontmatter=False)

    # 找第二個 ---
    lines = content.split("\n")
    if len(lines) < 2 or lines[0].strip() != "---":
        return FrontmatterResult(metadata={}, body=content, has_frontmatter=False)

    # 找結尾的 ---
    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break

    if end_idx is None:
        raise FrontmatterError(
            "frontmatter 開頭 '---' 但找不到結尾 '---'"
        )

    # 解析 YAML
    yaml_content = "\n".join(lines[1:end_idx])
    try:
        metadata = yaml.safe_load(yaml_content) or {}
    except yaml.YAMLError as e:
        raise FrontmatterError(f"frontmatter YAML 解析失敗：{e}") from e

    if not isinstance(metadata, dict):
        raise FrontmatterError(
            f"frontmatter 必須是 dict，收到 {type(metadata).__name__}"
        )

    # 內文（移除 frontmatter）
    body = "\n".join(lines[end_idx + 1 :])
    # 移除開頭的空白行
    body = body.lstrip("\n")

    return FrontmatterResult(
        metadata=metadata,
        body=body,
        has_frontmatter=True,
    )
