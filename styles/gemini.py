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
}
.panel-line:first-child { margin-top: 0; }
.panel-line:last-child { margin-bottom: 0; }
.panel-line.empty {
  min-height: 0.9rem;
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
  width: 100%;
  border-collapse: collapse;
  margin: 1.5rem 0;
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
        cleaned = [strip_ansi(line) for line in box_lines]
        if len(cleaned) >= 2 and cleaned[0].startswith(("╭", "┌")) and cleaned[-1].startswith(("╰", "└")):
            rows: List[str] = []
            buffer = ""
            for raw in cleaned[1:-1]:
                segment = raw
                if segment.startswith("│"):
                    segment = segment[1:]
                if segment.endswith("│"):
                    segment = segment[:-1]
                    buffer += segment
                    candidate = buffer.rstrip()
                    if candidate:
                        rows.append(candidate)
                    buffer = ""
                else:
                    if segment.strip():
                        buffer += segment + " "
                    else:
                        if buffer:
                            rows.append(buffer.rstrip())
                            buffer = ""
            if buffer.rstrip():
                rows.append(buffer.rstrip())
            inner = rows
        else:
            inner = cleaned

        title_text = ""
        body_lines: List[str] = []
        for entry in inner:
            if not title_text:
                if entry.strip():
                    title_text = entry.strip()
                continue
            if not body_lines and entry.strip() == "":
                continue
            body_lines.append(entry)

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
        if body_lines:
            html_parts.append('<div class="panel-body">')
            for raw in body_lines:
                raw_clean = strip_ansi(raw.rstrip())
                if not raw_clean.strip():
                    continue
                trimmed_numeric = raw_clean.lstrip(" 0123456789")
                line_cls = "panel-line"
                if trimmed_numeric.startswith("+"):
                    line_cls += " diff-add"
                elif trimmed_numeric.startswith("-"):
                    if "panel-command" in classes and trimmed_numeric.startswith("- "):
                        line_cls += " cmd"
                    else:
                        line_cls += " diff-del"
                elif trimmed_numeric.startswith("@@") or trimmed_numeric.startswith("diff --") or trimmed_numeric.startswith("index "):
                    line_cls += " diff-meta"
                elif trimmed_numeric.startswith(("---", "+++", "? ", "~ ")):
                    line_cls += " diff-meta"
                html_parts.append(f'<div class="{line_cls}">{html.escape(raw_clean)}</div>')
            html_parts.append("</div>")
        html_parts.append("</div>")
        return "\n".join(html_parts)

    def consume_panel(start: int) -> tuple[str, int]:
        box: List[str] = [lines[start]]
        idx = start + 1
        while idx < total:
            box.append(lines[idx])
            if lines[idx].startswith(("╰", "└")):
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

        if raw_line.startswith(("╭", "┌")):
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
                if nxt_raw.lstrip().startswith(("╭", "┌", "✦", "•", ">")):
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
                if nxt_raw.lstrip().startswith(("╭", "┌", "✦", "•", ">")):
                    break
                block.append(lines[i])
                i += 1
            out.append(render_thought(block))
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
def postprocess_html_for_kotlin(html_str:str)->str:
    """
    Dentro de <pre><code class="language-kotlin">...</code></pre>
    aplica coloreado básico mediante spans (kw, lit, type).
    """
    def _repl(m):
        inner = m.group(1)
        return '<pre><code class="language-kotlin code-kotlin">' + _colorize_kotlin(inner) + "</code></pre>"
    return re.sub(r'<pre><code class="language-kotlin">(.*?)</code></pre>', _repl, html_str, flags=re.S)

def gemini_css()->str:
    return GEMINI_CSS
