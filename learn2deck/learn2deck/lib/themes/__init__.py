"""learn2deck.themes - 內建主題

主題是 YAML 檔案，由 core.theme.load_theme() 載入。
此處只暴露內建主題的清單函式（給 CLI 用）。
"""
from pathlib import Path


def list_builtin_themes() -> list[str]:
    """列出所有內建主題的名稱（不含 .yaml 副檔名）"""
    themes_dir = Path(__file__).parent
    return sorted(p.stem for p in themes_dir.glob("*.yaml"))


def get_builtin_theme_path(name: str) -> Path:
    """取得內建主題的完整路徑"""
    return Path(__file__).parent / f"{name}.yaml"
