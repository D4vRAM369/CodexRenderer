#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Helpers para renderizar logs en estilo Claude-Code.
Basado en `geminirenderer_core`, pero enlazando con el nuevo tema ámbar.
"""
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Tuple

from .geminirenderer_core import ensure_pandoc, read_odt, read_plain_txt
from .styles import claude_code


def markdown_to_html(md_text: str, metadata: Optional[dict] = None) -> str:
    """
    Convierte Markdown a HTML embebiendo la hoja Claude-Code.
    """
    ensure_pandoc()
    meta = metadata or {"title": "Claude-Code Export"}

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        md_path = tmp_dir / "input.md"
        out_path = tmp_dir / "output.html"
        md_path.write_text(md_text, encoding="utf-8")

        cmd = [
            "pandoc",
            str(md_path),
            "-o",
            str(out_path),
            "--from",
            "markdown+raw_html-tex_math_dollars-tex_math_single_backslash",
            "--to",
            "html5",
            "--standalone",
            "--embed-resources",
            "--highlight-style",
            "espresso",
        ]
        for key, value in meta.items():
            if value:
                cmd += ["--metadata", f"{key}={value}"]

        subprocess.run(cmd, check=True)
        html_str = out_path.read_text(encoding="utf-8", errors="replace")

    html_str = claude_code.postprocess_html(html_str)
    css = claude_code.claude_css()
    style_tag = f"<style>\n{css}\n</style>\n"
    if "</head>" in html_str:
        return html_str.replace("</head>", style_tag + "</head>")
    return style_tag + html_str


def _maybe_convert_md_content(md_text: str) -> str:
    """
    Evita transformar dos veces si ya contiene el banner Claude/Gemini.
    """
    if '<div class="banner">' in md_text:
        return md_text
    return claude_code.to_markdown_claude(md_text)


def convert_path(input_path: Path, output_dir: Optional[Path] = None) -> Tuple[Path, Path]:
    """
    Convierte un archivo soportado a Markdown + HTML Claude-Code.
    """
    if output_dir is None:
        output_dir = input_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    suffix = input_path.suffix.lower()
    stem = input_path.stem

    md_path = output_dir / f"{stem}.claude-code.md"
    html_path = output_dir / f"{stem}.claude-code.html"

    if suffix == ".txt":
        source_text = read_plain_txt(input_path)
        md_text = claude_code.to_markdown_claude(source_text)
    elif suffix == ".odt":
        source_text = read_odt(input_path)
        md_text = claude_code.to_markdown_claude(source_text)
    elif suffix == ".md":
        md_raw = read_plain_txt(input_path)
        md_text = _maybe_convert_md_content(md_raw)
    else:
        raise RuntimeError(
            f"Formato no soportado para Claude-Code Renderer: {input_path.name} "
            "(usa .txt, .md o .odt)"
        )

    md_path.write_text(md_text, encoding="utf-8")
    html_text = markdown_to_html(md_text, metadata={"title": stem})
    html_path.write_text(html_text, encoding="utf-8")
    return md_path, html_path


__all__ = ["convert_path", "markdown_to_html"]
