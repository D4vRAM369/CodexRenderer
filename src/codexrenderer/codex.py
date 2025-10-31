from __future__ import annotations

"""
CodexRenderer conversion pipeline.

This module exposes helpers to turn .txt/.odt/.md files into Markdown + HTML
with the dark “Alacritty/Codex” theme embedded in the HTML output.
"""

import re
import shutil
import subprocess
import tempfile
from importlib import resources
from pathlib import Path
from typing import List, Optional, Tuple

__all__ = [
    "convert_file",
    "convert_lines_to_markdown",
    "ensure_pandoc",
    "read_odt_input",
    "read_text_input",
]


# ------------------- Lectura -------------------
def read_text_input(path: Path) -> List[str]:
    return path.read_text(encoding="utf-8", errors="replace").splitlines()


def read_odt_input(path: Path) -> List[str]:
    try:
        from odf.opendocument import load
        from odf import text
    except Exception as exc:  # pragma: no cover - import guard
        raise RuntimeError("Instala odfpy:  pip install odfpy") from exc

    doc = load(str(path))
    lines: List[str] = []
    for paragraph in doc.getElementsByType(text.P):
        frag = "".join(
            node.data
            if hasattr(node, "data")
            else (
                node.firstChild.data
                if hasattr(node, "firstChild") and hasattr(node.firstChild, "data")
                else ""
            )
            for node in paragraph.childNodes
        )
        lines.extend(frag.splitlines() or [""])
    return lines


# ------------------- Heurísticas -------------------
CODE_KWS = {
    "kotlin": [
        r"\bfun\b",
        r"\bdata\s+class\b",
        r"\bval\b",
        r"\bvar\b",
        r"import\s+android",
        r"Coroutine",
        r"@Composable",
    ],
    "java": [
        r"\bpublic\b",
        r"\bclass\b",
        r"\bstatic\b",
        r"\bvoid\b",
        r";\s*$",
        r"System\.out\.print",
    ],
    "python": [r"^def\s", r"^class\s", r":\s*$", r"\bimport\b", r"\basync\b", r"\bawait\b"],
    "bash": [
        r"^#!/usr/bin/env\s+bash",
        r"\b#!/bin/bash",
        r"\bset -e",
        r"\bgrep\b",
        r"\bawk\b",
        r"\btar\b",
        r"\badb\b",
    ],
    "json": [r"^\s*\{", r"\}\s*$", r'"\w+"\s*:'],
    "xml": [r"^\s*<\?xml", r"^\s*<[\w\-]+", r"</[\w\-]+>\s*$"],
}

PROMPT_CHARS = r"[>\u203A\u00BB]"  # >  ›  »


def guess_language(lines: List[str]) -> str:
    scores = {key: 0 for key in CODE_KWS}
    for line in lines[: min(80, len(lines))]:
        for lang, patterns in CODE_KWS.items():
            if any(re.search(pattern, line) for pattern in patterns):
                scores[lang] += 1
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else ""


def looks_like_code(line: str) -> bool:
    if line.strip().startswith("```"):
        return True
    if re.match(r"^\s{4,}\S", line):
        return True
    if any(
        token in line
        for token in ["package ", "import ", "@Composable", "class ", "fun ", "val ", "var ", "#!/"]
    ):
        return True
    if sum(line.count(token) for token in ["{", "}", ";", "(", ")"]) >= 2:
        return True
    return False


def is_ai_thought(line: str) -> bool:
    return bool(re.match(r"^\s*[•\-\*\u2022]\s+", line))


def is_question(line: str) -> bool:
    if re.match(r"^\s*\?\s+", line):
        return True
    return bool(
        re.match(rf"^\s*{PROMPT_CHARS}\s*PNL(?:[:\-]\s+|\s+)", line, flags=re.IGNORECASE)
    )


def is_prompt(line: str) -> bool:
    return bool(re.match(rf"^\s*{PROMPT_CHARS}\s+(?!PNL\b)", line, flags=re.IGNORECASE))


