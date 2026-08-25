"""
列出 DeckSpec 的所有 slides，方便看解析結果。
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, "/home/elan/pi-proj/learn2deck")

from learn2deck.lib.parsers.markdown import parse_markdown


def inspect_deck(md_path: Path) -> None:
    deck = parse_markdown(md_path)
    print(f"# {md_path.name}")
    print(f"# title: {deck.title}")
    print(f"# subtitle: {deck.subtitle}")
    print(f"# theme: {deck.theme}")
    print(f"# slides: {len(deck.slides)}")
    print()

    type_count: dict[str, int] = {}
    for i, s in enumerate(deck.slides, 1):
        type_count[s.type.value] = type_count.get(s.type.value, 0) + 1

    print(f"# type distribution: {type_count}")
    print()
    for i, s in enumerate(deck.slides, 1):
        body_summary = ""
        if s.body:
            if "items" in s.body:
                body_summary = f"items={len(s.body['items'])}"
            elif "rows" in s.body:
                body_summary = f"headers={len(s.body.get('headers', []))} rows={len(s.body['rows'])}"
            elif "code" in s.body:
                body_summary = f"code_lines={s.body['code'].count(chr(10))+1}"
            elif "text" in s.body:
                body_summary = f"text_len={len(s.body['text'])}"
        print(f"  {i:02d} [{s.type.value:18s}] {s.title[:50]!r}  subtitle={(s.subtitle or '')[:40]!r}  body={body_summary}")


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: inspect_deck.py <path/to/file.md>")
        return 2
    p = Path(sys.argv[1])
    if not p.exists():
        print(f"Not found: {p}")
        return 2
    inspect_deck(p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
