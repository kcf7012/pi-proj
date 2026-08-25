"""
learn2deck CLI 測試

使用 typer.testing.CliRunner 測試各指令。
"""
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from learn2deck.cli import app

runner = CliRunner()


# === version ===
class TestVersion:
    def test_version(self):
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "learn2deck" in result.stdout
        assert "0.1.0" in result.stdout

    def test_version_flag(self):
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.stdout


# === help ===
class TestHelp:
    def test_root_help(self):
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "build" in result.stdout
        assert "validate" in result.stdout
        assert "theme" in result.stdout
        assert "init" in result.stdout

    def test_build_help(self):
        result = runner.invoke(app, ["build", "--help"])
        assert result.exit_code == 0
        assert "--theme" in result.stdout
        assert "--output" in result.stdout
        assert "--validate" in result.stdout

    def test_validate_help(self):
        result = runner.invoke(app, ["validate", "--help"])
        assert result.exit_code == 0
        assert "--rules" in result.stdout

    def test_theme_help(self):
        result = runner.invoke(app, ["theme", "--help"])
        assert result.exit_code == 0
        assert "list" in result.stdout
        assert "show" in result.stdout


# === build ===
class TestBuild:
    @pytest.fixture
    def md_file(self, tmp_path):
        f = tmp_path / "test.md"
        f.write_text("# Test\n\n## Section\n\ncontent here")
        return f

    def test_basic_build(self, md_file, tmp_path):
        out = tmp_path / "out.pptx"
        result = runner.invoke(app, [
            "build", str(md_file),
            "-o", str(out),
            "--quiet",
        ])
        assert result.exit_code == 0
        assert out.exists()
        assert out.stat().st_size > 0

    def test_build_with_custom_theme(self, md_file, tmp_path):
        out = tmp_path / "out.pptx"
        result = runner.invoke(app, [
            "build", str(md_file),
            "-o", str(out),
            "--theme", "minimal-bw",
            "--quiet",
        ])
        assert result.exit_code == 0
        assert out.exists()

    def test_build_nonexistent_file(self, tmp_path):
        result = runner.invoke(app, [
            "build", "/nonexistent/file.md",
            "-o", str(tmp_path / "out.pptx"),
        ])
        assert result.exit_code == 1
        assert "不存在" in result.stderr or "不存在" in result.stdout

    def test_build_with_validate(self, md_file, tmp_path):
        out = tmp_path / "out.pptx"
        result = runner.invoke(app, [
            "build", str(md_file),
            "-o", str(out),
            "--validate",
            "--quiet",
        ])
        assert result.exit_code == 0
        assert out.exists()

    def test_build_with_strict_validate(self, md_file, tmp_path):
        out = tmp_path / "out.pptx"
        result = runner.invoke(app, [
            "build", str(md_file),
            "-o", str(out),
            "--validate",
            "--strict",
            "--quiet",
        ])
        # 簡單 test.md 應該通過
        assert result.exit_code == 0

    def test_build_with_invalid_theme(self, md_file, tmp_path):
        out = tmp_path / "out.pptx"
        result = runner.invoke(app, [
            "build", str(md_file),
            "-o", str(out),
            "--theme", "nonexistent-theme",
            "--quiet",
        ])
        assert result.exit_code == 1
        assert "找不到" in result.stderr or "找不到" in result.stdout


# === validate ===
class TestValidate:
    @pytest.fixture
    def pptx_file(self, tmp_path):
        # 建立一個有效的 PPTX
        from learn2deck.lib.parsers import parse_content
        from learn2deck.lib.builders import build_full_deck
        md = tmp_path / "test.md"
        md.write_text("# Test\n\n## Section\n\ncontent")
        pptx = tmp_path / "test.pptx"
        deck = parse_content(str(md))
        build_full_deck(deck, str(pptx))
        return pptx

    def test_validate_passing(self, pptx_file):
        result = runner.invoke(app, ["validate", str(pptx_file)])
        assert result.exit_code == 0
        assert "PASSED" in result.stdout

    def test_validate_with_json(self, pptx_file):
        result = runner.invoke(app, [
            "validate", str(pptx_file), "--json",
        ])
        assert result.exit_code == 0
        # 應為合法 JSON
        import json
        data = json.loads(result.stdout)
        assert "passed" in data
        assert "issues" in data
        assert "stats" in data

    def test_validate_with_specific_rules(self, pptx_file):
        result = runner.invoke(app, [
            "validate", str(pptx_file), "--rules", "R1,R5",
        ])
        assert result.exit_code == 0

    def test_validate_with_invalid_rules(self, pptx_file):
        result = runner.invoke(app, [
            "validate", str(pptx_file), "--rules", "R99",
        ])
        assert result.exit_code == 1
        assert "未知" in result.stderr or "未知" in result.stdout

    def test_validate_nonexistent_file(self, tmp_path):
        result = runner.invoke(app, [
            "validate", str(tmp_path / "nonexistent.pptx"),
        ])
        assert result.exit_code == 1

    def test_validate_quiet(self, pptx_file):
        result = runner.invoke(app, [
            "validate", str(pptx_file), "--quiet",
        ])
        assert result.exit_code == 0
        # 簡單 test.md 沒有 issues，所以 quiet 應該輸出「無問題」或「PASSED」
        # 不需要驗證具體文字


