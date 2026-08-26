r"""
Phase 9 視覺驗證 HTML 報告產生器（Windows 友善版）

把 PNG + HTML 報告複製到 /mnt/c/Users/Elan/Desktop/phase9_report/
這樣從 Windows 瀏覽器直接開啟就能讀到圖。

用法：
    python3 build_report_windows.py
    # 產出：C:\Users\Elan\Desktop\phase9_report\phase9_report.html
    # Windows 開啟：雙擊該 HTML 即可
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path
from collections import defaultdict
import re


OLD_SRC = Path("/tmp/old_png")
NEW_SRC = Path("/tmp/new_png")
WIN_OUT = Path("/mnt/c/Users/Elan/Desktop/phase9_report")
HTML_FILE = WIN_OUT / "phase9_report.html"


def collect_pngs(directory: Path) -> dict[str, list[Path]]:
    """收集每個檔案的 PNG"""
    groups: dict[str, list[Path]] = defaultdict(list)
    for png in sorted(directory.glob("*.png")):
        m = re.match(r"^(.+?)_pptx_slide-(\d+)\.png$", png.name)
        if not m:
            continue
        base = m.group(1)
        groups[base].append(png)
    for base in groups:
        groups[base].sort(
            key=lambda p: int(re.search(r"slide-(\d+)", p.name).group(1))
        )
    return groups


def build_html(old_groups: dict, new_groups: dict) -> str:
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
    html.append('<p>比對 <code>C:\\Users\\Elan\\Desktop\\phase9_report\\old_png\\</code>'
                '（舊）vs <code>...\\new_png\\</code>（新 learn2deck 產出）。</p>')

    html.append('<div class="toc"><strong>目錄：</strong>')
    for old_base, new_base, label in file_pairs:
        anchor = f"file-{old_base}"
        html.append(f'<a href="#{anchor}">{label}</a>')
    html.append('</div>')

    for old_base, new_base, label in file_pairs:
        old_pngs = old_groups.get(old_base, [])
        new_pngs = new_groups.get(new_base, [])

        anchor = f"file-{old_base}"
        html.append(f'<h2 id="{anchor}">{label}</h2>')
        html.append('<p class="meta">')
        html.append(f'<strong>OLD slides:</strong> {len(old_pngs)}  |  ')
        html.append(f'<strong>NEW slides:</strong> {len(new_pngs)}  |  ')
        delta = len(new_pngs) - len(old_pngs)
        if delta < 0:
            html.append(f'<span class="delta-warn">Δ: {delta:+d}</span>')
        elif delta > 0:
            html.append(f'<span class="delta-bad">Δ: {delta:+d}（比舊版多）</span>')
        else:
            html.append('<span class="delta-good">Δ: 0</span>')
        html.append('</p>')

        max_n = max(len(old_pngs), len(new_pngs))

        for i in range(max_n):
            html.append('<div class="slide-pair">')
            html.append(f'<h3>Slide {i+1:02d}</h3>')

            html.append('<div class="comparison">')

            # OLD — 用相對路徑（HTML 跟 PNG 在同一個 phase9_report/ 目錄）
            html.append('<div class="slide-img">')
            html.append('<span class="label">OLD</span>')
            if i < len(old_pngs):
                html.append(f'<img src="old_png/{old_pngs[i].name}" '
                            f'alt="OLD slide {i+1}">')
            else:
                html.append('<div class="missing">（無對應 OLD slide）</div>')
            html.append('</div>')

            # NEW
            html.append('<div class="slide-img">')
            html.append('<span class="label">NEW (learn2deck)</span>')
            if i < len(new_pngs):
                # Windows 連結資料夾檔名是「中文 螢幕擷取畫面」不友好，
                # 因此用 ASCII 檔名 new_07-discover-plugins_pptx_slide-NN.png
                html.append(f'<img src="new_png/{new_pngs[i].name}" '
                            f'alt="NEW slide {i+1}">')
            else:
                html.append('<div class="missing">（無對應 NEW slide）</div>')
            html.append('</div>')

            html.append('</div></div>')

    # 切換模式的 JavaScript
    html.append('<script>')
    html.append('function setMode(mode) {')
    html.append('  document.querySelectorAll(".comparison").forEach(el => {')
    html.append('    el.style.gridTemplateColumns = "1fr 1fr";')
    html.append('    if (mode === "new") {')
    html.append('      el.querySelectorAll(".slide-img").forEach((d, i) => {')
    html.append('        d.style.display = (i === 1) ? "block" : "none";')
    html.append('      });')
    html.append('      el.style.gridTemplateColumns = "1fr";')
    html.append('    } else if (mode === "old") {')
    html.append('      el.querySelectorAll(".slide-img").forEach((d, i) => {')
    html.append('        d.style.display = (i === 0) ? "block" : "none";')
    html.append('      });')
    html.append('      el.style.gridTemplateColumns = "1fr";')
    html.append('    } else {')
    html.append('      el.querySelectorAll(".slide-img").forEach(d => {')
    html.append('        d.style.display = "block";')
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
    if not OLD_SRC.exists() or not NEW_SRC.exists():
        print(f"❌ 找不到 PNG 目錄")
        print(f"   請先執行 ./convert_pptx_to_png.sh")
        return 2

    # 建立 Windows 目錄
    WIN_OUT.mkdir(parents=True, exist_ok=True)
    win_old = WIN_OUT / "old_png"
    win_new = WIN_OUT / "new_png"
    win_old.mkdir(exist_ok=True)
    win_new.mkdir(exist_ok=True)

    # 複製 PNG（用 rsync 或 cp）
    print(f"→ 複製 PNG 到 {WIN_OUT}/...")
    shutil.copytree(OLD_SRC, win_old, dirs_exist_ok=True)
    shutil.copytree(NEW_SRC, win_new, dirs_exist_ok=True)

    old_n = len(list(win_old.glob("*.png")))
    new_n = len(list(win_new.glob("*.png")))
    print(f"  ✓ old_png: {old_n} 張")
    print(f"  ✓ new_png: {new_n} 張")

    # 收集分組
    old_groups = collect_pngs(win_old)
    new_groups = collect_pngs(win_new)

    # 寫 HTML
    html = build_html(old_groups, new_groups)
    HTML_FILE.write_text(html, encoding="utf-8")
    print(f"\n✓ 報告產出：{HTML_FILE}")
    print()
    print("開啟方式（從 Windows）：")
    print(f'  雙擊檔案：{HTML_FILE}')
    print()
    print("開啟方式（從 WSL）：")
    print(f"  explorer.exe {HTML_FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
