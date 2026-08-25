"""
Phase 9 視覺驗證 HTML 報告產生器

把 /tmp/old_png/ 和 /tmp/new_png/ 的 PNG 合併成單一 HTML，
方便用瀏覽器逐張比對。

特色：
- 每對檔案（新 00 / 舊 00-overview）有獨立章節
- 每章節內逐張並排顯示 OLD vs NEW
- 用 # 錨點快速跳到特定 slide
- 可選「只看新版」「只看舊版」「並排」三種檢視模式

用法：
    python build_html_report.py
    # 產出 /tmp/phase9_report.html，用瀏覽器開啟
"""
from __future__ import annotations

import sys
from pathlib import Path
from collections import defaultdict
import re


OLD_DIR = Path("/tmp/old_png")
NEW_DIR = Path("/tmp/new_png")
OUT_FILE = Path("/tmp/phase9_report.html")


def collect_pngs(directory: Path) -> dict[str, list[Path]]:
    """收集每個檔案的 PNG（依檔名前綴分組）"""
    groups: dict[str, list[Path]] = defaultdict(list)
    for png in sorted(directory.glob("*.png")):
        # 檔名格式：<base>_pptx_slide-NN.png
        m = re.match(r"^(.+?)_pptx_slide-(\d+)\.png$", png.name)
        if not m:
            continue
        base = m.group(1)
        groups[base].append(png)
    # 依 slide 編號排序
    for base in groups:
        groups[base].sort(
            key=lambda p: int(re.search(r"slide-(\d+)", p.name).group(1))
        )
    return groups


