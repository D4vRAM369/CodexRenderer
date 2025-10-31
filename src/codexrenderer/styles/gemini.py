# -*- coding: utf-8 -*-
"""
Modo Gemini para CodexRenderer:
- Entrada: transcript plano (export/log) o .odt
- Salida intermedia: Markdown enriquecido emulando el estilo visual de GeminiCLI
- Salida final: HTML con CSS que replica colores, paneles y resaltados del cliente Gemini
"""

from __future__ import annotations
from typing import List
import html

# ---------- COLORES / TEMA ----------
GEMINI_CSS = r"""
:root {
  --bg: #0f1117;
  --fg: #d9e3ff;
  --muted: #96a1c4;
  --accent-blue: #7aa8ff;
  --accent-purple: #bd8bff;
  --accent-pink: #ff7dcb;
  --accent-cyan: #3ad7ff;
  --panel-bg: #121a2c;
  --panel-border: #1f2740;
  --panel-shadow: rgba(6, 9, 16, 0.6);
  --code-bg: #151f33;
  --user-bg: rgba(255, 215, 120, 0.08);
  --user-border: rgba(255, 215, 120, 0.35);
  --diff-add-bg: rgba(122, 201, 108, 0.22);
  --diff-add-fg: #dfffd1;
  --diff-del-bg: rgba(255, 118, 118, 0.22);
  --diff-del-fg: #ffd8d8;
  --diff-meta-bg: rgba(90, 110, 160, 0.25);
}
html, body {
  background: var(--bg);
  color: var(--fg);
  font-family: 'JetBrains Mono', 'Fira Code', 'SFMono-Regular', Menlo, Consolas, 'Liberation Mono', monospace;
  line-height: 1.65;
  margin: 0;
  padding: 2rem 1.75rem 4rem;
}
a {
  color: var(--accent-cyan);
  text-decoration: none;
  border-bottom: 1px dotted rgba(58, 215, 255, 0.6);
}
a:hover {
  color: var(--accent-purple);
  border-bottom-color: rgba(189, 139, 255, 0.8);
}
p { margin: 0 0 1rem; }
ul, ol { margin: 0 0 1rem 1.4rem; }
li { margin-bottom: 0.35rem; }
hr {
  border: none;
  border-top: 1px solid var(--panel-border);
  margin: 2.2rem 0;
}
pre, code {
  background: var(--code-bg);
  color: var(--fg);
  border-radius: 10px;
}
pre {
  padding: 1rem 1.15rem;
  overflow: auto;
  border: 1px solid var(--panel-border);
  box-shadow: 0 0 0 1px rgba(26, 34, 54, 0.35);
}
code {
  padding: 0.15rem 0.4rem;
  border: 1px solid rgba(31, 39, 64, 0.6);
}
.banner {
  width: 100%;
  margin: -0.7rem 0 1.9rem;
  text-transform: uppercase;
  font-size: 58px;
  letter-spacing: 1.8px;
  font-weight: 900;
  color: transparent;
  background-image: linear-gradient(90deg, #63a8ff 0%, #b681ff 55%, #ff7ac4 100%);
  -webkit-background-clip: text;
  background-clip: text;
  text-shadow: 0 0 22px rgba(75, 145, 255, 0.35);
}
.user-qa {
  margin: 1.6rem 0;
  padding: 0.95rem 1.15rem;
  border-radius: 12px;
  background: var(--user-bg);
  color: #ffe58f;
  border: 1px solid var(--user-border);
  border-left: 4px solid #ffdf70;
  font-weight: 650;
  box-shadow: 0 10px 28px rgba(12, 10, 2, 0.25);
}
.user-qa .lead {
  color: #fff3c4;
  margin-right: 0.6rem;
}
.user-qa br { line-height: 1.7; }
.ia {
  margin: 1.5rem 0;
  color: #d4c2ff;
  font-style: italic;
}
.panel {
  background: var(--panel-bg);
  border: 1px solid var(--panel-border);
  border-radius: 14px;
  margin: 1.75rem 0;
  box-shadow: 0 18px 45px var(--panel-shadow);
  overflow: hidden;
}
.panel-title {
  padding: 1rem 1.2rem 0.6rem;
  font-weight: 700;
  color: var(--accent-blue);
  letter-spacing: 0.4px;
}
.panel-info .panel-title { color: var(--accent-cyan); }
.panel-command .panel-title { color: var(--accent-purple); }
.panel-body {
  padding: 0.35rem 1.2rem 1.2rem;
}
.panel-line {
  white-space: pre;
  font-family: inherit;
  padding: 0.32rem 0.75rem;
  border-radius: 7px;
  margin: 0.05rem 0;
  line-height: 1.5;
  background: transparent;
  border: 1px solid transparent;
  overflow-x: auto;
}
.panel-line:first-child { margin-top: 0; }
.panel-line:last-child { margin-bottom: 0; }
.panel-line.empty {
  min-height: 0.9rem;
}
.panel-grid {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin: 0.4rem 0;
}
.panel-grid .panel-row {
  display: grid;
  gap: 0.55rem;
}
.panel-grid.cols-2 .panel-row {
  grid-template-columns: minmax(0, auto) minmax(0, 1fr);
}
.panel-grid.cols-3 .panel-row {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}
.panel-grid.cols-4 .panel-row {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}
.panel-grid.cols-auto .panel-row {
  grid-template-columns: repeat(auto-fit, minmax(0, 1fr));
}
.panel-grid .panel-cell {
  padding: 0.55rem 0.7rem;
  border-radius: 8px;
  border: 1px solid rgba(31, 39, 64, 0.45);
  background: rgba(26, 34, 54, 0.45);
  white-space: pre;
  font-family: inherit;
  color: var(--fg);
  box-shadow: inset 0 0 0 1px rgba(31, 39, 64, 0.2);
}
pre code.code-diff {
  display: block;
  background: rgba(21, 28, 46, 0.65);
  border: 1px solid rgba(49, 70, 120, 0.35);
  border-radius: 12px;
  padding: 0.48rem 0.35rem;
  margin: 1.5rem 0;
  box-shadow: inset 0 0 0 1px rgba(49, 70, 120, 0.18);
}
pre code.code-diff .diff-line {
  display: inline;
  white-space: pre-wrap;
  padding: 0;
  border-radius: 0;
  margin: 0;
  line-height: inherit;
  color: var(--fg);
}
pre code.code-diff .diff-line::after {
  content: "\\A";
  white-space: pre;
}
pre code.code-diff .diff-add {
  background: var(--diff-add-bg);
  color: var(--fg);
}
pre code.code-diff .diff-del {
  background: var(--diff-del-bg);
  color: var(--fg);
}
pre code.code-diff .diff-meta {
  background: rgba(122, 168, 255, 0.15);
  color: var(--accent-blue);
  font-style: italic;
}
pre code.code-diff .diff-blank {
  min-height: 0.42rem;
  padding-top: 0.22rem;
  padding-bottom: 0.22rem;
}
.panel-diff .panel-line.diff-add {
  background: var(--diff-add-bg);
  color: var(--diff-add-fg);
}
.panel-diff .panel-line.diff-del {
  background: var(--diff-del-bg);
  color: var(--diff-del-fg);
}
.panel-diff .panel-line.diff-meta {
  background: var(--diff-meta-bg);
  color: var(--muted);
  font-style: italic;
}
.panel-command .panel-line {
  background: rgba(122, 168, 255, 0.08);
  color: var(--fg);
  border-color: rgba(49, 70, 120, 0.35);
}
.panel-info .panel-line {
  background: rgba(42, 195, 222, 0.08);
  color: var(--fg);
  border-color: rgba(42, 195, 222, 0.18);
}
.panel-line strong { color: inherit; }
blockquote {
  border-left: 4px solid rgba(122, 168, 255, 0.35);
  background: rgba(17, 26, 44, 0.7);
  padding: 0.85rem 1.2rem;
  border-radius: 10px;
  margin: 1.6rem 0;
  color: var(--muted);
}
table {
  width: 100% !important;
  max-width: 100%;
  border-collapse: collapse;
  margin: 1.5rem 0;
  table-layout: auto;
}
th, td {
  border: 1px solid var(--panel-border);
  padding: 0.6rem 0.8rem;
}
th {
  background: rgba(122, 168, 255, 0.15);
  color: var(--accent-blue);
}
"""

