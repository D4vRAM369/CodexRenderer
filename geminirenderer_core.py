#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Core helpers for GeminiRenderer workflows.
Provide conversions txt/odt/md -> Gemini-flavoured Markdown -> HTML with embedded CSS.
"""
from __future__ import annotations

import html
import shlex
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Tuple

from styles import gemini


def read_plain_txt(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def read_odt(path: Path) -> str:
    """
    Extracts text content from an ODT document, preserving basic paragraphs.
    """
    try:
        from odf.opendocument import load
        from odf import teletype
        from odf.text import H, P, ListItem
    except Exception as exc:
        raise RuntimeError("Instala odfpy para leer archivos .odt (pip install odfpy)") from exc

    doc = load(str(path))
    pieces: list[str] = []
    for element in (
        doc.getElementsByType(H)
        + doc.getElementsByType(P)
        + doc.getElementsByType(ListItem)
    ):
        text = teletype.extractText(element) or ""
        text = text.strip()
        if text:
            pieces.append(text)

    if not pieces:
        body = teletype.extractText(doc.text) or ""
        body = body.strip()
        if body:
            pieces.append(body)

    return "\n".join(pieces).strip() + "\n"


def ensure_pandoc() -> None:
    if shutil.which("pandoc") is None:
        raise RuntimeError(
            "pandoc no encontrado. Instálalo con: sudo apt install -y pandoc"
        )


def markdown_to_html(md_text: str, metadata: Optional[dict] = None) -> str:
    """
    Render Markdown to HTML using pandoc and embed Gemini CSS.
    """
    ensure_pandoc()
    if metadata is None:
        metadata = {"title": "GeminiRenderer Export"}

    with tempfile.TemporaryDirectory() as tmp:
        md_path = Path(tmp) / "input.md"
        out_path = Path(tmp) / "output.html"
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
        for key, value in (metadata or {}).items():
            if value:
                cmd += ["--metadata", f"{key}={value}"]

        subprocess.run(cmd, check=True)
        html_str = out_path.read_text(encoding="utf-8", errors="replace")

    html_str = gemini.postprocess_html_for_kotlin(html_str)
    css = gemini.gemini_css()
    style_tag = f"<style>\n{css}\n</style>\n"
    if "</head>" in html_str:
        html_str = html_str.replace("</head>", style_tag + "</head>")
    else:
        html_str = style_tag + html_str
    return html_str


def _maybe_convert_md_content(md_text: str) -> str:
    """
    Gemini exports converted to Markdown already contain the banner marker.
    Detect it to avoid double-wrapping.
    """
    if '<div class="banner">' in md_text:
        return md_text
    return gemini.to_markdown_gemini(md_text)


def convert_path(input_path: Path, output_dir: Optional[Path] = None) -> Tuple[Path, Path]:
    """
    Convert input path to Gemini-style Markdown + HTML.
    Returns tuple (markdown_path, html_path).
    """
    if output_dir is None:
        output_dir = input_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    suffix = input_path.suffix.lower()
    stem = input_path.stem

    md_path = output_dir / f"{stem}.gemini.md"
    html_path = output_dir / f"{stem}.gemini.html"

    if suffix == ".txt":
        source_text = read_plain_txt(input_path)
        md_text = gemini.to_markdown_gemini(source_text)
    elif suffix == ".odt":
        source_text = read_odt(input_path)
        md_text = gemini.to_markdown_gemini(source_text)
    elif suffix == ".md":
        md_raw = read_plain_txt(input_path)
        md_text = _maybe_convert_md_content(md_raw)
    else:
        raise RuntimeError(
            f"Formato no soportado para GeminiRenderer: {input_path.name} "
            "(usa .txt, .md o .odt)"
        )

    md_path.write_text(md_text, encoding="utf-8")
    html_text = markdown_to_html(md_text, metadata={"title": stem})
    html_path.write_text(html_text, encoding="utf-8")
    return md_path, html_path


__all__ = [
    "convert_path",
    "markdown_to_html",
    "read_plain_txt",
    "read_odt",
    "ensure_pandoc",
]