def build_html(old_groups: dict, new_groups: dict) -> str:
    # 配對（用編號對應：00, 01, 02, ...）
    file_pairs = [
        ("00-overview", "new_00-claude-code-plugins-series", "00 系列總覽"),
        ("01-plugin-marketplaces", "new_01-plugin-marketplaces", "01 Plugin Marketplaces"),
        ("02-plugins", "new_02-plugins", "02 Plugins"),
        ("03-plugins-reference", "new_03-plugins-reference", "03 Plugin 技術參考"),
        ("04-skills", "new_04-skills", "04 Skills"),
        ("05-subagents", "new_05-subagents", "05 Subagents"),
        ("06-hooks", "new_06-hooks", "06 Hooks"),
        ("07-discover-plugins", "new_07-discover-plugins", "07 探索並安裝 Plugins"),
    ]

    html = ['<!DOCTYPE html>', '<html lang="zh-TW">', '<head>',
            '<meta charset="UTF-8">',
            '<title>Phase 9 視覺驗證報告</title>',
            '<style>',
            'body { font-family: -apple-system, "Segoe UI", "Microsoft JhengHei", sans-serif;',
            '       margin: 0; padding: 20px; background: #f5f5f5; }',
            'h1 { color: #2C2C2C; border-bottom: 3px solid #C75A1A; padding-bottom: 10px; }',
            'h2 { color: #C75A1A; margin-top: 40px; }',
            '.toc { background: white; padding: 15px 20px; border-radius: 8px;',
            '        box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 30px; }',
            '.toc a { display: inline-block; margin: 4px 12px 4px 0; color: #C75A1A;',
            '          text-decoration: none; font-weight: 500; }',
            '.toc a:hover { text-decoration: underline; }',
            '.slide-pair { background: white; margin: 20px 0; padding: 20px;',
            '               border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }',
            '.slide-pair h3 { margin-top: 0; color: #2C2C2C; }',
            '.slide-pair .meta { font-size: 13px; color: #666; margin: 5px 0 15px; }',
            '.slide-pair .meta .delta-bad { color: #d32f2f; font-weight: bold; }',
            '.slide-pair .meta .delta-warn { color: #f57c00; font-weight: bold; }',
            '.slide-pair .meta .delta-good { color: #388e3c; }',
            '.comparison { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }',
            '.comparison.single { grid-template-columns: 1fr; }',
            '.slide-img { text-align: center; }',
            '.slide-img img { max-width: 100%; border: 1px solid #ddd;',
            '                  box-shadow: 0 1px 3px rgba(0,0,0,0.1); }',
            '.slide-img .label { display: block; margin-bottom: 8px; font-weight: bold;',
            '                     color: #555; font-size: 14px; }',
            '.missing { color: #999; font-style: italic; padding: 40px;',
            '           background: #fafafa; border-radius: 4px; }',
            '.controls { position: fixed; top: 20px; right: 20px;',
            '             background: white; padding: 12px 16px; border-radius: 8px;',
            '             box-shadow: 0 2px 8px rgba(0,0,0,0.15); z-index: 1000; }',
            '.controls button { margin: 0 4px; padding: 6px 12px; border: 1px solid #C75A1A;',
            '                   background: white; color: #C75A1A; border-radius: 4px;',
            '                   cursor: pointer; font-size: 13px; }',
            '.controls button.active { background: #C75A1A; color: white; }',
            '.controls button:hover { background: #fce4d2; }',
            '</style>',
            '</head>', '<body>']

    html.append('<div class="controls">')
    html.append('<button onclick="setMode(\'side\')" id="btn-side" class="active">並排</button>')
    html.append('<button onclick="setMode(\'new\')" id="btn-new">只看新版</button>')
    html.append('<button onclick="setMode(\'old\')" id="btn-old">只看舊版</button>')
    html.append('</div>')

    html.append('<h1>Phase 9 視覺驗證報告</h1>')
    html.append('<p>比對 <code>/home/elan/pi-proj/*.pptx</code>（舊）vs '
                '<code>/tmp/new_*.pptx</code>（新 learn2deck 產出）。</p>')

    # TOC
    html.append('<div class="toc"><strong>目錄：</strong>')
    for old_base, new_base, label in file_pairs:
        anchor = f"file-{old_base}"
        html.append(f'<a href="#{anchor}">{label}</a>')
    html.append('</div>')

    # 每對檔案的章節
    for old_base, new_base, label in file_pairs:
        old_pngs = old_groups.get(old_base, [])
        new_pngs = new_groups.get(new_base, [])

        anchor = f"file-{old_base}"
        html.append(f'<h2 id="{anchor}">{label}</h2>')
        html.append(f'<p class="meta">')
        html.append(f'<strong>OLD slides:</strong> {len(old_pngs)}  |  ')
        html.append(f'<strong>NEW slides:</strong> {len(new_pngs)}  |  ')
        delta = len(new_pngs) - len(old_pngs)
        if delta < 0:
            html.append(f'<span class="delta-warn">Δ: {delta:+d}</span>')
        elif delta > 0:
            html.append(f'<span class="delta-bad">Δ: {delta:+d}（比舊版多）</span>')
        else:
            html.append(f'<span class="delta-good">Δ: 0</span>')
        html.append('</p>')

        max_n = max(len(old_pngs), len(new_pngs))

        for i in range(max_n):
            html.append('<div class="slide-pair">')
            html.append(f'<h3>Slide {i+1:02d}</h3>')

            html.append('<div class="comparison side">')

            # OLD
            html.append('<div class="slide-img">')
            html.append('<span class="label">OLD</span>')
            if i < len(old_pngs):
                png_name = old_pngs[i].name
                html.append(f'<img src="{OLD_DIR.name}/{png_name}" '
                            f'alt="OLD slide {i+1}">')
            else:
                html.append('<div class="missing">（無對應 OLD slide）</div>')
            html.append('</div>')

            # NEW
            html.append('<div class="slide-img">')
            html.append('<span class="label">NEW (learn2deck)</span>')
            if i < len(new_pngs):
                png_name = new_pngs[i].name
                html.append(f'<img src="{NEW_DIR.name}/{png_name}" '
                            f'alt="NEW slide {i+1}">')
            else:
                html.append('<div class="missing">（無對應 NEW slide）</div>')
            html.append('</div>')

            html.append('</div>')  # close comparison
            html.append('</div>')  # close slide-pair

    html.append('<script>')
    html.append('function setMode(mode) {')
    html.append('  document.querySelectorAll(".comparison").forEach(el => {')
    html.append('    el.classList.remove("side", "new", "old");')
    html.append('    el.classList.add(mode);')
    html.append('    if (mode === "side") {')
    html.append('      el.style.gridTemplateColumns = "1fr 1fr";')
    html.append('      el.querySelectorAll(".slide-img").forEach((d, i) => {')
    html.append('        d.style.display = (i === 0 && mode === "old") ? "none" : "block";')
    html.append('      });')
    html.append('    } else if (mode === "new") {')
    html.append('      el.style.gridTemplateColumns = "1fr";')
    html.append('      el.querySelectorAll(".slide-img").forEach((d, i) => {')
    html.append('        d.style.display = (i === 1) ? "block" : "none";')
    html.append('      });')
    html.append('    } else {')
    html.append('      el.style.gridTemplateColumns = "1fr";')
    html.append('      el.querySelectorAll(".slide-img").forEach((d, i) => {')
    html.append('        d.style.display = (i === 0) ? "block" : "none";')
    html.append('      });')
    html.append('    }')
    html.append('  });')
    html.append('  document.querySelectorAll(".controls button").forEach(b => b.classList.remove("active"));')
    html.append('  document.getElementById("btn-" + mode).classList.add("active");')
    html.append('}')
    html.append('</script>')

    html.append('</body></html>')
    return "\n".join(html)


def main() -> int:
    if not OLD_DIR.exists():
        print(f"❌ 找不到 {OLD_DIR}")
        print(f"   請先執行 ./convert_pptx_to_png.sh 產生 PNG")
        return 2
    if not NEW_DIR.exists():
        print(f"❌ 找不到 {NEW_DIR}")
        return 2

    old_groups = collect_pngs(OLD_DIR)
    new_groups = collect_pngs(NEW_DIR)

    print(f"OLD groups: {len(old_groups)}")
    for base, pngs in old_groups.items():
        print(f"  {base}: {len(pngs)} PNGs")
    print(f"NEW groups: {len(new_groups)}")
    for base, pngs in new_groups.items():
        print(f"  {new_groups and base}: {len(pngs)} PNGs")

    html = build_html(old_groups, new_groups)
    OUT_FILE.write_text(html, encoding="utf-8")
    print(f"\n✓ 報告產出：{OUT_FILE}")
    print(f"  在瀏覽器開啟：xdg-open {OUT_FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
