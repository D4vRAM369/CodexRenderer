#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

# =========================
# PBL-01: vendor path first
# =========================
# Si has "vendorizado" paquetes Python dentro del repo (p.ej. tkinterdnd2 en thirdparty/vendor),
# añádelos a sys.path ANTES de cualquier import del paquete.
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
VENDOR = HERE / "thirdparty" / "vendor"
if VENDOR.is_dir() and str(VENDOR) not in sys.path:
    sys.path.insert(0, str(VENDOR))  # ahora importará desde thirdparty/vendor si existe

# Resto de imports de estándar
import argparse
import platform
import threading
from typing import List, Optional

# Proyecto
from . import __version__ as PACKAGE_VERSION
from .geminirenderer_core import convert_path, ensure_pandoc

# ============================================================================
# PBL-02: Bootstrap robusto de TkDND (inspirado en CodexRenderer, extendido)
# ============================================================================
def _pick_tkdnd_subdir(root: Path) -> Path | None:
    """
    Devuelve la subcarpeta de tkdnd adecuada para la plataforma, si contiene tkdnd.tcl.
    Convenciones de carpeta soportadas:
      - linux-x64 / linux-x86 / linux-arm64
      - win-x64 / win-x86
      - macos-universal / macos-arm64 / macos-x64
    """
    sysname = platform.system().lower()
    mach = platform.machine().lower()

    # Normaliza arquitectura
    if "aarch64" in mach or "arm64" in mach:
        arch = "arm64"
    elif mach in ("x86_64", "amd64", "x64"):
        arch = "x64"
    elif mach in ("i386", "i686", "x86"):
        arch = "x86"
    else:
        arch = mach  # fallback

    # Candidatos por plataforma
    candidates: list[Path] = []
    if sysname.startswith("linux"):
        candidates += [root / f"linux-{arch}", root / "linux"]
    elif sysname.startswith("darwin"):
        # evita nombres antiguos "osx-*"; usa "macos-*"
        candidates += [
            root / "macos-universal",
            root / f"macos-{arch}",
            root / "macos",
        ]
    elif sysname.startswith("win"):
        candidates += [root / f"win-{arch}", root / "win"]

    # Fallback directo al root
    candidates.append(root)

    for c in candidates:
        if (c / "tkdnd.tcl").exists():
            return c
    return None


def _init_tkdnd_paths() -> str | None:
    """
    Intenta resolver TKDND_LIBRARY en este orden:
      1) Variable de entorno TKDND_LIBRARY (si ya viene definida externamente).
      2) thirdparty/tkdnd/<plataforma> dentro del proyecto.
      3) Carpeta "tkdnd" al lado de tkinterdnd2 en site-packages o vendor.
      4) Carpeta "tkdnd" incluida en bundles (p.ej. PyInstaller, sys._MEIPASS).
    Devuelve la ruta establecida o None si no se encontró, pero no falla:
    la GUI podrá degradar a "sin DnD" con file picker.
    """
    # 0) Si ya está puesta por el entorno, respétala
    env_val = os.environ.get("TKDND_LIBRARY")
    if env_val:
        return env_val

    # 1) thirdparty/tkdnd en el repo
    vendor_root = HERE / "thirdparty" / "tkdnd"
    vendor_sub = _pick_tkdnd_subdir(vendor_root)
    if vendor_sub:
        os.environ["TKDND_LIBRARY"] = str(vendor_sub)
        return str(vendor_sub)

    # 2) Paquete tkinterdnd2 (sirve si el propio paquete incluye "tkdnd/")
    try:
        import importlib.util

        spec = importlib.util.find_spec("tkinterdnd2")
        if spec and spec.origin:
            pkg_dir = Path(spec.origin).parent
            sub = _pick_tkdnd_subdir(pkg_dir / "tkdnd")
            if sub:
                os.environ["TKDND_LIBRARY"] = str(sub)
                return str(sub)
    except Exception:
        pass

    # 3) Bundles estilo PyInstaller
    if hasattr(sys, "_MEIPASS"):
        base = Path(getattr(sys, "_MEIPASS")) / "tkdnd"  # type: ignore[attr-defined]
        sub = _pick_tkdnd_subdir(base)
        if sub:
            os.environ["TKDND_LIBRARY"] = str(sub)
            return str(sub)

    # No encontrada (la GUI seguirá sin DnD)
    return None


_TKDND_PATH = _init_tkdnd_paths()

# GUI base
import tkinter as tk  # noqa: E402
from tkinter import filedialog, messagebox, ttk  # noqa: E402

# Intento de import de tkinterdnd2 (puede salir mal si sólo falta la parte nativa)
try:  # noqa: E402
    from tkinterdnd2 import DND_FILES, TkinterDnD  # type: ignore

    DND_AVAILABLE = True
    DND_STATUS_MSG = f"DnD activo ({_TKDND_PATH})" if _TKDND_PATH else "DnD activo (tkdnd global)"