# === theme ===
class TestTheme:
    def test_theme_list(self):
        result = runner.invoke(app, ["theme", "list"])
        assert result.exit_code == 0
        assert "claude-orange" in result.stdout
        assert "minimal-bw" in result.stdout

    def test_theme_show_claude(self):
        result = runner.invoke(app, ["theme", "show", "claude-orange"])
        assert result.exit_code == 0
        assert "claude-orange" in result.stdout
        assert "primary" in result.stdout  # 顏色

    def test_theme_show_minimal_bw(self):
        result = runner.invoke(app, ["theme", "show", "minimal-bw"])
        assert result.exit_code == 0
        assert "minimal-bw" in result.stdout

    def test_theme_show_nonexistent(self):
        result = runner.invoke(app, ["theme", "show", "nonexistent"])
        assert result.exit_code == 1
        assert "找不到" in result.stderr or "找不到" in result.stdout

    def test_theme_new(self, tmp_path):
        out_yaml = tmp_path / "my-theme.yaml"
        result = runner.invoke(app, [
            "theme", "new", "my-theme",
            "--base", "claude-orange",
            "-o", str(out_yaml),
        ])
        assert result.exit_code == 0
        assert out_yaml.exists()

    def test_theme_validate_valid(self, tmp_path):
        # 用真實的內建主題檔案測試
        from learn2deck.lib.themes import get_builtin_theme_path
        theme_path = get_builtin_theme_path("claude-orange")
        result = runner.invoke(app, [
            "theme", "validate", str(theme_path),
        ])
        assert result.exit_code == 0
        assert "有效" in result.stdout

    def test_theme_validate_invalid(self, tmp_path):
        bad = tmp_path / "bad.yaml"
        bad.write_text("name: bad\ncolors:\n  primary: not-a-color")
        result = runner.invoke(app, [
            "theme", "validate", str(bad),
        ])
        assert result.exit_code == 1


# === init ===
class TestInit:
    def test_init_creates_files(self, tmp_path):
        target = tmp_path / "new-deck"
        result = runner.invoke(app, ["init", str(target)])
        assert result.exit_code == 0
        assert (target / "outline.yaml").exists()
        assert (target / "content.md").exists()
        assert (target / "README.md").exists()

    def test_init_default_directory(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["init"])
        assert result.exit_code == 0
        assert (tmp_path / "my-deck").exists()
        assert (tmp_path / "my-deck" / "outline.yaml").exists()

    def test_init_files_have_correct_content(self, tmp_path):
        target = tmp_path / "deck"
        runner.invoke(app, ["init", str(target)])

        outline = (target / "outline.yaml").read_text()
        assert "deck:" in outline
        assert "title:" in outline
        assert "slides:" in outline

        content = (target / "content.md").read_text()
        assert "#" in content  # 有 markdown 標題

        readme = (target / "README.md").read_text()
        assert "learn2deck" in readme
        assert "learn2deck build" in readme

    def test_init_then_build(self, tmp_path):
        """init 後能直接 build 範本"""
        target = tmp_path / "deck"
        runner.invoke(app, ["init", str(target)])

        result = runner.invoke(app, [
            "build", str(target / "content.md"),
            "-o", str(target / "out.pptx"),
            "--validate",
            "--quiet",
        ])
        assert result.exit_code == 0
        assert (target / "out.pptx").exists()


# === 整合測試 ===
class TestEndToEndCLI:
    """完整流程：init → build → validate"""

    def test_full_workflow(self, tmp_path, monkeypatch):
        # 1. init
        target = tmp_path / "workflow-test"
        result = runner.invoke(app, ["init", str(target)])
        assert result.exit_code == 0

        # 2. build
        out = target / "out.pptx"
        result = runner.invoke(app, [
            "build", str(target / "content.md"),
            "-o", str(out),
            "--validate",
            "--quiet",
        ])
        assert result.exit_code == 0
        assert out.exists()

        # 3. validate（單獨跑）
        result = runner.invoke(app, ["validate", str(out), "--json", "--quiet"])
        assert result.exit_code == 0
