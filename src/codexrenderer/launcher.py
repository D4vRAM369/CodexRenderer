# src/codexrenderer/launcher.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Launcher unificado (GUI+CLI) para Codex, Gemini y Claude.

Opciones:
- Codex (GUI)
- Gemini (GUI)  -> usa codexrenderer.geminirenderer_gui:main si existe; si no, cae a CLI
- Claude (GUI)  -> usa codexrenderer.claudecode_gui:main si existe; si no, cae a CLI
- Gemini (CLI)  -> codexrenderer.gemini_cli:main (con selectores de archivos)
- Claude (CLI)  -> codexrenderer.claudecode_cli:main (con selectores de archivos)
"""
from __future__ import annotations
import sys, subprocess, shutil, importlib.util
from typing import List, Optional

def _has_mod(name: str) -> bool:
    return importlib.util.find_spec(name) is not None

def _pandoc_ok() -> bool:
    return shutil.which("pandoc") is not None

def _launch_import(module: str, attr: str = "main") -> int:
    mod = __import__(module, fromlist=[attr])
    fn = getattr(mod, attr)
    return int(fn() or 0)

def _run_module(module: str, args: List[str]) -> int:
    return subprocess.call([sys.executable, "-m", module, *args])

# ---------- pickers ----------
def _choose_files_gui() -> Optional[List[str]]:
    try:
        import tkinter as tk
        from tkinter import filedialog
    except Exception:
        return None
    root = tk.Tk(); root.withdraw()
    files = filedialog.askopenfilenames(
        title="Selecciona entradas (.txt/.odt/.md/.log)",
        filetypes=[("Text/ODT/MD/LOG", "*.txt *.odt *.md *.log"), ("Todos", "*.*")]
    )
    root.update(); root.destroy()
    return list(files) if files else []

def _choose_outdir_gui() -> Optional[str]:
    try:
        import tkinter as tk
        from tkinter import filedialog
    except Exception:
        return None
    root = tk.Tk(); root.withdraw()
    outdir = filedialog.askdirectory(title="Selecciona carpeta de salida")
    root.update(); root.destroy()
    return outdir or ""

def _ask_console_files() -> List[str]:
    print("Introduce rutas separadas por espacio:")
    line = input("> ").strip()
    return [p for p in line.split() if p]

def _ask_console_outdir() -> str:
    print("Carpeta de salida (Enter = misma carpeta):")
    return input("> ").strip()

def _flow_cli(module_name: str) -> int:
    files = _choose_files_gui()
    if files is None:  # sin entorno gráfico
        files = _ask_console_files()
    if not files:
        print("[INFO] Operación cancelada (sin archivos)."); return 0

    outdir = _choose_outdir_gui()
    if outdir is None:
        outdir = _ask_console_outdir()

    args: List[str] = []
    if outdir: args += ["-o", outdir]
    if not _pandoc_ok(): args += ["--skip-pandoc-check"]
    args += files
    return _run_module(module_name, args)

# ---------- selector ----------
OPTIONS = [
    ("Codex (GUI)",           "gui-codex"),
    ("Gemini (GUI)",          "gui-gemini"),
    ("Claude (GUI)",          "gui-claude"),
    ("Gemini (CLI)",          "cli-gemini"),
    ("Claude (CLI)",          "cli-claude"),
]

def _selector_gui() -> Optional[str]:
    try:
        import tkinter as tk
        from tkinter import ttk
    except Exception:
        return None
    root = tk.Tk()
    root.title("CodexRunner — Selecciona modo")
    root.geometry("460x260"); root.resizable(False, False)

    ttk.Label(root, text="¿Qué quieres lanzar?").pack(pady=(16,8))

    v = tk.StringVar(value=OPTIONS[0][1])
    frm = ttk.Frame(root, padding=10); frm.pack(fill="x")
    for label, val in OPTIONS:
        ttk.Radiobutton(frm, text=label, value=val, variable=v).pack(anchor="w")

    def ok(): root.quit()
    ttk.Button(root, text="Lanzar", command=ok).pack(pady=(8,16))
    root.mainloop()
    choice = v.get(); root.destroy()
    return choice

def _selector_cli() -> str:
    print("Selecciona opción:")
    for i,(label, val) in enumerate(OPTIONS, start=1):
        print(f"  {i}) {label}")
    mapping = {str(i):val for i,(_,val) in enumerate(OPTIONS, start=1)}
    while True:
        ans = input("Opción [1-5]: ").strip()
        if ans in mapping: return mapping[ans]
        print("Inválido. Intenta de nuevo.")

def main():
    choice = _selector_gui() or _selector_cli()

    if choice == "gui-codex":
        # Tu GUI principal (drag-and-drop ya integrado)
        sys.exit(_launch_import("codexrenderer.codexrenderer_gui", "main"))

    if choice == "gui-gemini":
        if _has_mod("codexrenderer.geminirenderer_gui"):
            sys.exit(_launch_import("codexrenderer.geminirenderer_gui", "main"))
        print("[WARN] GUI de Gemini no encontrada. Abriendo CLI…")
        sys.exit(_flow_cli("codexrenderer.gemini_cli"))

    if choice == "gui-claude":
        if _has_mod("codexrenderer.claudecode_gui"):
            sys.exit(_launch_import("codexrenderer.claudecode_gui", "main"))
        print("[WARN] GUI de Claude no encontrada. Abriendo CLI…")
        sys.exit(_flow_cli("codexrenderer.claudecode_cli"))

    if choice == "cli-gemini":
        sys.exit(_flow_cli("codexrenderer.gemini_cli"))

    if choice == "cli-claude":
        sys.exit(_flow_cli("codexrenderer.claudecode_cli"))

if __name__ == "__main__":
    main()

