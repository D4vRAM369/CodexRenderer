# -*- coding: utf-8 -*-
"""
Tema Claude-Code para CodexRenderer.

Se apoya en la lógica de parsing del modo Gemini, pero ajusta la estética:
- Paleta oscuro-vainilla con acentos naranja brûlée.
- Preguntas del usuario resaltadas en ámbar (como `> prompt` en Claude).
- Banner con icono de estrella blanca y degradados cálidos.
"""
from __future__ import annotations

import html as _html
import re

from . import gemini


CLAUDE_CSS = r"""
:root {
  --bg: #0f131a;
  --bg-alt: #171d26;
  --fg: #f7f4ec;
  --muted: #d2c6bb;
  --accent: #ff9d5c;
  --accent-strong: #ff7c3f;
  --panel-bg: #1b2532;
  --panel-border: rgba(255, 157, 92, 0.28);
  --panel-shadow: rgba(10, 7, 3, 0.55);
  --code-bg: rgba(255, 157, 92, 0.09);
  --code-border: rgba(255, 157, 92, 0.32);
  --amber: #f5c164;
  --amber-strong: #facc6b;
  --diff-add-bg: rgba(110, 198, 152, 0.22);
  --diff-add-fg: #dbffe8;
  --diff-del-bg: rgba(255, 125, 125, 0.23);
  --diff-del-fg: #ffe1e1;
}
*, *::before, *::after {
  box-sizing: border-box;
}
html, body {
  background: radial-gradient(circle at top left, rgba(255,147,92,0.08) 0%, transparent 45%) var(--bg);
  color: var(--fg);
  font-family: 'JetBrains Mono', 'Fira Code', 'SFMono-Regular', Menlo, Consolas, 'Liberation Mono', monospace;
  line-height: 1.62;
  width: 100%;
  max-width: none;
  min-height: 100%;
  margin: 0;
  padding: 2.2rem 1.8rem 4rem;
}
body {
  max-width: none;
  width: 100%;
  margin: 0;
}
a {
  color: var(--accent);
  text-decoration: none;
  border-bottom: 1px dotted rgba(255, 157, 92, 0.5);
}
a:hover {
  color: var(--accent-strong);
  border-bottom-color: rgba(255, 157, 92, 0.9);
}
p { margin: 0 0 1rem; }
ul, ol { margin: 0 0 1rem 1.4rem; }
li { margin-bottom: 0.35rem; }
hr {
  border: none;
  border-top: 1px solid rgba(255, 157, 92, 0.18);
  margin: 2.2rem 0;
}
pre, code {
  background: var(--code-bg);
  color: var(--fg);
  border-radius: 10px;
}
pre {
  padding: 1rem 1.1rem;
  overflow: auto;
  border: 1px solid var(--code-border);
  box-shadow: inset 0 0 0 1px rgba(255, 157, 92, 0.18);
}
code {
  padding: 0.18rem 0.45rem;
  border: 1px solid rgba(255, 199, 143, 0.35);
  box-shadow: inset 0 0 0 1px rgba(255, 157, 92, 0.12);
}
.banner {
  display: inline-flex;
  align-items: center;
  gap: 1.4rem;
  margin: -0.5rem 0 2.1rem;
  padding: 0.4rem 1.6rem 0.6rem 0.6rem;
  border-radius: 16px;
  background: linear-gradient(135deg, rgba(255,147,92,0.25) 0%, rgba(23,29,38,0.05) 100%);
  box-shadow: 0 22px 48px rgba(8, 6, 4, 0.35);
  font-size: 48px;
  font-weight: 900;
  letter-spacing: 1.2px;
  color: transparent;
  background-clip: text;
  -webkit-background-clip: text;
  background-image: linear-gradient(90deg, #ffe0bd 0%, #ffc38f 60%, #ff995d 100%);
  position: relative;
}
.banner::before {
  content: "";
  flex: 0 0 72px;
  height: 72px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.95) 0%, rgba(255, 255, 255, 0.7) 45%, rgba(255, 255, 255, 0.1) 80%, transparent 100%);
  mask: url("data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMjAgMTIwIj48cG9seWdvbiBmaWxsPSIjRkZGRkZGIiBwb2ludHM9IjYwLDUgNzMsNDIgMTEyLDQ1IDgxLDY5IDkyLDEwOCA2MCw4NiAyOCwxMDggMzksNjkgOCw0NSA0Nyw0MiIvPjwvc3ZnPg==") center/64px 64px no-repeat;
  -webkit-mask: url("data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMjAgMTIwIj48cG9seWdvbiBmaWxsPSIjRkZGRkZGIiBwb2ludHM9IjYwLDUgNzMsNDIgMTEyLDQ1IDgxLDY5IDkyLDEwOCA2MCw4NiAyOCwxMDggMzksNjkgOCw0NSA0Nyw0MiIvPjwvc3ZnPg==") center/64px 64px no-repeat;
  background-color: #ffffff;
  box-shadow: 0 12px 30px rgba(255, 195, 143, 0.45);
}
.user-qa {
  margin: 1.6rem 0;
  padding: 1.05rem 1.3rem;
  border-radius: 14px;
  background: rgba(245, 193, 100, 0.12);
  border: 1px solid rgba(245, 193, 100, 0.35);
  border-left: 5px solid var(--amber);
  font-weight: 650;
  color: var(--amber-strong);
  box-shadow: 0 18px 36px rgba(8, 6, 4, 0.32);
}
.user-qa .lead {
  color: var(--amber-strong);
  margin-right: 0.75rem;
  font-weight: 800;
  text-shadow: 0 0 18px rgba(250, 204, 107, 0.55);
}
.claude-meta {
  display: inline-flex;
  align-items: center;
  gap: 1.35rem;
  margin: 1.2rem 0 2.4rem;
  padding: 0.9rem 1.5rem 1rem 1.2rem;
  border-radius: 18px;
  background: linear-gradient(135deg, rgba(255, 157, 92, 0.22), rgba(15, 19, 26, 0.85));
  border: 1px solid rgba(255, 157, 92, 0.32);
  box-shadow: 0 28px 54px rgba(8, 6, 4, 0.45);
}
.claude-meta-star {
  flex: 0 0 72px;
  height: 72px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 34px;
  font-weight: 800;
  color: #1a120a;
  background: radial-gradient(circle at 30% 30%, #fff3df 0%, #ffd7ad 55%, #ff995d 100%);
  box-shadow: 0 16px 32px rgba(255, 195, 143, 0.55);
  text-shadow: 0 0 18px rgba(255, 130, 70, 0.55);
}
.claude-meta-body {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  font-size: 1.04rem;
}
.claude-meta-line {
  color: var(--muted);
  letter-spacing: 0.03em;
}
.claude-meta-line:first-child {
  color: var(--fg);
  font-weight: 700;
  letter-spacing: 0.04em;
}
.claude-meta-line:nth-child(2) {
  color: var(--accent);
  font-weight: 600;
}
.ia {
  margin: 1.4rem 0;
  color: #f0e6d7;
  font-style: italic;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 10px;
  padding: 0.75rem 1rem;
  border-left: 3px solid rgba(255, 157, 92, 0.4);
}
.panel {
  background: var(--panel-bg);
  border: 1px solid var(--panel-border);
  border-radius: 14px;
  margin: 1.75rem 0;
  box-shadow: 0 20px 46px var(--panel-shadow);
  overflow: hidden;
}
.panel-title {
  padding: 1rem 1.2rem 0.55rem;
  font-weight: 720;
  color: var(--accent);
  letter-spacing: 0.4px;
  text-transform: uppercase;
}
.panel-command .panel-title { color: #f5a879; }
.panel-info .panel-title { color: #ffc38f; }
.panel-diff .panel-title { color: #f6b6a3; }
.panel-body {
  padding: 0.45rem 1.25rem 1.25rem;
}
.panel-line {
  white-space: pre;
  font-family: inherit;
  padding: 0.45rem 0.9rem;
  border-radius: 8px;
  margin: 0.15rem 0;
  line-height: 1.5;
  background: rgba(12, 15, 22, 0.25);
  border: 1px solid rgba(255, 157, 92, 0.12);
  color: var(--fg);
  overflow-x: auto;
}
.panel-grid {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin: 0.5rem 0;
}
.panel-grid .panel-row {
  display: grid;
  gap: 0.6rem;
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
  padding: 0.55rem 0.8rem;
  border-radius: 10px;
  border: 1px solid rgba(255, 157, 92, 0.22);
  background: rgba(20, 24, 33, 0.55);
  white-space: pre;
  font-family: inherit;
  color: var(--fg);
  box-shadow: inset 0 0 0 1px rgba(255, 157, 92, 0.14);
}
pre code.code-diff {
  display: block;
  background: rgba(12, 15, 22, 0.55);
  border: 1px solid rgba(255, 157, 92, 0.22);
  border-radius: 14px;
  padding: 0.5rem 0.4rem;
  margin: 1.6rem 0;
  box-shadow: inset 0 0 0 1px rgba(255, 157, 92, 0.12);
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
  background: rgba(245, 193, 100, 0.16);
  color: var(--amber-strong);
  font-style: italic;
}
pre code.code-diff .diff-blank {
  min-height: 0.45rem;
  padding-top: 0.25rem;
  padding-bottom: 0.25rem;
}
.panel-line.diff-add {
  background: var(--diff-add-bg);
  color: var(--diff-add-fg);
}
.panel-line.diff-del {
  background: var(--diff-del-bg);
  color: var(--diff-del-fg);
}
.panel-line.diff-meta {
  background: rgba(245, 193, 100, 0.12);
  color: var(--amber);
  font-style: italic;
}
blockquote {
  border-left: 4px solid rgba(255, 157, 92, 0.45);
  background: rgba(23, 29, 38, 0.66);
  padding: 0.9rem 1.3rem;
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
  border: 1px solid rgba(255, 157, 92, 0.24);
  padding: 0.6rem 0.85rem;
}
th {
  background: rgba(255, 157, 92, 0.18);
  color: var(--accent-strong);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}
"""