except Exception as _e:  # pragma: no cover
    DND_AVAILABLE = False
    DND_STATUS_MSG = f"DnD NO disponible: {_e!s}".splitlines()[0]


class GeminiRendererGUI:
    def __init__(self) -> None:
        # PBL-03: asegura dependencias externas (pandoc) antes de abrir UI
        ensure_pandoc()

        # Crea la raíz en función de DnD
        if DND_AVAILABLE:
            self.root = TkinterDnD.Tk()
        else:
            self.root = tk.Tk()

        self.root.title("GeminiRenderer — Drag & Drop (.txt / .md / .odt)")
        self.root.geometry("820x600")
        default_font = ("JetBrains Mono", 10)
        self.root.option_add("*Font", default_font)

        self._build_styles()
        self._build_layout()

        self.out_dir: Optional[Path] = None

    # ------------------------------------------------------------------ UI --
    def _build_styles(self) -> None:
        style = ttk.Style()
        bg = "#0f1117"
        fg = "#d9e3ff"
        panel = "#121a2c"

        self.root.configure(bg=bg)
        style.configure("TFrame", background=bg)
        style.configure("TLabel", background=bg, foreground=fg)
        style.configure("TButton", background=panel, foreground=fg)
        style.map("TButton", background=[("active", "#1b273f")])

    def _build_layout(self) -> None:
        top = ttk.Frame(self.root, padding=12)
        top.pack(fill="x")

        # Área de drop / clic
        self.drop_label = tk.Label(
            top,
            text="Arrastra tus exportes Gemini (.txt/.md/.odt)\n(o haz clic para elegir archivos)",
            relief="ridge",
            borderwidth=2,
            height=4,
            bg="#141c2c",
            fg="#ffe58f",
            font=("JetBrains Mono", 11, "bold"),
        )
        self.drop_label.pack(fill="x")

        # Bindings DnD si está disponible
        if DND_AVAILABLE:
            try:
                self.drop_label.drop_target_register(DND_FILES)  # type: ignore[attr-defined]
                self.drop_label.dnd_bind("<<Drop>>", self.on_drop)

                def on_enter(_event: object) -> None:
                    self.drop_label.config(bg="#1d2c47")

                def on_leave(_event: object) -> None:
                    self.drop_label.config(bg="#141c2c")

                self.drop_label.dnd_bind("<<DragEnter>>", on_enter)
                self.drop_label.dnd_bind("<<DragLeave>>", on_leave)
            except Exception as e:
                # Si falla el binding, degrada a clic
                self.drop_label.config(
                    text=f"Drag & Drop no disponible ({e}).\nHaz clic para añadir archivos…"
                )
        else:
            self.drop_label.config(
                text="Drag & Drop no disponible.\nHaz clic para añadir archivos…"
            )

        # Clic para file picker siempre activo
        self.drop_label.bind("<Button-1>", lambda _e: self.on_add_files())

        # Botonera superior
        buttons = ttk.Frame(top)
        buttons.pack(fill="x", pady=(10, 0))
        self.btn_add = ttk.Button(buttons, text="Añadir archivos…", command=self.on_add_files)
        self.btn_add.pack(side="left")

        self.btn_clear = ttk.Button(buttons, text="Limpiar lista", command=self.on_clear)
        self.btn_clear.pack(side="left", padx=6)

        self.btn_outdir = ttk.Button(
            buttons, text="Elegir carpeta de salida…", command=self.on_pick_outdir
        )
        self.btn_outdir.pack(side="left")

        self.outdir_var = tk.StringVar(value="(misma carpeta)")
        ttk.Label(buttons, textvariable=self.outdir_var).pack(side="left", padx=10)

        # Lista de archivos
        mid = ttk.Frame(self.root, padding=12)
        mid.pack(fill="both", expand=True)

        self.files_list = tk.Listbox(
            mid,
            height=12,
            selectmode="extended",
            bg="#101827",
            fg="#e5ecff",
            highlightbackground="#22324d",
            highlightcolor="#3a4f74",
            selectbackground="#2a3f65",
            selectforeground="#ffe58f",
        )
        self.files_list.pack(fill="both", expand=True, side="left")

        scroll = ttk.Scrollbar(mid, orient="vertical", command=self.files_list.yview)
        scroll.pack(side="left", fill="y")
        self.files_list.configure(yscrollcommand=scroll.set)

        # Barra inferior
        bottom = ttk.Frame(self.root, padding=12)
        bottom.pack(fill="x")

        self.btn_run = ttk.Button(bottom, text="Render", command=self.on_run)
        self.btn_run.pack(side="left")

        # Estado: muestra si DnD está activo y qué ruta se usa
        self.status_var = tk.StringVar(value=f"Listo. {DND_STATUS_MSG}")
        ttk.Label(bottom, textvariable=self.status_var).pack(side="left", padx=10)

        # Log
        self.log = tk.Text(
            self.root,
            height=10,
            bg="#0b121f",
            fg="#9fb4ff",
            insertbackground="#ffe58f",
            borderwidth=0,
            wrap="word",
        )
        self.log.pack(fill="both", expand=False, padx=12, pady=(0, 12))

    # ------------------------------------------------------------- Callbacks --
    def log_print(self, message: str) -> None:
        self.log.insert("end", message + "\n")
        self.log.see("end")
        self.root.update_idletasks()

    def on_add_files(self) -> None:
        paths = filedialog.askopenfilenames(
            title="Selecciona exportes Gemini",
            filetypes=[
                ("Gemini transcripts", "*.txt *.md *.odt"),
                ("Text", "*.txt"),
                ("Markdown", "*.md"),
                ("ODT", "*.odt"),
                ("Todos", "*.*"),
            ],
        )
        for path in paths:
            self._add_file(Path(path))

    def on_drop(self, event) -> None:  # type: ignore[override]
        for path in self._split_dnd_paths(event.data):
            self._add_file(Path(path))

    def on_clear(self) -> None:
        self.files_list.delete(0, "end")
        self.log_print("[lista] Vacía.")

    def on_pick_outdir(self) -> None:
        selected = filedialog.askdirectory(title="Elige carpeta de salida")
        if selected:
            self.out_dir = Path(selected)
            self.outdir_var.set(str(self.out_dir))
            self.log_print(f"[outdir] {self.out_dir}")

    def on_run(self) -> None:
        items = [Path(self.files_list.get(i)) for i in range(self.files_list.size())]
        if not items:
            messagebox.showinfo("GeminiRenderer", "Añade al menos un archivo.")
            return
        self.btn_run.config(state="disabled")
        self.status_var.set("Procesando…")
        threading.Thread(target=self._run_async, args=(items,), daemon=True).start()

    def _run_async(self, items: List[Path]) -> None:
        ok = 0
        fail = 0
        for item in items:
            try:
                self.log_print(f"[convert] {item.name} …")
                md_path, html_path = convert_path(item, self.out_dir)
                self.log_print(f"  ✔ MD:    {md_path}")
                self.log_print(f"  ✔ HTML:  {html_path}")
                ok += 1
            except Exception as exc:  # pragma: no cover - UI feedback
                self.log_print(f"  ✖ ERROR: {exc}")
                fail += 1
        self.status_var.set(f"Terminado. OK={ok} ERR={fail} — {DND_STATUS_MSG}")
        self.btn_run.config(state="normal")

    # ------------------------------------------------------------ Utilities --
    def _add_file(self, path: Path) -> None:
        if not path.exists():
            self.log_print(f"[skip] {path} (no existe)")
            return
        if path.is_dir():
            for child in sorted(path.iterdir()):
                if child.suffix.lower() in {".txt", ".md", ".odt"}:
                    self.files_list.insert("end", str(child))
            self.log_print(f"[add] Carpeta: {path}")
        else:
            if path.suffix.lower() in {".txt", ".md", ".odt"}:
                self.files_list.insert("end", str(path))
                self.log_print(f"[add] {path}")
            else:
                self.log_print(f"[skip] {path.name} (formato no soportado)")

    @staticmethod
    def _split_dnd_paths(raw: str) -> List[str]:
        # Parser Tk DnD para rutas con espacios {...}
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
                if buf:
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