# --- helpers de coloreado mínimo para ver azul/violeta en HTML ---
import re
_KW = r"\b(var|val|fun|by|class|object|if|else|when|return|for|while|override)\b"
_LIT = r"\b(true|false|null)\b"
_TYPE = r"\b(String|Int|Boolean|Float|Double|Long|List|Map|Set|Unit)\b"

def _colorize_kotlin(code:str)->str:
    code = re.sub(_KW, r'<span class="kw">\1</span>', code)
    code = re.sub(_LIT, r'<span class="lit">\1</span>', code)
    code = re.sub(_TYPE, r'<span class="type">\1</span>', code)
    return code

ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")

# ---------- Transformación de texto -> Markdown con “componentes” Gemini ----------
def to_markdown_gemini(src: str, title: str = "GEMINI") -> str:
    """
    Convierte un log/export de Gemini CLI a Markdown con HTML embebido que replica su estilo.
    - Renderiza el banner superior.
    - Reconoce bloques de panel (╭ ╮ ... ╰ ╯) y los transforma en tarjetas .panel.
    - Destaca mensajes del usuario (> …) y pensamientos IA (✦/• …).
    - Agrupa fragmentos de código y diffs para que conserven indentación.
    """
    lines = src.splitlines()
    total = len(lines)
    out: List[str] = [f'<div class="banner">{html.escape(title)}</div>']
    i = 0
    in_fence = False
    skipping_ascii_art = True
    panel_top_chars = ("╭", "┌", "┏", "╔")
    panel_bottom_chars = ("╰", "└", "┗", "╚")
    panel_vertical_chars = ("│", "┃", "║")
    panel_joint_chars = ("├", "┝", "┠", "╞", "╟", "╪", "╫", "┣", "┡", "┢", "╠", "╬")

    def is_fence(s: str) -> bool:
        return s.strip().startswith("```")

    def strip_ansi(s: str) -> str:
        return ANSI_RE.sub("", s)

    def looks_like_code_line(line: str) -> bool:
        raw = strip_ansi(line)
        stripped = raw.lstrip()
        if not stripped:
            return False
        if raw.startswith(("    ", "\t")):
            return True
        if stripped.startswith(("android:", "app:", "tools:", "xmlns:", "<", "</", "<?", "#include", "#define")):
            return True
        if stripped.startswith((
            "val ", "var ", "fun ", "class ", "object ", "data ", "sealed ",
            "enum ", "def ", "async def ", "lambda ", "public ", "private ", "protected ",
            "override ", "static ", "const ", "final ", "return ", "if ", "else ", "elif ",
            "switch ", "case ", "when ", "try ", "catch ", "finally ", "for ", "while "
        )):
            return True
        if stripped.startswith(("using ", "namespace ", "package ", "import ")):
            return True
        if stripped[0].isdigit():
            pos = 0
            while pos < len(stripped) and stripped[pos].isdigit():
                pos += 1
            if pos < len(stripped) and stripped[pos] in ('.', ')', ':'):
                return False  # lista numerada normal
            tail = stripped[pos:].lstrip()
            if not tail:
                return False
            if tail.startswith((
                "<", "{", "}", "fun", "val", "var", "if", "when", "switch",
                "case", "return", "android:", "Material", "ImageButton", "LinearLayout"
            )):
                return True
            if any(ch in tail for ch in "=;{}()<>[]"):
                return True
        if "=" in stripped and any(op in stripped for op in ("==", "!=", "<=", ">=", ":=", "->")) and any(
            sym in stripped for sym in ("(", ")", "{", "}", ";", "<", ">", "[", "]")
        ):
            return True
        if stripped.endswith("{") and ":" in stripped:
            return True
        return False

    def render_panel(box_lines: List[str]) -> str:
        cleaned = [strip_ansi(line).rstrip("\n") for line in box_lines]
        rows_joined: List[str] = []

        if (
            len(cleaned) >= 2
            and cleaned[0].lstrip().startswith(panel_top_chars)
            and cleaned[-1].lstrip().startswith(panel_bottom_chars)
        ):
            current = ""
            for raw in cleaned[1:-1]:
                trimmed = raw.lstrip()
                if not trimmed:
                    continue
                if trimmed.startswith(panel_joint_chars):
                    continue
                segment = trimmed
                if segment[:1] in panel_vertical_chars:
                    segment = segment[1:]
                end_marker = False
                if segment.endswith(panel_vertical_chars):
                    segment = segment[:-1]
                    end_marker = True
                current += segment
                if end_marker:
                    candidate = current.rstrip()
                    if candidate:
                        rows_joined.append(candidate)
                    current = ""
            if current.rstrip():
                rows_joined.append(current.rstrip())
        else:
            rows_joined = [line.rstrip() for line in cleaned if line.strip()]

        parsed_rows: List[List[str]] = []
        for row in rows_joined:
            if not row:
                continue
            parts = None
            for separator in panel_vertical_chars:
                if separator in row:
                    parts = row.split(separator)
                    break
            if parts is None:
                parts = [row]
            parsed_rows.append([part.rstrip() for part in parts])

        if not parsed_rows:
            parsed_rows = [[line.strip()] for line in cleaned if line.strip()]

        title_text = ""
        body_rows: List[List[str]] = []
        for cells in parsed_rows:
            candidate = ""
            for cell in cells:
                stripped_cell = cell.strip()
                if stripped_cell:
                    candidate = stripped_cell
                    break
            if not title_text and candidate:
                title_text = candidate
                continue
            if any(cell.strip() for cell in cells):
                body_rows.append(cells)

        classes: List[str] = ["panel"]
        title_lower = title_text.lower()
        if any(token in title_lower for token in ("edit", "diff", "patch")):
            classes.append("panel-diff")
        elif any(token in title_lower for token in ("shell", "command", "run ", "python", "bash")):
            classes.append("panel-command")
        elif any(token in title_lower for token in ("read", "write", "result", "files", "plan", "apply", "export")):
            classes.append("panel-info")

        html_parts: List[str] = [f'<div class="{" ".join(classes)}">']
        if title_text:
            html_parts.append(f'<div class="panel-title">{html.escape(title_text)}</div>')

        if body_rows:
            max_cols = max(len(row) for row in body_rows)
            use_grid = max_cols > 1
            html_parts.append('<div class="panel-body">')
            if use_grid:
                grid_class = f'panel-grid cols-{max_cols}' if max_cols <= 4 else "panel-grid cols-auto"
                html_parts.append(f'<div class="{grid_class}">')
                for row in body_rows:
                    padded = row + [""] * (max_cols - len(row))
                    if not any(cell.strip() for cell in padded):
                        continue
                    html_parts.append('<div class="panel-row">')
                    for idx_cell, cell in enumerate(padded):
                        text = cell.rstrip()
                        if idx_cell > 0:
                            text = text.lstrip()
                        cell_html = html.escape(text) if text else "&nbsp;"
                        html_parts.append(f'<div class="panel-cell">{cell_html}</div>')
                    html_parts.append("</div>")
                html_parts.append("</div>")
            else:
                is_code_panel = "panel-diff" in classes or any(
                    row and row[0].lstrip(" 0123456789").startswith(("+", "-"))
                    for row in body_rows
                )

                if is_code_panel:
                    code_lines: list[str] = []
                    for row in body_rows:
                        text = row[0].rstrip()
                        if not text.strip():
                            code_lines.append("")
                            continue
                        trimmed_numeric = text.lstrip(" 0123456789")
                        if trimmed_numeric.startswith(("+", "-")):
                            num_prefix = text[:len(text) - len(trimmed_numeric)]
                            display_text = num_prefix + trimmed_numeric[1:]
                        else:
                            display_text = text
                        code_lines.append(display_text)

                    code_block = "\n".join(code_lines)
                    html_parts.append(f'<pre><code>{html.escape(code_block)}</code></pre>')
                else:
                    for row in body_rows:
                        text = row[0].rstrip()
                        if not text.strip():
                            continue
                        html_parts.append(f'<div class="panel-line">{html.escape(text)}</div>')
            html_parts.append("</div>")
        html_parts.append("</div>")
        return "\n".join(html_parts)

    def consume_panel(start: int) -> tuple[str, int]:
        box: List[str] = [lines[start]]
        idx = start + 1
        while idx < total:
            box.append(lines[idx])
            if strip_ansi(lines[idx]).lstrip().startswith(panel_bottom_chars):
                idx += 1
                break
            idx += 1
        return render_panel(box), idx

    def render_user(block: List[str]) -> str:
        if not block:
            return ""
        segments: List[str] = []
        for idx, raw in enumerate(block):
            text = strip_ansi(raw)
            if idx == 0:
                text = text.lstrip()
                if text.startswith(">"):
                    text = text[1:].lstrip()
            else:
                text = text.strip()
            segments.append(text)
        while segments and not segments[-1].strip():
            segments.pop()
        if not segments:
            return ""
        escaped = [html.escape(seg) if seg else "&nbsp;" for seg in segments]
        first = escaped[0]
        rest = escaped[1:]
        body = first if not rest else f"{first}<br/>" + "<br/>".join(rest)
        return f'<div class="user-qa"><span class="lead">&gt;</span>{body}</div>'

    def render_thought(block: List[str]) -> str:
        if not block:
            return ""
        cleaned: List[str] = []
        for idx, raw in enumerate(block):
            text = strip_ansi(raw)
            if idx == 0:
                text = text.lstrip()
                if text and text[0] in ("✦", "•"):
                    text = text[1:].lstrip()
            else:
                text = text.strip()
            cleaned.append(text)
        while cleaned and not cleaned[-1].strip():
            cleaned.pop()
        if not cleaned:
            return ""
        escaped = [html.escape(seg) if seg else "&nbsp;" for seg in cleaned]
        body = escaped[0] if len(escaped) == 1 else escaped[0] + "<br/>" + "<br/>".join(escaped[1:])
        return f'<div class="ia">✦ {body}</div>'

    while i < total:
        line = lines[i]
        raw_line = strip_ansi(line)

        if skipping_ascii_art:
            if not raw_line.strip():
                i += 1
                continue
            if all(ch in "░█▓▒▌▐▀▄─ " for ch in raw_line):
                i += 1
                continue
            if raw_line.strip().upper() == "GEMINI":
                i += 1
                continue
            skipping_ascii_art = False

        if is_fence(raw_line):
            out.append(raw_line)
            in_fence = not in_fence
            i += 1
            continue
        if in_fence:
            out.append(raw_line)
            i += 1
            continue

        if raw_line.lstrip().startswith(panel_top_chars):
            panel_html, i = consume_panel(i)
            out.append(panel_html)
            continue

        if not raw_line.strip():
            out.append("")
            i += 1
            continue

        if raw_line.lstrip().startswith(">"):
            block = [line]
            i += 1
            while i < total:
                nxt_raw = strip_ansi(lines[i])
                if not nxt_raw.strip():
                    block.append("")
                    i += 1
                    break
                if nxt_raw.lstrip().startswith(panel_top_chars + ("✦", "•", ">")):
                    break
                block.append(lines[i])
                i += 1
            out.append(render_user(block))
            continue

        if raw_line.lstrip().startswith(("✦", "•")):
            block = [line]
            i += 1
            while i < total:
                nxt_raw = strip_ansi(lines[i])
                if not nxt_raw.strip():
                    block.append("")
                    i += 1
                    break
                if nxt_raw.lstrip().startswith(panel_top_chars + ("✦", "•", ">")):
                    break
                block.append(lines[i])
                i += 1
            out.append(render_thought(block))
            continue

        if raw_line.startswith(("+", "-")) and not raw_line.startswith(("++", "--")):
            block = []
            while i < total:
                current = strip_ansi(lines[i])
                if not current.strip():
                    i += 1
                    break
                if current.startswith(("+", "-")) and not current.startswith(("++", "--")):
                    cleaned = current[1:]
                    block.append(cleaned)
                    i += 1
                else:
                    break
            while block and not block[-1].strip():
                block.pop()
            if block:
                out.append("```")
                out.extend(block)
                out.append("```")
            continue

        if looks_like_code_line(line):
            block = [strip_ansi(line)]
            i += 1
            while i < total:
                nxt = lines[i]
                nxt_raw = strip_ansi(nxt)
                if looks_like_code_line(nxt) or not nxt_raw.strip():
                    block.append(nxt_raw)
                    i += 1
                    continue
                break
            while block and not block[-1].strip():
                block.pop()
            if block:
                out.append("```")
                out.extend(block)
                out.append("```")
            continue

        out.append(raw_line)
        i += 1

    md = "\n".join(out).rstrip() + "\n"
    return md

