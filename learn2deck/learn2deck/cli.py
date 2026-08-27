"""
learn2deck CLI 入口

使用 typer + rich，提供：
- build: 從 .md 產生 PPTX
- validate: 驗證已產出的 PPTX
- theme: 管理主題
- init: 初始化新專案範本
- version: 顯示版本
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from . import __version__
from .lib.core import DeckSpec, SlideType
from .lib.parsers import parse_content
from .lib.builders import build_full_deck
from .lib.validators import validate_deck, print_report, BUILTIN_VALIDATORS

app = typer.Typer(
    name="learn2deck",
    help="從 Markdown 教材與技術文件產生符合設計風格的 PPTX 簡報",
    no_args_is_help=True,
    rich_markup_mode="rich",
    add_completion=False,
)
console = Console()
error_console = Console(stderr=True, style="red")


# === Helper ===

def _resolve_theme(theme_name: str):
    """載入主題，找不到時印錯誤並離開"""
    from .lib.core import load_theme, ThemeNotFoundError
    try:
        return load_theme(theme_name)
    except ThemeNotFoundError as e:
        error_console.print(f"[red]❌ {e}[/red]")
        raise typer.Exit(1)


# === version ===

@app.command()
def version():
    """顯示版本資訊"""
    console.print(f"[bold green]learn2deck[/bold green] v{__version__}")


# === build ===

@app.command()
def build(
    input: Path = typer.Argument(
        ...,
        help="輸入的 .md 或 .yaml 檔案路徑",
        exists=False,
    ),
    output: Path = typer.Option(
        ...,
        "-o", "--output",
        help="輸出的 .pptx 檔案路徑",
    ),
    theme: str = typer.Option(
        "claude-orange",
        "--theme", "-t",
        help="主題名稱（預設 claude-orange）",
    ),
    validate_: bool = typer.Option(
        False,
        "--validate",
        help="產出後自動跑驗證",
    ),
    strict: bool = typer.Option(
        False,
        "--strict",
        help="嚴格模式（警告也視為錯誤）",
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet", "-q",
        help="安靜模式（不輸出進度）",
    ),
):
    """從 Markdown / YAML 產生 PPTX 簡報

    範例：

        learn2deck build input.md -o output.pptx

        learn2deck build input.md -o output.pptx --theme minimal-bw

        learn2deck build input.md -o output.pptx --validate
    """
    if not input.exists():
        error_console.print(f"[red]❌ 檔案不存在：{input}[/red]")
        raise typer.Exit(1)

    # 1. 解析
    if not quiet:
        console.print(f"[dim]📄 解析 {input}...[/dim]")
    try:
        deck = parse_content(str(input))
    except Exception as e:
        error_console.print(f"[red]❌ 解析失敗：{e}[/red]")
        raise typer.Exit(1)

    # 套用 CLI 指定的 theme（覆寫檔案中的設定）
    if theme:
        deck.theme = theme

    if not quiet:
        console.print(
            f"[green]✓[/green] 解析成功：{deck.total_slides} 張投影片"
        )
        console.print(f"[dim]   主題：{deck.theme}[/dim]")
        type_count = deck.slide_types_count
        types_str = ", ".join(f"{k}:{v}" for k, v in type_count.items())
        console.print(f"[dim]   版型：{types_str}[/dim]")

    # 2. 載入主題
    theme_obj = _resolve_theme(deck.theme)

    # 3. 產出
    if not quiet:
        console.print(f"[dim]🎨 產生 {output}...[/dim]")
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        build_full_deck(deck, str(output))
    except Exception as e:
        error_console.print(f"[red]❌ 產出失敗：{e}[/red]")
        raise typer.Exit(1)

    if not quiet:
        import os
        size = os.path.getsize(output)
        console.print(
            f"[bold green]✅ 簡報產生完成：{output} ({size:,} bytes, {deck.total_slides} slides)[/bold green]"
        )

    # 4. 驗證（如果要求）
    if validate_:
        if not quiet:
            console.print(f"[dim]🔍 驗證中...[/dim]")
        report = validate_deck(str(output), strict=strict)
        if not quiet:
            print_report(report)
        if not report.passed:
            raise typer.Exit(1)


# === validate ===

@app.command()
def validate(
    pptx: Path = typer.Argument(
        ...,
        help="要驗證的 .pptx 檔案路徑",
        exists=False,
    ),
    rules: Optional[str] = typer.Option(
        None,
        "--rules", "-r",
        help="指定規則（逗號分隔，如 R1,R2,R5）。預設全部",
    ),
    strict: bool = typer.Option(
        False,
        "--strict",
        help="嚴格模式（警告也視為錯誤）",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="以 JSON 格式輸出（CI/CD 用）",
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet", "-q",
        help="安靜模式（只輸出最終結果）",
    ),
):
    """驗證已產出的 PPTX 簡報

    範例：

        learn2deck validate output.pptx

        learn2deck validate output.pptx --strict

        learn2deck validate output.pptx --json > report.json

        learn2deck validate output.pptx --rules R1,R5
    """
    if not pptx.exists():
        error_console.print(f"[red]❌ 檔案不存在：{pptx}[/red]")
        raise typer.Exit(1)

    rule_list = None
    if rules:
        rule_list = [r.strip().upper() for r in rules.split(",")]
        # 驗證規則名稱
        invalid = [r for r in rule_list if r not in BUILTIN_VALIDATORS]
        if invalid:
            error_console.print(
                f"[red]❌ 未知規則：{', '.join(invalid)}。可用：{', '.join(BUILTIN_VALIDATORS.keys())}[/red]"
            )
            raise typer.Exit(1)

    report = validate_deck(str(pptx), rules=rule_list, strict=strict)

    if json_output:
        # JSON 格式
        print(json.dumps(report.to_dict(), indent=2, ensure_ascii=False))
    elif not quiet:
        print_report(report)

    if not report.passed:
        raise typer.Exit(1)


# === theme ===

theme_app = typer.Typer(help="管理主題", no_args_is_help=True)
app.add_typer(theme_app, name="theme")


@theme_app.command("list")
def theme_list():
    """列出所有可用主題"""
    from .lib.themes import list_builtin_themes

    themes = list_builtin_themes()
    if not themes:
        console.print("[yellow]⚠ 沒有可用的內建主題[/yellow]")
        return

    table = Table(title="🎨 可用主題", show_header=True, header_style="bold")
    table.add_column("名稱", style="cyan")
    table.add_column("說明")

    for name in themes:
        try:
            theme = _resolve_theme(name)
            desc = theme.description or "(無說明)"
        except typer.Exit:
            desc = "(載入失敗)"
        table.add_row(name, desc)

    console.print(table)


@theme_app.command("show")
def theme_show(
    name: str = typer.Argument(..., help="主題名稱"),
):
    """顯示主題的詳細資訊"""
    theme = _resolve_theme(name)

    console.print(f"\n[bold cyan]🎨 {theme.name}[/bold cyan]")
    console.print(f"   說明：{theme.description}")

    # 顏色
    console.print(f"\n   [bold]顏色 ({len(theme.colors)})：[/bold]")
    for c, h in theme.colors.items():
        console.print(f"     • {c}: [#{h.lstrip('#')}]{h}[/#{h.lstrip('#')}]")

    # 字體
    console.print(f"\n   [bold]字體：[/bold]")
    for f, v in theme.fonts.items():
        console.print(f"     • {f}: {v}")

    # 字級
    console.print(f"\n   [bold]字級：[/bold]")
    for s, v in theme.font_sizes.items():
        console.print(f"     • {s}: {v}pt")

    # 版面
    console.print(f"\n   [bold]版面：[/bold]")
    for k, v in theme.layout.items():
        console.print(f"     • {k}: {v}\"")


@theme_app.command("new")
def theme_new(
    name: str = typer.Argument(..., help="新主題名稱"),
    base: str = typer.Option(
        "claude-orange",
        "--base", "-b",
        help="基於哪個主題建立",
    ),
    output: Path = typer.Option(
        None,
        "-o", "--output",
        help="輸出 YAML 路徑（預設為 themes/<name>.yaml）",
    ),
):
    """從現有主題複製建立新主題"""
    import yaml

    base_theme = _resolve_theme(base)

    if output is None:
        from .lib.themes import get_builtin_theme_path
        # 預設輸出到 themes/ 目錄
        themes_dir = get_builtin_theme_path(base).parent
        output = themes_dir / f"{name}.yaml"

    new_data = {
        "name": name,
        "description": f"基於 {base} 的自訂主題",
        "colors": base_theme.colors,
        "fonts": base_theme.fonts,
        "font_sizes": base_theme.font_sizes,
        "layout": base_theme.layout,
        "decorations": base_theme.decorations,
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", encoding="utf-8") as f:
        yaml.dump(new_data, f, allow_unicode=True, sort_keys=False)

    console.print(f"[green]✓ 新主題已建立：{output}[/green]")
    console.print(f"   編輯後用 [cyan]learn2deck theme validate {output}[/cyan] 檢查")


@theme_app.command("validate")
def theme_validate(
    path: Path = typer.Argument(..., help="主題 YAML 檔案路徑", exists=False),
):
    """驗證自訂主題檔案"""
    if not path.exists():
        error_console.print(f"[red]❌ 檔案不存在：{path}[/red]")
        raise typer.Exit(1)

    from .lib.core import load_theme, ThemeValidationError
    try:
        theme = load_theme(str(path))
        # 主動觸發所有顏色驗證（不只在 get_color() 時才檢查）
        for color_name in theme.colors:
            try:
                theme.get_color(color_name)
            except ThemeValidationError as e:
                raise ThemeValidationError(
                    f"顏色 '{color_name}' 無效：{e}"
                ) from e
        console.print(f"[green]✓ 主題有效：{theme.name}[/green]")
        console.print(f"   顏色：{len(theme.colors)} 個")
        console.print(f"   字體：{len(theme.fonts)} 個")
        console.print(f"   字級：{len(theme.font_sizes)} 個")
        console.print(f"   版面：{len(theme.layout)} 個")
    except ThemeValidationError as e:
        error_console.print(f"[red]❌ 主題無效：{e}[/red]")
        raise typer.Exit(1)


# === init ===

@app.command()
def init(
    directory: Path = typer.Argument(
        Path("my-deck"),
        help="要初始化的目錄",
    ),
):
    """初始化新 deck 專案（建立範本檔案）

    範例：

        learn2deck init my-deck/
    """
    directory.mkdir(parents=True, exist_ok=True)

    # outline.yaml
    outline_path = directory / "outline.yaml"
    outline_content = """# learn2deck outline example