# ------------------- Utilidades -------------------
def escape_html(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def escape_md(text: str) -> str:
    if re.match(r"^\s*#{1,6}\s+\S", text):
        return "\\" + text
    return text


def visible_arrow(symbol: str) -> str:
    return "&gt;" if symbol == ">" else symbol


def _inline_css_banner() -> str:
    with resources.as_file(
        resources.files("codexrenderer.assets").joinpath("alacritty.css")
    ) as css_file:
        css_text = css_file.read_text(encoding="utf-8")
    return f"<style>\n{css_text}\n</style>\n"


# ------------------- Conversión -------------------
def convert_lines_to_markdown(lines: List[str], inline_css: bool) -> str:
    out: List[str] = []
    if inline_css:
        out.append(_inline_css_banner())

    i = 0
    total = len(lines)
    inside_backticks = False

    while i < total:
        line = lines[i]

        if line.strip().startswith("```"):
            out.append(line)
            inside_backticks = not inside_backticks
            i += 1
            continue
        if inside_backticks:
            out.append(line)
            i += 1
            continue

        if re.match(r"^[+-](?![+-])", line):
            block: List[str] = []
            clean_block: List[str] = []
            while i < total and (
                re.match(r"^[+-](?![+-])", lines[i]) or lines[i].strip() == ""
            ):
                current_line = lines[i]
                if re.match(r"^[+](?![+-])", current_line):
                    clean_block.append(current_line[1:])
                elif re.match(r"^[-](?![+-])", current_line):
                    clean_block.append(current_line[1:])
                else:
                    clean_block.append(current_line)
                block.append(current_line)
                i += 1

            lang = guess_language(clean_block)
            code = "\n".join(clean_block)
            if inline_css:
                out.append('<pre class="term"><code>')
            out.append(f"```{lang}\n{code}\n```")
            if inline_css:
                out.append("</code></pre>")
            continue

        if is_ai_thought(line):
            text = re.sub(r"^\s*[•\-\*\u2022]\s*", "", line).strip()
            j = i + 1
            extra: List[str] = []
            while (
                j < total
                and lines[j].strip()
                and not re.match(r"^[+-](?![+-])", lines[j])
                and not looks_like_code(lines[j])
                and not is_question(lines[j])
                and not is_prompt(lines[j])
            ):
                extra.append(lines[j].strip())
                j += 1
            if extra:
                text += " " + " ".join(extra)
                i = j
            else:
                i += 1
            out.append(f'<span class="ait"><em>{escape_html(text)}</em></span>')
            continue

        match_q = re.match(r"^\s*(\?)\s+(.*)$", line)
        if match_q:
            symbol, text = match_q.group(1), match_q.group(2).strip()
            out.append(f'<span class="q">{escape_html(symbol + " " + text)}</span>')
            i += 1
            continue

        match_pnl = re.match(
            rf"^\s*({PROMPT_CHARS})\s*PNL(?:[:\-]\s+|\s+)(.*)$", line, flags=re.IGNORECASE
        )
        if match_pnl:
            symbol, text = match_pnl.group(1), match_pnl.group(2).strip()
            out.append(f'<span class="q">{visible_arrow(symbol)} {escape_html(text)}</span>')
            i += 1
            continue

        if is_prompt(line):
            while i < total and is_prompt(lines[i]):
                prompt_match = re.match(
                    rf"^\s*({PROMPT_CHARS})\s+(.*)$", lines[i], flags=re.IGNORECASE
                )
                if prompt_match:
                    symbol, text = prompt_match.group(1), prompt_match.group(2).strip()
                    out.append(
                        f'<span class="prompt">{visible_arrow(symbol)} {escape_html(text)}</span>'
                    )
                else:
                    out.append(escape_md(lines[i]))
                i += 1
            continue

        if looks_like_code(line):
            block = [line]
            j = i + 1
            while (
                j < total
                and looks_like_code(lines[j])
                and not lines[j].strip().startswith("```")
            ):
                block.append(lines[j])
                j += 1
            lang = guess_language(block)
            code = "\n".join(block)
            if inline_css:
                out.append('<pre class="term"><code>')
            out.append(f"```{lang}\n{code}\n```")
            if inline_css:
                out.append("</code></pre>")
            i = j
            continue

        out.append(escape_md(line))
        i += 1

    md_text = "\n".join(out)
    return re.sub(r"\n{3,}", "\n\n", md_text).strip() + "\n"


def ensure_pandoc() -> None:
    if shutil.which("pandoc") is None:
        raise RuntimeError("pandoc no encontrado. Instálalo con: sudo apt install -y pandoc")


def _load_css() -> str:
    with resources.as_file(
        resources.files("codexrenderer.assets").joinpath("alacritty.css")
    ) as css_path:
        return css_path.read_text(encoding="utf-8")


def _write_markdown(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def _pandoc_html(md_path: Path, html_path: Path, title: str, css_text: str) -> None:
    ensure_pandoc()
    with tempfile.TemporaryDirectory() as tmp:
        css_file = Path(tmp) / "codexrenderer.css"
        css_file.write_text(css_text, encoding="utf-8")
        subprocess.run(
            [
                "pandoc",
                str(md_path),
                "-f",
                "markdown+raw_html-tex_math_dollars-tex_math_single_backslash",
                "-t",
                "html5",
                "-s",
                "--embed-resources",
                "--css",
                str(css_file),
                "--highlight-style=pygments",
                "-o",
                str(html_path),
                "--metadata",
                f"title={title}",
            ],
            check=True,
        )


def convert_file(
    input_path: Path,
    out_dir: Optional[Path] = None,
    *,
    inline_css: bool = False,
    embed_css: bool = True,
) -> Tuple[Path, Optional[Path]]:
    """
    Convert input into Markdown + HTML and return the resulting paths.
    """
    input_path = input_path.resolve()
    if out_dir is None:
        out_dir = input_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    suffix = input_path.suffix.lower()
    stem = input_path.stem

    if suffix == ".txt":
        lines = read_text_input(input_path)
        md_text = convert_lines_to_markdown(lines, inline_css)
    elif suffix == ".odt":
        lines = read_odt_input(input_path)
        md_text = convert_lines_to_markdown(lines, inline_css)
    elif suffix == ".md":
        md_text = input_path.read_text(encoding="utf-8")
    else:
        raise RuntimeError("Soportado: .txt, .odt o .md")

    md_path = out_dir / f"{stem}.md"
    _write_markdown(md_path, md_text)

    if embed_css:
        css_text = _load_css()
        html_path = out_dir / f"{stem}.html"
        _pandoc_html(md_path, html_path, title=stem, css_text=css_text)
        html_result: Optional[Path] = html_path
    else:
        html_result = None

    return md_path, html_result