def parse_cli(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="geminirenderer-gui",
        description="Interfaz gráfica Drag & Drop para convertir exportes Gemini.",
    )
    parser.add_argument("--debug", action="store_true", help="Imprime información adicional")
    parser.add_argument("--version", action="store_true", help="Muestra la versión y sale")
    return parser.parse_args(argv)


__version__ = PACKAGE_VERSION


def _launch_gui(debug: bool = False) -> int:
    if debug:
        print("DEBUG: iniciando GeminiRenderer GUI")
        print("DEBUG: TKDND_LIBRARY =", os.environ.get("TKDND_LIBRARY"))
        print("DEBUG: DND_AVAILABLE =", DND_AVAILABLE, "|", DND_STATUS_MSG)
    try:
        app = GeminiRendererGUI()
        if debug:
            print("DEBUG: mainloop()")
        app.root.mainloop()
        return 0
    except Exception as exc:  # pragma: no cover - feedback gráfico
        import traceback

        tb = traceback.format_exc()
        print("ERROR en GeminiRenderer GUI:\n", tb, flush=True)
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("GeminiRenderer — Error", f"{exc}\n\n{tb}")
            root.destroy()
        except Exception:
            pass
        return 1


def main(argv: list[str] | None = None) -> int:
    args = parse_cli(argv)
    if args.version:
        print(f"GeminiRenderer GUI {__version__}")
        return 0
    return _launch_gui(debug=args.debug)


if __name__ == "__main__":
    raise SystemExit(main())
