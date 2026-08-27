"""
learn2deck.lib.skill - Claude Skill 整合工具

提供：
- find_skill_dir(): 找出隨套件發佈的 SKILL 檔案位置
- install_skill(): 把 SKILL 安裝到 ~/.claude/skills/learn2deck/
"""
from __future__ import annotations

import shutil
from importlib import metadata as importlib_metadata
from pathlib import Path

# SKILL 的必要檔案/目錄
SKILL_FILES = ["SKILL.md"]
SKILL_DIRS = ["references", "templates", "examples"]


def _find_in_wheel() -> Path | None:
    """從 wheel 的 data files 找 SKILL.md"""
    try:
        pkg_files = importlib_metadata.files("learn2deck")
        if pkg_files is None:
            return None
        for f in pkg_files:
            # data files 路徑通常類似 "share/learn2deck/skill/SKILL.md"
            path_str = str(f)
            if path_str.endswith("SKILL.md") and "share" in path_str:
                # f.locate() 在 wheel 內指向實際位置
                skill_md = Path(str(f.locate()))  # type: ignore[attr-defined]
                if skill_md.exists():
                    return skill_md.parent
    except Exception:
        pass
    return None


def _find_in_source(pkg_root: Path) -> Path | None:
    """從原始碼 checkout 找 SKILL 目錄

    兩種情境：
    A) share/learn2deck/skill/ 已建立（build wheel 前的準備）
    B) SKILL.md 在套件根目錄（開發模式、git checkout）

    Returns:
        Path 到「邏輯上的 SKILL 目錄」，可能是 share/.../skill 或套件根
    """
    # 情境 A
    share_skill = pkg_root / "share" / "learn2deck" / "skill"
    if (share_skill / "SKILL.md").exists():
        return share_skill

    # 情境 B：直接在套件根（dev 模式）
    if (pkg_root / "SKILL.md").exists():
        return pkg_root

    return None


def find_skill_dir() -> Path | None:
    """找出隨套件發佈的 SKILL 目錄

    搜尋順序：
    1. importlib.metadata 查 wheel 的 data files（pip install 後的位置）
    2. 相對於套件源碼（dev 模式 / git checkout）

    Returns:
        Path 到包含 SKILL.md 的目錄，找不到則回傳 None
    """
    # 方案 A：wheel data files
    wheel_skill = _find_in_wheel()
    if wheel_skill is not None:
        return wheel_skill

    # 方案 B：原始碼
    pkg_root = Path(__file__).parent.parent.parent  # learn2deck/lib → learn2deck → 套件根
    return _find_in_source(pkg_root)


def _copy_skill_subset(src: Path, dst: Path) -> None:
    """複製 SKILL 相關檔案到目標目錄

    從 src 挑出：
    - SKILL.md
    - references/ (整個目錄)
    - templates/ (整個目錄)
    - examples/ (整個目錄，gitkeep 等空檔案會跳過)

    其他檔案（HANDOFF.md、learn2deck/ 套件本體、tests/ 等）不複製
    """
    # 複製單一檔案
    for filename in SKILL_FILES:
        src_file = src / filename
        if src_file.exists():
            shutil.copy2(src_file, dst / filename)

    # 複製子目錄（忽略 .gitkeep 等佔位檔）
    def _ignore(parent: Path, names: list[str]) -> set[str]:
        return {n for n in names if n == ".gitkeep" or n.startswith(".")}

    for dirname in SKILL_DIRS:
        src_dir = src / dirname
        if src_dir.exists():
            shutil.copytree(src_dir, dst / dirname, dirs_exist_ok=True, ignore=_ignore)


def install_skill(target: Path | None = None, force: bool = False) -> Path:
    """把 SKILL 安裝到指定目錄

    Args:
        target: 目標目錄（預設 ~/.claude/skills/learn2deck）
        force: 強制覆蓋現有目錄

    Returns:
        安裝後的目標路徑

    Raises:
        FileNotFoundError: 找不到 SKILL 目錄
        FileExistsError: 目標已存在但未設 force
    """
    skill_dir = find_skill_dir()
    if skill_dir is None:
        raise FileNotFoundError(
            "找不到 SKILL.md。請確認套件安裝完整（pip install --force-reinstall learn2deck）"
        )

    if target is None:
        target = Path.home() / ".claude" / "skills" / "learn2deck"

    target = target.expanduser().resolve()

    if target.exists() and not force:
        raise FileExistsError(
            f"目標已存在：{target}\n"
            f"如要覆蓋請加 --force，或指定其他 --target"
        )

    # 建立目標目錄
    target.parent.mkdir(parents=True, exist_ok=True)

    # 清空並重建
    if target.exists() and force:
        shutil.rmtree(target)
    target.mkdir(parents=True)

    # 只複製 SKILL 相關檔案（不要把整個 source tree 複製過去）
    _copy_skill_subset(skill_dir, target)

    return target