def claude_css() -> str:
    """Devuelve la hoja de estilos Claude-Code."""
    return CLAUDE_CSS


_META_SEP = re.compile(r"\s{2,}")
_META_MARK = re.compile(r"[▐▛▜▝▘▞▟▙]")


def _looks_like_meta_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped or stripped.startswith("<"):
        return False
    return bool(
        _META_MARK.search(stripped)
        or stripped.startswith("Claude Code v")
        or stripped.startswith("Sonnet ")
    )


def _extract_meta_body(block: list[str]) -> list[str] | None:
    values: list[str] = []
    has_mark = False
    for raw in block:
        stripped = raw.strip()
        if not stripped:
            continue
        if _META_MARK.search(stripped):
            has_mark = True
        parts = _META_SEP.split(stripped)
        if len(parts) >= 2:
            candidate = parts[-1]
        else:
            candidate = stripped
        if candidate:
            values.append(candidate)
    if not values:
        return None
    if not has_mark and len(values) < 2:
        return None
    return values


def _render_meta(values: list[str]) -> str:
    lines = "\n".join(f'    <div class="claude-meta-line">{_html.escape(val)}</div>' for val in values)
    return (
        '<div class="claude-meta">\n'
        '  <div class="claude-meta-star">✶</div>\n'
        '  <div class="claude-meta-body">\n'
        f"{lines}\n"
        "  </div>\n"
        "</div>"
    )