# ---------- enriquecimiento específico para HTML (kotlin) ----------
_DIFF_FENCE_MARKERS = ("+", "-", "@@", "diff --", "index ", "---", "+++", "? ", "~ ")


def _highlight_diff_code_blocks(html_str: str) -> str:
    def _classify(line: str) -> str | None:
        trimmed = line.lstrip()
        if not trimmed:
            return "blank"
        idx = 0
        while idx < len(trimmed) and trimmed[idx].isdigit():
            idx += 1
        remainder = trimmed[idx:].lstrip()
        if not remainder:
            return "blank"
        if remainder.startswith("+"):
            return "add"
        if remainder.startswith("-"):
            return "del"
        if remainder.startswith(_DIFF_FENCE_MARKERS[2:]):
            return "meta"
        return None

    def _decorate(attrs: str, body: str) -> str | None:
        if "code-kotlin" in attrs or "code-diff" in attrs:
            return None
        raw = html.unescape(body)
        if "\n" in raw:
            lines = raw.split("\n")
        else:
            lines = re.split(r' (?=\d+\s+[+\-]?)', raw)
        if not any(_classify(line) in {"add", "del", "meta"} for line in lines):
            return None
        decorated: list[str] = []
        for line in lines:
            kind = _classify(line)
            classes: list[str] = ["diff-line"]
            if kind == "add":
                classes.append("diff-add")
            elif kind == "del":
                classes.append("diff-del")
            elif kind == "meta":
                classes.append("diff-meta")
            elif kind == "blank":
                classes.append("diff-blank")
            working = line.rstrip("\r")
            num_match = re.match(r"\s*\d+\s*(.*)", working)
            if num_match:
                working = num_match.group(1)

            if kind in ("add", "del") and working and working[0] in ("+", "-"):
                working = working[1:]

            content = working
            content_html = html.escape(content, quote=False) if content else "&nbsp;"
            decorated.append(f'<span class="{" ".join(classes)}">{content_html}</span>')
        attrs_out = attrs
        if "class=" in attrs_out:
            attrs_out = re.sub(
                r'class="([^"]*)"',
                lambda m: f'class="{m.group(1)} code-diff"',
                attrs_out,
                count=1,
            )
        else:
            attrs_out += ' class="code-diff"'
        return "<code" + attrs_out + ">" + "\n".join(decorated) + "</code>"

    def _repl_block(match: re.Match[str]) -> str:
        attrs = match.group(1) or ""
        body = match.group(2)
        decorated = _decorate(attrs, body)
        if decorated is None:
            return match.group(0)
        return "<pre>" + decorated + "</pre>"

    def _repl_inline(match: re.Match[str]) -> str:
        attrs = match.group(1) or ""
        body = match.group(2)
        decorated = _decorate(attrs, body)
        if decorated is None:
            return match.group(0)
        return "<pre>" + decorated + "</pre>"

    html_str = re.sub(r"<pre><code([^>]*)>(.*?)</code></pre>", _repl_block, html_str, flags=re.S)
    return re.sub(r"<code([^>]*)>(.*?)</code>", _repl_inline, html_str, flags=re.S)


