#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

# -------------------- IMPORTS BÁSICOS --------------------
import os
import sys
import html
import shutil
import subprocess
import threading
from pathlib import Path
from typing import List, Optional
import argparse  # <-- para --version / --debug

# CodexRenderer GUI — ODT/TXT -> Markdown -> HTML con tema Alacritty/Codex (drag & drop)
# Requisitos:
#   - Python 3.10+
#   - odfpy (para .odt):  pip install odfpy
#   - pandoc (sistema):   sudo apt install -y pandoc
#   - (Opcional) tkinterdnd2 para drag&drop nativo: pip install tkinterdnd2

__version__ = "0.1.0"

# -------------------- TEMA CSS (EMBEBIDO) --------------------
CODEX_CSS = r"""
:root {
  --bg: #050a05;
  --fg: #c2ffc2;
  --dim: #8aff8a;
  --accent: #00ff66;
  --muted: #6bd96b;
  --warning: #ffb86c;
  --red: #ff5555;
  --green: #4dff88;
}
html, body {
  background: var(--bg);
  color: var(--fg);
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace;
  line-height: 1.6; margin: 0; padding: 2rem 1.5rem 4rem;
}
h1, h2, h3 {
  color: var(--accent);
  text-shadow: 0 0 12px rgba(0,255,102,0.45);
  letter-spacing: 0.5px;
}
a { color: var(--dim); text-decoration: none; border-bottom: 1px dotted var(--muted); }
a:hover { color: var(--accent); border-bottom-color: var(--accent); }
pre, code {
  background: rgba(0, 255, 80, 0.06);
  color: var(--fg);
}
pre {
  padding: 0.9rem 1rem; border-radius: 10px; overflow-x: auto;
  box-shadow: inset 0 0 22px rgba(0,255,80,0.1);
  border: 1px solid rgba(0,255,120,0.18);
}
table { border-collapse: collapse; width: 100%; }
th, td { border: 1px solid rgba(0,255,120,0.12); padding: .5rem .65rem; }
th { background: rgba(0,255,80,0.08); }
.ia-thought { color: var(--muted); font-style: italic; }
body::before {
  content: ""; position: fixed; inset: 0;
  background-image:
    radial-gradient(transparent 60%, rgba(0,255,120,0.06)),
    repeating-linear-gradient(to bottom, rgba(0,255,120,0.08) 0 2px, transparent 2px 30px);
  opacity: 0.18; pointer-events: none;
}
"""