def to_markdown_claude(src: str, title: str = "CLAUDE·CODE") -> str:
    """
    Reutiliza el parser Gemini pero cambiando el título del banner.
    """
    raw_md = gemini.to_markdown_gemini(src, title=title)
    lines = raw_md.splitlines()
    out: list[str] = []
    i = 0
    in_fence = False
    total = len(lines)

    meta_done = False

    while i < total:
        line = lines[i]
        stripped = line.strip()
        if stripped.startswith("```"):
            out.append(line)
            in_fence = not in_fence
            i += 1
            continue
        if in_fence:
            out.append(line)
            i += 1
            continue
        if _looks_like_meta_line(line):
            block: list[str] = []
            start = i
            while i < total and _looks_like_meta_line(lines[i]):
                block.append(lines[i])
                i += 1
            meta_vals = _extract_meta_body(block) if not meta_done else None
            if meta_vals:
                out.append(_render_meta(meta_vals))
                meta_done = True
                continue
            out.extend(block)
            continue
        out.append(line)
        i += 1

    return "\n".join(out)


def postprocess_html(html_str: str) -> str:
    """
    Aplica el post-procesado gemini (resaltado Kotlin simple) para reutilizar lógica existente.
    """
    return gemini.postprocess_html_for_kotlin(html_str)


__all__ = ["claude_css", "to_markdown_claude", "postprocess_html"]