def _remove_line_numbers_from_code(html_str: str) -> str:
    """
    Extrae números de línea del código y los pone en spans no copiables.
    Procesa tanto texto plano como spans existentes.
    """
    def _process_code_block(match: re.Match[str]) -> str:
        tag_open = match.group(1)
        content = match.group(2)
        tag_close = match.group(3)

        if '<span' in content:
            content = re.sub(
                r'<span class="diff-line([^"]*)">\s*(\d+)\s+([+\-])?(.*?)</span>',
                lambda m: (
                    f'<span class="diff-line{m.group(1)}">'
                    f'<span class="line-num" style="user-select: none;">{m.group(2)} {m.group(3) or ""}</span>'
                    f'{m.group(4)}</span>'
                ),
                content
            )
        else:
            unescaped = html.unescape(content)
            lines = unescaped.split('\n')
            processed_lines: list[str] = []

            for line in lines:
                line_match = re.match(r'^(\s*)(\d+)\s+([+\-])?(.*)$', line)
                if line_match:
                    indent = line_match.group(1)
                    linenum = line_match.group(2)
                    marker = line_match.group(3) or ''
                    code = line_match.group(4)
                    processed_line = f'{indent}<span class="line-num" style="user-select: none;">{linenum} {marker}</span>{html.escape(code) if code else ""}'
                    processed_lines.append(processed_line)
                else:
                    processed_lines.append(html.escape(line))

            content = '\n'.join(processed_lines)

        return f'{tag_open}{content}{tag_close}'

    return re.sub(
        r'(<pre><code[^>]*>)(.*?)(</code></pre>)',
        _process_code_block,
        html_str,
        flags=re.S
    )

def postprocess_html_for_kotlin(html_str: str) -> str:
    """
    Dentro de <pre><code class="language-kotlin">...</code></pre>
    aplica coloreado básico mediante spans (kw, lit, type).
    """
    html_str = _highlight_diff_code_blocks(html_str)
    html_str = _remove_line_numbers_from_code(html_str)

    def _repl(m):
        inner = m.group(1)
        return '<pre><code class="language-kotlin code-kotlin">' + _colorize_kotlin(inner) + "</code></pre>"
    return re.sub(r'<pre><code class="language-kotlin">(.*?)</code></pre>', _repl, html_str, flags=re.S)

def gemini_css()->str:
    return GEMINI_CSS