# 編輯這個檔案後執行：learn2deck build outline.yaml -o output.pptx

deck:
  title: 我的簡報
  subtitle: 副標題
  theme: claude-orange

slides:
  - type: cover
    title: 我的簡報
    subtitle: 副標題
    body:
      tag: "# Demo"

  - type: objectives
    title: 本章你會學到
    body:
      items:
        - icon: "🎯"
          title: 概念 1
          desc: 簡短說明
        - icon: "📦"
          title: 工具 2
          desc: 簡短說明
        - icon: "🧪"
          title: 測試 3
          desc: 簡短說明

  - type: section
    title: 章節標題
    body:
      section_num: "Part 1"
      section_subtitle: 章節副標題

  - type: title_content
    title: 標題
    subtitle: 副標題
    body:
      items:
        - 第一點
        - 第二點
        - 第三點

  - type: title_table
    title: 比較表
    body:
      headers: [欄位 A, 欄位 B]
      rows:
        - [值 1, 值 2]
        - [值 3, 值 4]

  - type: title_code
    title: 程式碼範例
    body:
      language: python
      code: |
        def hello():
            print("Hello, world!")

  - type: summary
    title: 重點回顧
    body:
      key_points:
        - 重點 1
        - 重點 2
      next_steps:
        - 下一步
