#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse, os, re
from typing import List

# ------------------- Lectura -------------------
def read_text_input(path: str) -> List[str]:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read().splitlines()

def read_odt_input(path: str) -> List[str]:
    try:
        from odf.opendocument import load
        from odf import text
    except Exception as e:
        raise RuntimeError("Instala odfpy:  pip install odfpy") from e
    doc = load(path)
    lines: List[str] = []
    for p in doc.getElementsByType(text.P):
        frag = "".join(
            node.data if hasattr(node, "data") else
            (node.firstChild.data if hasattr(node, "firstChild") and hasattr(node.firstChild, "data") else "")
            for node in p.childNodes
        )
        lines.extend(frag.splitlines() or [""])
    return lines

# ------------------- Heurísticas -------------------
CODE_KWS = {
    "kotlin":[r"\bfun\b", r"\bdata\s+class\b", r"\bval\b", r"\bvar\b", r"import\s+android", r"Coroutine", r"@Composable"],
    "java":[r"\bpublic\b", r"\bclass\b", r"\bstatic\b", r"\bvoid\b", r";\s*$", r"System\.out\.print"],
    "python":[r"^def\s", r"^class\s", r":\s*$", r"\bimport\b", r"\basync\b", r"\bawait\b"],
    "bash":[r"^#!/usr/bin/env\s+bash", r"\b#!/bin/bash", r"\bset -e", r"\bgrep\b", r"\bawk\b", r"\btar\b", r"\badb\b"],
    "json":[r"^\s*\{", r"\}\s*$", r'"\w+"\s*:'],
    "xml":[r"^\s*<\?xml", r"^\s*<[\w\-]+", r"</[\w\-]+>\s*$"],
}

PROMPT_CHARS = r"[>\u203A\u00BB]"   # >  ›  »

def guess_language(lines: List[str]) -> str:
    scores = {k:0 for k in CODE_KWS}
    for ln in lines[:min(80, len(lines))]:
        for lang,pats in CODE_KWS.items():
            for pat in pats:
                if re.search(pat, ln):
                    scores[lang]+=1
    lang = max(scores, key=scores.get)
    return lang if scores[lang] > 0 else ""

def looks_like_code(line: str) -> bool:
    if line.strip().startswith("```"): return True
    if re.match(r"^\s{4,}\S", line): return True
    if any(t in line for t in ["package ", "import ", "@Composable", "class ", "fun ", "val ", "var ", "#!/"]): return True
    if sum(line.count(t) for t in ["{","}",";","(",")"]) >= 2: return True
    return False

def is_ai_thought(line: str) -> bool:
    return bool(re.match(r"^\s*[•\-\*\u2022]\s+", line))

def is_question(line: str) -> bool:
    if re.match(r"^\s*\?\s+", line): return True
    return bool(re.match(rf"^\s*{PROMPT_CHARS}\s*PNL(?:[:\-]\s+|\s+)", line, flags=re.IGNORECASE))

def is_prompt(line: str) -> bool:
    return bool(re.match(rf"^\s*{PROMPT_CHARS}\s+(?!PNL\b)", line, flags=re.IGNORECASE))

