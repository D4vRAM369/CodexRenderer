from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_cli_generates_markdown(tmp_path: Path) -> None:
    src = tmp_path / "note.txt"
    src.write_text("Hello Codex", encoding="utf-8")
    out_dir = tmp_path / "output"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "codexrenderer.cli",
            str(src),
            "-o",
            str(out_dir),
            "--md-only",
            "--inline-css",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr

    md_path = out_dir / "note.md"
    assert md_path.exists()
    content = md_path.read_text(encoding="utf-8")
    assert "style" in content  # CSS embebido