"""
    outline_path.write_text(outline_content, encoding="utf-8")

    # content.md
    content_path = directory / "content.md"
    content_path.write_text(
        """# 我的簡報標題

副標題或簡介

## 第一章

內容寫在這裡。

- 重點 A
- 重點 B

## 第二章

更多內容。

```python
print("Hello, world!")
```

## 下一步

- 行動 1
- 行動 2
""",
        encoding="utf-8",
    )

    # README.md
    readme_path = directory / "README.md"
    readme_path.write_text(
        f"""# {directory.name} — learn2deck 專案

這個目錄由 `learn2deck init` 建立。

## 檔案

- `outline.yaml` — 結構化大綱（精確控制每張投影片）
- `content.md` — Markdown 內容（自動推斷版型）

## 使用方式

### 從 Markdown

```bash
learn2deck build content.md -o output.pptx
```

### 從 YAML

```bash
learn2deck build outline.yaml -o output.pptx
```

### 套用不同主題

```bash
learn2deck build content.md -o output.pptx --theme minimal-bw
```

### 驗證

```bash
learn2deck validate output.pptx
```

## 切換主題

```bash
learn2deck theme list
learn2deck theme show minimal-bw
learn2deck theme new my-theme --base claude-orange
```
""",
        encoding="utf-8",
    )

    console.print(f"[green]✓ 已初始化 {directory}/[/green]")
    console.print(f"   • {outline_path}")
    console.print(f"   • {content_path}")
    console.print(f"   • {readme_path}")
    console.print()
    console.print(f"[cyan]下一步：[/cyan]learn2deck build {content_path} -o {directory}/output.pptx")


# === skill ===

skill_app = typer.Typer(help="管理 Claude Skill 安裝", no_args_is_help=True)
app.add_typer(skill_app, name="skill")


@skill_app.command("install")
def skill_install(
    target: Optional[Path] = typer.Option(
        None,
        "--target", "-t",
        help="安裝目標目錄（預設 ~/.claude/skills/learn2deck）",
    ),
    force: bool = typer.Option(
        False,
        "--force", "-f",
        help="覆蓋現有安裝",
    ),
):
    """把 learn2deck SKILL 安裝到 Claude skills 目錄

    安裝位置預設為 ~/.claude/skills/learn2deck/
    安裝後 Claude Code 即可透過觸發語使用本 skill。

    範例：

        learn2deck skill install

        learn2deck skill install --target ~/my-skills/learn2deck

        learn2deck skill install --force
    """
    from .lib.skill import install_skill

    try:
        install_path = install_skill(target=target, force=force)
    except FileNotFoundError as e:
        error_console.print(f"[red]❌ {e}[/red]")
        raise typer.Exit(1)
    except FileExistsError as e:
        error_console.print(f"[red]❌ {e}[/red]")
        raise typer.Exit(1)

    console.print(f"[bold green]✅ SKILL 已安裝：{install_path}[/bold green]")
    console.print()
    console.print("[cyan]使用方式[/cyan]")
    console.print("   在 Claude Code 中輸入觸發語，例如：")
    console.print('   • "幫我把 04-skills.md 做成簡報"')
    console.print('   • "從 markdown 產生 pptx"')
    console.print('   • "build a deck from this md"')
    console.print()
    console.print(f"   [dim]如需移除：rm -rf {install_path}[/dim]")


@skill_app.command("path")
def skill_path():
    """顯示 SKILL 檔案的安裝位置（隨套件發佈）"""
    from .lib.skill import find_skill_dir

    skill_dir = find_skill_dir()
    if skill_dir is None:
        error_console.print("[red]❌ 找不到 SKILL 檔案[/red]")
        raise typer.Exit(1)

    skill_md = skill_dir / "SKILL.md"
    console.print(f"[bold cyan]📂 SKILL 檔案位置[/bold cyan]")
    console.print(f"   {skill_md}")


# === main callback ===

@app.callback()
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        None,
        "--version",
        callback=lambda v: version_callback(v) if v else None,
        is_eager=True,
        help="顯示版本並離開",
    ),
):
    """learn2deck - Markdown 轉 PPTX 工具"""
    pass


def version_callback(value: bool):
    if value:
        console.print(f"[bold green]learn2deck[/bold green] v{__version__}")
        raise typer.Exit()


if __name__ == "__main__":
    app()
