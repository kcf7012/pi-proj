"""
測試 SKILL.md 的觸發語設計

驗證項目：
1. 「應該觸發」案例：使用者的明確轉檔意圖能被 SKILL.md 描述捕獲
2. 「不應該觸發」案例：避免誤觸發（編輯既有 PPTX、一般簡報建議等）

這個測試檢查 SKILL.md frontmatter 的 description 是否包含足夠的
明確關鍵字與句型範例，避免 Claude 誤判觸發條件。
"""
from __future__ import annotations

import re
from pathlib import Path

# SKILL.md 位置
SKILL_PATH = Path(__file__).parent.parent / "SKILL.md"


def _extract_description() -> str:
    """從 SKILL.md 抽出 description"""
    content = SKILL_PATH.read_text(encoding="utf-8")
    fm_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    assert fm_match, "SKILL.md 缺少 frontmatter (--- 區塊)"

    fm = fm_match.group(1)
    desc_match = re.search(r"description:\s*(.+?)(?=\n[a-z_-]+:|$)", fm, re.DOTALL)
    assert desc_match, "SKILL.md 缺少 description"

    return desc_match.group(1).strip()


def _extract_patterns(description: str) -> list[str]:
    """抽出 description 中所有可作為觸發模式的字串

    包含：
    - 引號內的明確短語（長度 ≥ 3）
    - e.g. 範例中的句型
    """
    # 純關鍵字（引號內）
    quoted = re.findall(r'"([^"]+)"', description)
    specific = [p for p in quoted if len(p) >= 3]

    # 句型範例（e.g. 內）
    patterns = []
    examples_match = re.search(r'\(e\.g\.\s*(.+?)\)', description)
    if examples_match:
        examples_text = examples_match.group(1)
        patterns = [p.strip().strip('"').strip("'") for p in examples_text.split(",")]

    # 合併去重
    all_patterns = specific + patterns
    return list(dict.fromkeys(all_patterns))


def _matches(text: str, patterns: list[str]) -> tuple[bool, str]:
    """檢查文字是否符合任一觸發模式"""
    text_lower = text.lower()
    for kw in patterns:
        if kw.lower() in text_lower:
            return True, f"matched: '{kw}'"
    return False, "no match"


# === 測試案例 ===

# 應該觸發：明確的轉檔意圖
SHOULD_TRIGGER = [
    # 中文明確指令
    "幫我把 04-skills.md 做成簡報",
    "我要 8 份文件的簡報",
    "把這個 .md 轉成投影片",
    "幫我做一份 Plugin 簡報",
    "用 markdown 做簡報",
    "產生 Plugin 的 deck",
    "markdown 轉投影片",
    # 英文明確指令
    "make slides from this md",
    "build a deck for 00-overview",
    # 混合
    "從 markdown 產生 pptx",
    "從 md 產生 pptx",
]

# 不應該觸發：避免誤觸發
SHOULD_NOT_TRIGGER = [
    # 編輯既有 PPTX
    "把這個 .pptx 改成橫式",
    "幫我看一下這個 pptx",
    # 一般評論
    "這份 markdown 寫得很好",
    "markdown 的語法有哪些？",
    # 一般簡報建議
    "如何設計好看的簡報？",
    "幫我寫一個簡報大綱",
    # PowerPoint 一般問題
    "PowerPoint 有什麼快捷鍵？",
    # 與本 skill 無關
    "什麼是 Claude Code？",
]


# === pytest 測試函式 ===

def test_skill_md_exists():
    """SKILL.md 必須存在"""
    assert SKILL_PATH.exists(), f"SKILL.md 不存在於 {SKILL_PATH}"


def test_skill_md_has_frontmatter():
    """SKILL.md 必須有 YAML frontmatter"""
    content = SKILL_PATH.read_text(encoding="utf-8")
    assert content.startswith("---\n"), "SKILL.md 必須以 --- 開頭（YAML frontmatter）"
    assert "\n---\n" in content, "SKILL.md 必須有結尾 ---"


def test_skill_md_has_name_field():
    """frontmatter 必須有 name 欄位"""
    description = _extract_description()
    content = SKILL_PATH.read_text(encoding="utf-8")
    fm_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    fm = fm_match.group(1)
    assert re.search(r"^name:\s*\w+", fm, re.MULTILINE), "frontmatter 缺少 name 欄位"


def test_skill_md_description_long_enough():
    """description 至少 100 字（Claude 需要足夠的語意線索）"""
    description = _extract_description()
    assert len(description) >= 100, (
        f"description 太短 ({len(description)} 字)，建議 ≥ 100 字以提供足夠觸發線索"
    )


def test_skill_md_has_triggers():
    """description 必須包含至少 5 個明確關鍵字"""
    description = _extract_description()
    patterns = _extract_patterns(description)
    assert len(patterns) >= 5, (
        f"觸發模式太少 ({len(patterns)} 個)，建議至少 5 個明確短語+句型"
    )


def test_skill_md_has_exclusion_clause():
    """description 必須包含「Do NOT use」或類似的排除條款"""
    description = _extract_description()
    assert "Do NOT" in description or "do not" in description.lower(), (
        "description 應包含明確的「不要觸發」條件（如 Do NOT use for）"
    )


def test_should_trigger_cases():
    """所有「應該觸發」案例都應被 SKILL.md 描述捕獲"""
    description = _extract_description()
    patterns = _extract_patterns(description)

    failures = []
    for text in SHOULD_TRIGGER:
        matched, reason = _matches(text, patterns)
        if not matched:
            failures.append(f"  ❌ {text!r} → {reason}")

    if failures:
        msg = (
            f"以下「應該觸發」案例未匹配到任何 SKILL.md 模式：\n"
            + "\n".join(failures)
            + "\n\n建議在 SKILL.md description 中加入對應關鍵字或句型範例。"
        )
        raise AssertionError(msg)


def test_should_not_trigger_cases():
    """所有「不應該觸發」案例都不應被 SKILL.md 描述捕獲"""
    description = _extract_description()
    patterns = _extract_patterns(description)

    failures = []
    for text in SHOULD_NOT_TRIGGER:
        matched, reason = _matches(text, patterns)
        if matched:
            failures.append(f"  ❌ {text!r} → {reason}")

    if failures:
        msg = (
            f"以下「不應該觸發」案例意外匹配到 SKILL.md 模式（會誤觸發）：\n"
            + "\n".join(failures)
            + "\n\n建議從 description 移除過於通用的詞（如單獨 'pptx'、'簡報'）。"
        )
        raise AssertionError(msg)


def test_skill_md_mentions_no_llm():
    """SKILL.md 應明確說明不呼叫 LLM（v1.0 純規則版）"""
    content = SKILL_PATH.read_text(encoding="utf-8")
    # 檢查 SKILL.md 本文（非 frontmatter）有提到「不呼叫 LLM」之類的說明
    body = content.split("---", 2)[2] if content.count("---") >= 2 else content
    assert "不呼叫" in body or "純規則" in body or "v1.0" in body, (
        "SKILL.md 本文應說明本 skill 不呼叫 LLM（v1.0 純規則版特性）"
    )


def test_skill_md_references_section():
    """SKILL.md 應引用 references/ 內的設計文件"""
    content = SKILL_PATH.read_text(encoding="utf-8")
    assert "references/" in content, "SKILL.md 應引用 references/ 內的設計文件"
