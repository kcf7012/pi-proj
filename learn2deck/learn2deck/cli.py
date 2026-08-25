"""
learn2deck CLI 入口

使用 typer 框架，提供 build / validate / theme / init 四大指令。
"""
import typer
from rich.console import Console

from . import __version__

app = typer.Typer(
    name="learn2deck",
    help="從 Markdown 教材與技術文件產生符合設計風格的 PPTX 簡報",
    no_args_is_help=True,
    rich_markup_mode="rich",
)
console = Console()


@app.command()
def version():
    """顯示版本資訊"""
    console.print(f"[bold green]learn2deck[/bold green] v{__version__}")


@app.callback()
def main(
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
