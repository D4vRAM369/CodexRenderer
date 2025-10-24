# -*- coding: utf-8 -*-
"""
Modo Gemini para CodexRenderer:
- Entrada: texto plano (export/log) o .odt (ya lo maneja el lector .odt del proyecto)
- Salida intermedia: Markdown "rico" (etiquetas HTML mínimas embebidas donde compensa)
- Salida final opcional: HTML con CSS Gemini (gradiente, cards, diff, callouts)
"""

from __future__ import annotations
from typing import List
import html

# ---------- COLORES / TEMA ----------
GEMINI_CSS = r"""
:root{
  --bg:#0b0c10;
  --fg:#dfe7ff;
  --muted:#a7b3d1;
  --ok:#87ff87;
  --warn:#ffd75f;
  --err:#ff6b6b;
  --accent1:#7aa2f7;  /* azul */
  --accent2:#bb9af7;  /* violeta */
  --accent3:#2ac3de;  /* cian */
  --box:#11131a;
  --box-border:#1b2030;
  --code-bg:#0f1320;
}
html,body{
  background:var(--bg);
  color:var(--fg);
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace;
  line-height:1.65; margin:0; padding:2rem 1.25rem 4rem;
}
a{ color:var(--accent3); text-decoration:none; border-bottom:1px dotted var(--accent3); }
a:hover{ color:var(--accent2); border-bottom-color:var(--accent2); }

h1,h2,h3{ color:var(--accent2); letter-spacing:0.3px; }
pre, code{ background:var(--code-bg); color:var(--fg); }
pre{ padding:0.9rem 1rem; border-radius:12px; overflow:auto; border:1px solid #1e2438; }

.banner{
  width:100%; margin:0 0 1rem; padding:0.8rem 0 1.2rem;
  background:linear-gradient(90deg, #7aa2f7 0%, #bb9af7 50%, #2ac3de 100%);
  -webkit-background-clip:text; background-clip:text; color:transparent;
  font-weight:800; font-size:56px; line-height:0.9; letter-spacing:2px;
  text-shadow:0 0 14px rgba(42,195,222,.15);
  user-select:none;
}

.callout{
  background:var(--box); border:1px solid var(--box-border);
  border-left:4px solid var(--accent3);
  padding:1rem 1rem; border-radius:10px; margin:1rem 0;
}
.card{
  background:var(--box); border:1px solid var(--box-border);
  padding:0.6rem 0.9rem; border-radius:10px; margin:1rem 0;
}
.card .title{
  font-weight:700; color:var(--accent1); margin-bottom:0.4rem;
}
.badge{
  display:inline-block; font-size:12px; padding:2px 8px; border-radius:999px;
  border:1px solid var(--box-border); background:rgba(122,162,247,.1); color:var(--accent1);
  margin-right:6px;
}
.diff{ border-radius:8px; overflow:hidden; border:1px solid #2a314a; }
.diff .add{ background:#0f1b12; color:#b4f7b4; }
.diff .del{ background:#1b1111; color:#f7b4b4; }
.diff .line{ padding:2px 10px; white-space:pre-wrap; font-family:inherit; }
.ia{ color:#c9b6ff; }            /* razonamiento Gemini */
.user-qa{ font-weight:700; color:#ffea70; }  /* > tus líneas */
.code-kotlin .kw{ color:#7aa2f7; font-weight:700; }   /* var, by, fun... */
.code-kotlin .lit{ color:#2ac3de; }                   /* null, true, false */
.code-kotlin .type{ color:#bb9af7; }                  /* String, Int... */
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

# ---------- Transformación de texto -> Markdown con “componentes” Gemini ----------
def to_markdown_gemini(src:str, title:str="GEMINI")->str:
    """
    Reglas:
      - Inserta banner “GEMINI” (HTML) al inicio (en MD se permite HTML crudo).
      - Líneas de usuario que empiezan por '> ' -> <span class="user-qa">...</span>
      - Bloques con encabezado 'Edit ', 'WriteFile ', 'ReadManyFiles ' -> .card con .title
      - Rachas + / - contiguas -> bloque .diff con .add/.del
      - Viñetas de razonamiento con '✦' o '•' -> <span class="ia">...</span>
      - Respeta bloques ```lang existentes; añade coloreado HTML simple para kotlin si pedimos HTML luego.
    """
    out: List[str] = []
    out.append(f'<div class="banner">{html.escape(title)}</div>')
    lines = src.splitlines()
    i=0
    in_code=False

    def is_fence(s:str)->bool:
        return s.strip().startswith("```")

    while i < len(lines):
        ln = lines[i]

        # cercas
        if is_fence(ln):
            out.append(ln)
            in_code = not in_code
            i+=1
            continue
        if in_code:
            out.append(ln)
            i+=1; continue

        # usuario
        if ln.startswith(">"):
            content = ln[1:].lstrip()
            out.append(f'<div class="user-qa">&gt; {html.escape(content)}</div>')
            i+=1; continue

        # tarjetas conocidas
        if ln.startswith(("Edit ", "WriteFile ", "ReadManyFiles ")):
            title = html.escape(ln.strip())
            out.append(f'<div class="card"><div class="title">{title}</div>')
            i+=1
            # acumula hasta línea en blanco o otra tarjeta
            block=[]
            while i<len(lines) and lines[i].strip()!="" and not lines[i].startswith(("Edit ","WriteFile ","ReadManyFiles ")):
                block.append(lines[i]); i+=1
            # deja el contenido como código “markdown” para preservar sangría
            body = "\n".join(block)
            out.append("\n\n```\n" + body + "\n```\n</div>")
            continue

        # diff (+/-) contiguo
        if ln.startswith(("+","-")) and not ln.startswith(("+++", "---")):
            adds=[]; dels=[]; chunk=[]
            while i<len(lines) and lines[i].startswith(("+","-")) and not lines[i].startswith(("+++", "---")):
                chunk.append(lines[i]); i+=1
            out.append('<div class="diff">')
            for c in chunk:
                cls = "add" if c.startswith("+") else "del"
                out.append(f'<div class="line {cls}">{html.escape(c)}</div>')
            out.append("</div>")
            continue

        # razonamiento
        if ln.strip().startswith(("✦","•")):
            out.append(f'<div class="ia">{html.escape(ln)}</div>')
            i+=1; continue

        out.append(ln)
        i+=1

    md = "\n".join(out).rstrip()+"\n"
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