# -------------------- CONVERSIÓN BASE --------------------
def read_plain_txt(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")

def read_odt(p: Path) -> str:
    """
    Extrae texto legible de un .odt (LibreOffice).
    - Usa odfpy y teletype para respetar saltos básicos.
    - Soporta P, H, ListItem; si falla, hace fallback al body completo.
    """
    from odf.opendocument import load
    from odf.text import P, H, ListItem
    from odf import teletype

    doc = load(str(p))
    pieces: list[str] = []

    # 1) Recorre cabeceras, párrafos e items de lista
    for el in (doc.getElementsByType(H) +
               doc.getElementsByType(P) +
               doc.getElementsByType(ListItem)):
        txt = teletype.extractText(el) or ""
        txt = txt.strip()
        if txt:
            pieces.append(txt)

    # 2) Fallback al cuerpo entero si no se extrajo nada
    if not pieces:
        body = teletype.extractText(doc.text) or ""
        body = body.strip()
        if body:
            pieces.append(body)

    return "\n".join(pieces).strip() + "\n"

def to_markdown_with_rules(src_text: str) -> str:
    """
    Reglas:
      - Rachas de líneas que empiezan por '+' o '-' -> bloque ```diff
      - Líneas que empiezan por '•' -> *<span class="ia-thought">...</span>*
      - Respeta bloques ```lang existentes
    """
    lines = src_text.splitlines()
    out: List[str] = []
    i = 0
    in_code = False

    def is_code_fence(s: str) -> bool:
        return s.strip().startswith("```")

    while i < len(lines):
        line = lines[i]

        # cercas de código existentes
        if is_code_fence(line):
            out.append(line)
            in_code = not in_code
            i += 1
            continue

        if in_code:
            out.append(line)
            i += 1
            continue

        # bloque diff contiguo
        if line.startswith(("+", "-")) and not line.startswith(("+++", "---")):
            block = [line]
            i += 1
            while (i < len(lines)
                   and lines[i].startswith(("+", "-"))
                   and not lines[i].startswith(("+++", "---"))
                   and not is_code_fence(lines[i])):
                block.append(lines[i])
                i += 1
            out.append("```diff")
            out.extend(block)
            out.append("```")
            continue

        # pensamiento IA
        if line.lstrip().startswith("•"):
            content = line.lstrip()[1:].lstrip()
            out.append(f"*<span class=\"ia-thought\">{html.escape(content)}</span>*")
            i += 1
            continue

        out.append(line)
        i += 1

    return ("\n".join(out)).rstrip() + "\n"

def ensure_pandoc() -> None:
    if shutil.which("pandoc") is None:
        raise RuntimeError("pandoc no encontrado. Instálalo con: sudo apt install -y pandoc")

def md_to_html(md_text: str, embed_css: bool = True) -> str:
    """
    Usa pandoc para convertir desde markdown GitHub (gfm) a html5 standalone,
    luego embebe CSS si aplica.
    """
    import tempfile
    ensure_pandoc()
    with tempfile.TemporaryDirectory() as td:
        md_path = Path(td) / "in.md"
        out_path = Path(td) / "out.html"
        md_path.write_text(md_text, encoding="utf-8")
        cmd = ["pandoc", "--from", "gfm", "--to", "html5", "--standalone",
               str(md_path), "-o", str(out_path)]
        subprocess.run(cmd, check=True)
        html_str = out_path.read_text(encoding="utf-8", errors="replace")
    if embed_css:
        style_tag = f"<style>\n{CODEX_CSS}\n</style>\n"
        if "</head>" in html_str:
            html_str = html_str.replace("</head>", style_tag + "</head>")
        else:
            html_str = style_tag + html_str
    return html_str

def convert_file(in_file: Path, out_dir: Optional[Path] = None) -> tuple[Path, Path]:
    """
    Convierte un archivo .txt/.odt a .md + .html
    - out_dir: si se pasa, escribe ahí; si no, junto al archivo original.
    """
    if out_dir is None:
        out_dir = in_file.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = in_file.stem
    out_md = out_dir / f"{stem}.md"
    out_html = out_dir / f"{stem}.html"

    # lectura
    suffix = in_file.suffix.lower()
    if suffix == ".odt":
        src = read_odt(in_file)
    elif suffix in (".txt",):
        src = read_plain_txt(in_file)
    else:
        raise RuntimeError(f"Formato no soportado: {in_file.name} (usa .odt o .txt)")

    # a MD con reglas
    md = to_markdown_with_rules(src)
    out_md.write_text(md, encoding="utf-8")

    # a HTML con CSS embebido
    html_final = md_to_html(md, embed_css=True)
    out_html.write_text(html_final, encoding="utf-8")

    return out_md, out_html

# -------------------- GUI TKINTER --------------------
# (Importamos Tkinter aquí, a nivel de módulo. Si quisieras evitar cargar Tk con --version,
#  puedes mover estos imports dentro de main() y también mover la clase CodexGUI allí.)
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# drag&drop opcional
DND_AVAILABLE = False
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except Exception:
    DND_AVAILABLE = False

class CodexGUI:
    def __init__(self):
        if DND_AVAILABLE:
            self.root = TkinterDnD.Tk()
        else:
            self.root = tk.Tk()

        self.root.title("CodexRenderer — Drag & Drop  (.txt / .odt)")
        self.root.geometry("800x560")

        # estilos
        default_font = ("Segoe UI", 10)
        self.root.option_add("*Font", default_font)

        # Frame top: Drop area + botones
        top = ttk.Frame(self.root, padding=12)
        top.pack(fill="x")

        self.drop_label = tk.Label(
            top,
            text="Arrastra aquí tus archivos .txt / .odt\n(o usa 'Añadir archivos')",
            relief="groove",
            borderwidth=2,
            height=4,
            bg="#101010", fg="#C2FFC2",
        )
        self.drop_label.pack(fill="x")

        if DND_AVAILABLE:
            self.drop_label.drop_target_register(DND_FILES)
            self.drop_label.dnd_bind("<<Drop>>", self.on_drop)

        btns = ttk.Frame(top)
        btns.pack(fill="x", pady=(10, 0))

        self.btn_add = ttk.Button(btns, text="Añadir archivos…", command=self.on_add_files)
        self.btn_add.pack(side="left")

        self.btn_clear = ttk.Button(btns, text="Limpiar lista", command=self.on_clear)
        self.btn_clear.pack(side="left", padx=6)

        self.btn_outdir = ttk.Button(btns, text="Elegir carpeta de salida…", command=self.on_pick_outdir)
        self.btn_outdir.pack(side="left")

        self.outdir_var = tk.StringVar(value="(misma carpeta de los archivos)")
        ttk.Label(btns, textvariable=self.outdir_var).pack(side="left", padx=10)

        # Middle: lista de archivos
        mid = ttk.Frame(self.root, padding=12)
        mid.pack(fill="both", expand=True)

        self.files_list = tk.Listbox(mid, height=10, selectmode="extended")
        self.files_list.pack(fill="both", expand=True, side="left")
        scroll = ttk.Scrollbar(mid, orient="vertical", command=self.files_list.yview)
        scroll.pack(side="left", fill="y")
        self.files_list.config(yscrollcommand=scroll.set)

        # Bottom: Run + log
        bottom = ttk.Frame(self.root, padding=12)
        bottom.pack(fill="both")

        self.btn_run = ttk.Button(bottom, text="Run", command=self.on_run)
        self.btn_run.pack(side="left")

        self.status_var = tk.StringVar(value="Listo.")
        ttk.Label(bottom, textvariable=self.status_var).pack(side="left", padx=10)

        # Log
        self.log = tk.Text(self.root, height=10, bg="#0b0b0b", fg="#c2ffc2")
        self.log.pack(fill="both", expand=False, padx=12, pady=(0, 12))

        # Datos
        self.out_dir: Optional[Path] = None

    def log_print(self, msg: str):
        self.log.insert("end", msg + "\n")
        self.log.see("end")
        self.root.update_idletasks()

    def on_add_files(self):
        paths = filedialog.askopenfilenames(
            title="Selecciona archivos .txt / .odt",
            filetypes=[("Text/ODT", "*.txt *.odt"), ("Text", "*.txt"), ("ODT", "*.odt"), ("Todos", "*.*")]
        )
        for p in paths:
            self._add_file(Path(p))

    def on_drop(self, event):
        # tkinterdnd2 pasa rutas separadas por espacios, manejar comillas
        raw = event.data
        items = self._split_dnd_paths(raw)
        for it in items:
            self._add_file(Path(it))

    def _split_dnd_paths(self, raw: str) -> List[str]:
        # Soporta rutas con espacios y {braces}
        out: List[str] = []
        buf = ""
        in_brace = False
        for ch in raw:
            if ch == "{":
                in_brace = True
                buf = ""
                continue
            if ch == "}":
                in_brace = False
                out.append(buf)
                buf = ""
                continue
            if ch == " " and not in_brace:
                if buf:
                    out.append(buf)
                    buf = ""
                continue
            buf += ch
        if buf:
            out.append(buf)
        return out

    def _add_file(self, p: Path):
        if not p.exists():
            return
        if p.is_dir():
            # si es carpeta, añadir todos los .txt/.odt dentro (no recursivo)
            for f in sorted(p.iterdir()):
                if f.suffix.lower() in (".txt", ".odt"):
                    self.files_list.insert("end", str(f))
            self.log_print(f"[add] Carpeta: {p}")
        else:
            if p.suffix.lower() in (".txt", ".odt"):
                self.files_list.insert("end", str(p))
                self.log_print(f"[add] {p}")
            else:
                self.log_print(f"[skip] {p.name} (no es .txt/.odt)")

    def on_clear(self):
        self.files_list.delete(0, "end")
        self.log_print("[clear] Lista vaciada.")

    def on_pick_outdir(self):
        d = filedialog.askdirectory(title="Elige carpeta de salida")
        if d:
            self.out_dir = Path(d)
            self.outdir_var.set(str(self.out_dir))
            self.log_print(f"[outdir] {self.out_dir}")

    def on_run(self):
        items = [Path(self.files_list.get(i)) for i in range(self.files_list.size())]
        if not items:
            messagebox.showwarning("CodexRenderer", "No hay archivos en la lista.")
            return

        self.btn_run.config(state="disabled")
        self.status_var.set("Procesando…")
        t = threading.Thread(target=self._run_convert, args=(items,), daemon=True)
        t.start()

    def _run_convert(self, items: List[Path]):
        ok, fail = 0, 0
        for p in items:
            try:
                self.log_print(f"[convert] {p.name} …")
                out_md, out_html = convert_file(p, self.out_dir)
                self.log_print(f"  ✔ MD:    {out_md}")
                self.log_print(f"  ✔ HTML:  {out_html}")
                ok += 1
            except Exception as e:
                self.log_print(f"  ✖ ERROR: {e}")
                fail += 1
        self.status_var.set(f"Terminado. OK={ok}  ERR={fail}")
        self.btn_run.config(state="normal")

# -------------------- PUNTO DE ENTRADA --------------------
def parse_cli():
    p = argparse.ArgumentParser(add_help=False)
    p.add_argument('--version', '-version', '-v', action='store_true',
                   help='Muestra la versión y sale')
    p.add_argument('--debug', action='store_true',
                   help='Imprime trazas de depuración')
    args, _ = p.parse_known_args()
    return args

def main(debug: bool = False):
    if debug:
        print("DEBUG: entrando en main()")
    try:
        if debug:
            print("DEBUG: creando instancia CodexGUI()")
        app = CodexGUI()
        if debug:
            print("DEBUG: llamando a mainloop()")
        app.root.mainloop()
        if debug:
            print("DEBUG: mainloop() terminó (ventana cerrada)")
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        print("ERROR en CodexRenderer GUI:\n", tb, flush=True)
        try:
            root = tk.Tk(); root.withdraw()
            messagebox.showerror("CodexRenderer — Error", f"{e}\n\n{tb}")
            root.destroy()
        except Exception:
            pass
        sys.exit(1)

if __name__ == "__main__":
    args = parse_cli()
    if args.version:
        print(f"CodexRenderer GUI {__version__}")
        sys.exit(0)
    main(debug=args.debug)

