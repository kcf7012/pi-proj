"""
R5: PPTX 格式驗證

規則：產出檔案必須是 Microsoft PowerPoint 2007+ 格式

策略：
1. 副檔名必須是 .pptx
2. 檔案必須是有效的 ZIP（PPTX 內部用 ZIP）
3. 檔案必須能被 python-pptx 重新讀取
"""
from __future__ import annotations

import zipfile
from pathlib import Path
from typing import TYPE_CHECKING

from .base import BaseValidator, Severity

if TYPE_CHECKING:
    pass


class FileFormatValidator(BaseValidator):
    """PPTX 檔案格式驗證

    注意：這個 validator 在檔案層級運作，不是投影片層級
    """

    rule_id = "R5"

    def validate(self, prs_or_path) -> list[Issue]:
        """驗證 PPTX 檔案格式

        接受兩種輸入：
        - str/Path：檔案路徑（會檢查檔案本身）
        - Presentation：已載入的物件（只能檢查物件有效性）
        """
        if isinstance(prs_or_path, (str, Path)):
            return self._validate_file(Path(prs_or_path))
        else:
            # Presentation 物件：檢查是否能被正常讀取
            return self._validate_presentation(prs_or_path)

    def _validate_file(self, path: Path) -> list[Issue]:
        """驗證檔案路徑"""
        issues: list[Issue] = []

        # 1. 副檔名
        if path.suffix.lower() != ".pptx":
            issues.append(self.make_error(
                f"副檔名錯誤：{path.suffix}（應為 .pptx）",
                file_path=str(path),
            ))
            return issues  # 後續檢查沒意義

        # 2. 檔案存在
        if not path.exists():
            issues.append(self.make_error(
                f"檔案不存在：{path}",
                file_path=str(path),
            ))
            return issues

        # 3. ZIP 格式
        if not zipfile.is_zipfile(path):
            issues.append(self.make_error(
                f"不是有效的 PPTX（ZIP 格式錯誤）：{path}",
                file_path=str(path),
            ))
            return issues

        # 4. 內部結構檢查（PPTX 必須有特定檔案）
        try:
            with zipfile.ZipFile(path, "r") as zf:
                names = zf.namelist()
                # 必要檔案
                required = [
                    "[Content_Types].xml",
                    "ppt/presentation.xml",
                ]
                missing = [r for r in required if r not in names]
                if missing:
                    issues.append(self.make_error(
                        f"PPTX 內部結構不完整，缺少：{', '.join(missing)}",
                        file_path=str(path),
                    ))
                    return issues
        except zipfile.BadZipFile:
            issues.append(self.make_error(
                f"ZIP 檔案損壞：{path}",
                file_path=str(path),
            ))

        return issues

    def _validate_presentation(self, prs) -> list[Issue]:
        """驗證 Presentation 物件"""
        issues: list[Issue] = []

        try:
            # 基本健全性檢查
            n_slides = len(prs.slides)
            if n_slides == 0:
                issues.append(self.make_warning(
                    "PPTX 沒有任何投影片",
                ))
        except Exception as e:
            issues.append(self.make_error(
                f"Presentation 物件無效：{e}",
            ))

        return issues