# ------------------- Utilidades -------------------
def escape_html(s: str) -> str:
    return (s.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;"))

def escape_md(s: str) -> str:
    if re.match(r"^\s*#{1,6}\s+\S", s): return "\\" + s
    return s

def visible_arrow(sym: str) -> str:
    # Devuelve la flecha visible apropiada para HTML
    return "&gt;" if sym == ">" else sym

# ------------------- Conversión -------------------
def convert_lines_to_markdown(lines: List[str], inline_css: bool) -> str:
    out: List[str] = []
    if inline_css:
        out.append(
            "<style>\n"
            "body{background:#0b0b0b;color:#ddd;font-family:'JetBrains Mono','Fira Code',monospace;}\n"
            "a{color:#8ab4f8}\n"
            ".term{background:#000;padding:12px;border-radius:8px;overflow:auto}\n"
            ".term code{background:transparent;color:#ddd}\n"
            ".ait{color:#00c853;font-style:italic}\n"
            ".q{color:#80d8ff;font-weight:600}\n"
            ".prompt{color:#ffd54f;font-weight:600}\n"
            "pre code{font-family:'JetBrains Mono','Fira Code',monospace;font-size:0.95rem}\n"
            "</style>\n"
        )

    i, n = 0, len(lines)
    inside_backticks = False

    while i < n:
        line = lines[i]

        # Respetar fences existentes
        if line.strip().startswith("```"):
            out.append(line); inside_backticks = not inside_backticks; i += 1; continue
        if inside_backticks:
            out.append(line); i += 1; continue

        # Bloques diff
        if re.match(r"^[+-](?![+-])", line):
            block = []
            while i < n and (re.match(r"^[+-](?![+-])", lines[i]) or lines[i].strip() == ""):
                block.append(lines[i]); i += 1
            code = "\n".join(block)
            if inline_css: out.append('<pre class="term"><code>')
            out.append(f"```diff\n{code}\n```")
            if inline_css: out.append("</code></pre>")
            continue

        # Pensamiento IA (verde cursiva) — agrupa párrafo
        if is_ai_thought(line):
            text = re.sub(r"^\s*[•\-\*\u2022]\s*", "", line).strip()
            j = i + 1; extra = []
            while j < n and lines[j].strip() and \
                  not re.match(r"^[+-](?![+-])", lines[j]) and \
                  not looks_like_code(lines[j]) and \
                  not is_question(lines[j]) and \
                  not is_prompt(lines[j]):
                extra.append(lines[j].strip()); j += 1
            if extra: text += " " + " ".join(extra); i = j
            else: i += 1
            out.append(f'<span class="ait"><em>{escape_html(text)}</em></span>')
            continue

        # Pregunta: "? …"
        m_q = re.match(r"^\s*(\?)\s+(.*)$", line)
        if m_q:
            sym, txt = m_q.group(1), m_q.group(2).strip()
            out.append(f'<span class="q">{escape_html(sym+" "+txt)}</span>')
            i += 1
            continue

        # Pregunta: "> PNL …" / "› PNL …" / "» PNL …"
        m_pnl = re.match(rf"^\s*({PROMPT_CHARS})\s*PNL(?:[:\-]\s+|\s+)(.*)$", line, flags=re.IGNORECASE)
        if m_pnl:
            sym, txt = m_pnl.group(1), m_pnl.group(2).strip()
            out.append(f'<span class="q">{visible_arrow(sym)} {escape_html(txt)}</span>')
            i += 1
            continue

        # Prompts genéricos: "> …" / "› …" / "» …" (NO PNL)
        if is_prompt(line):
            # Emite cada línea prompt por separado para mantener el "ritmo" original
            while i < n and is_prompt(lines[i]):
                m = re.match(rf"^\s*({PROMPT_CHARS})\s+(.*)$", lines[i], flags=re.IGNORECASE)
                if m:
                    sym, txt = m.group(1), m.group(2).strip()
                    out.append(f'<span class="prompt">{visible_arrow(sym)} {escape_html(txt)}</span>')
                else:
                    out.append(escape_md(lines[i]))
                i += 1
            continue

        # Bloque de código por heurística
        if looks_like_code(line):
            block = [line]; j = i + 1
            while j < n and looks_like_code(lines[j]) and not lines[j].strip().startswith("```"):
                block.append(lines[j]); j += 1
            lang = guess_language(block)
            code = "\n".join(block)
            if inline_css: out.append('<pre class="term"><code>')
            out.append(f"```{lang}\n{code}\n```")
            if inline_css: out.append("</code></pre>")
            i = j
            continue

        # Texto normal
        out.append(escape_md(line)); i += 1

    import re as _re
    md = "\n".join(out)
    md = _re.sub(r"\n{3,}", "\n\n", md)
    return md.strip() + "\n"

# ------------------- CLI -------------------
def main():
    ap = argparse.ArgumentParser(description="Convierte .txt/.odt a Markdown con estilo terminal.")
    ap.add_argument("input_path")
    ap.add_argument("-o","--output")
    ap.add_argument("--inline-css", action="store_true", help="Estilo oscuro tipo Alacritty incrustado")
    args = ap.parse_args()

    in_path = args.input_path
    if not os.path.isfile(in_path): raise SystemExit(f"No existe: {in_path}")

    ext = os.path.splitext(in_path)[1].lower()
    if ext == ".txt":
        lines = read_text_input(in_path)
    elif ext == ".odt":
        lines = read_odt_input(in_path)
    else:
        raise SystemExit("Soportado: .txt, .odt")

    md = convert_lines_to_markdown(lines, args.inline_css)
    out = args.output or os.path.splitext(in_path)[0] + ".md"
    with open(out, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"OK -> {out}")

if __name__ == "__main__":
    main()

