#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

# =========================
# PBL-01: vendor path first
# =========================
import os
import sys
import math
import argparse
import platform
import threading
from pathlib import Path
from typing import List, Optional

HERE = Path(__file__).resolve().parent
VENDOR = HERE / "thirdparty" / "vendor"
if VENDOR.is_dir() and str(VENDOR) not in sys.path:
    sys.path.insert(0, str(VENDOR))

# Asegura que el paquete 'codexrenderer' sea importable si se ejecuta como script
PROJECT_ROOT = HERE.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Proyecto
from codexrenderer.claudecode_core import convert_path
from codexrenderer.geminirenderer_core import ensure_pandoc


# ============================================================================
# PBL-02: Bootstrap robusto de TkDND (mismo enfoque que GeminiRenderer)
# ============================================================================
def _pick_tkdnd_subdir(root: Path) -> Path | None:
    sysname = platform.system().lower()
    mach = platform.machine().lower()

    if "aarch64" in mach or "arm64" in mach:
        arch = "arm64"
    elif mach in ("x86_64", "amd64", "x64"):
        arch = "x64"
    elif mach in ("i386", "i686", "x86"):
        arch = "x86"
    else:
        arch = mach

    candidates: list[Path] = []
    if sysname.startswith("linux"):
        candidates += [root / f"linux-{arch}", root / "linux"]
    elif sysname.startswith("darwin"):
        candidates += [
            root / "macos-universal",
            root / f"macos-{arch}",
            root / "macos",
        ]
    elif sysname.startswith("win"):
        candidates += [root / f"win-{arch}", root / "win"]

    candidates.append(root)

    for cand in candidates:
        if (cand / "tkdnd.tcl").exists():
            return cand
    return None


def _init_tkdnd_paths() -> str | None:
    env_val = os.environ.get("TKDND_LIBRARY")
    if env_val:
        return env_val

    vendor_root = HERE / "thirdparty" / "tkdnd"
    vendor_sub = _pick_tkdnd_subdir(vendor_root)
    if vendor_sub:
        os.environ["TKDND_LIBRARY"] = str(vendor_sub)
        return str(vendor_sub)

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

    if hasattr(sys, "_MEIPASS"):
        base = Path(getattr(sys, "_MEIPASS")) / "tkdnd"  # type: ignore[attr-defined]
        sub = _pick_tkdnd_subdir(base)
        if sub:
            os.environ["TKDND_LIBRARY"] = str(sub)
            return str(sub)

    return None


_TKDND_PATH = _init_tkdnd_paths()

# GUI base
import tkinter as tk  # noqa: E402
from tkinter import filedialog, messagebox, ttk  # noqa: E402

try:  # noqa: E402
    from tkinterdnd2 import DND_FILES, TkinterDnD  # type: ignore

    DND_AVAILABLE = True
    DND_STATUS_MSG = f"DnD activo ({_TKDND_PATH})" if _TKDND_PATH else "DnD activo (tkdnd)"
except Exception as _e:  # pragma: no cover
    DND_AVAILABLE = False
    DND_STATUS_MSG = f"DnD NO disponible: {_e!s}".splitlines()[0]


class ClaudeCodeRendererGUI:
    def __init__(self) -> None:
        ensure_pandoc()

        if DND_AVAILABLE:
            self.root = TkinterDnD.Tk()
        else:
            self.root = tk.Tk()

        self.root.title("Claude·Code Renderer — Drag & Drop")
        self.root.geometry("860x620")
        default_font = ("Noto Sans", 11)
        self.root.option_add("*Font", default_font)

        self._build_styles()
        self._build_layout()

        self.out_dir: Optional[Path] = None

    # ------------------------------------------------------------------ UI --
    def _build_styles(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")

        self.colors = {
            "bg": "#f5d7c8",
            "fg": "#341f18",
            "header_fg": "#2a1812",
            "accent": "#d0653f",
            "accent_dark": "#ab4f2d",
            "panel": "#fbe6db",
            "button_bg": "#f4b38f",
            "button_fg": "#341f18",
            "button_active": "#ffb88c",
            "button_disabled": "#d9a788",
            "drop_bg": "#fbece3",
            "drop_hover": "#f7dece",
            "drop_border": "#e5b9a1",
            "list_bg": "#fff5ee",
            "list_fg": "#341f18",
            "list_highlight": "#f6c5a7",
            "list_highlight_fg": "#2f1811",
            "log_bg": "#fae2d4",
            "log_fg": "#8a3f21",
            "status_fg": "#74351e",
            "footer_fg": "#8d4d2d",
        }

        self.root.configure(bg=self.colors["bg"])
        style.configure("Main.TFrame", background=self.colors["bg"])
        style.configure("TLabel", background=self.colors["bg"], foreground=self.colors["fg"])
        style.configure(
            "TButton",
            background=self.colors["button_bg"],
            foreground=self.colors["button_fg"],
            padding=6,
            focuscolor=self.colors["button_active"],
        )
        style.configure(
            "Run.TButton",
            background=self.colors["accent"],
            foreground="#fff7f0",
            padding=(14, 10),
            font=("Noto Sans", 12, "bold"),
            focuscolor=self.colors["accent_dark"],
        )
        style.map(
            "TButton",
            background=[
                ("active", self.colors["button_active"]),
                ("disabled", self.colors["panel"]),
            ],
            foreground=[("disabled", self.colors["button_disabled"])],
        )
        style.map(
            "Run.TButton",
            background=[
                ("active", self.colors["accent_dark"]),
                ("disabled", self.colors["button_disabled"]),
            ],
            foreground=[("disabled", self.colors["button_disabled"])],
        )
        style.configure(
            "Status.TLabel",
            background=self.colors["bg"],
            foreground=self.colors["status_fg"],
        )

    def _build_layout(self) -> None:
        colors = self.colors

        header = tk.Frame(self.root, bg=colors["bg"])
        header.pack(fill="x", padx=32, pady=(12, 6))

        banner = tk.Frame(header, bg=colors["bg"])
        banner.pack(anchor="w")

        mark_size = 96
        mark = tk.Canvas(banner, width=mark_size, height=mark_size, bg=colors["bg"], highlightthickness=0)
        center = mark_size / 2
        radius = mark_size * 0.44
        for angle_deg in range(0, 360, 30):
            rad = math.radians(angle_deg)
            x = center + math.cos(rad) * radius
            y = center + math.sin(rad) * radius
            mark.create_line(
                center,
                center,
                x,
                y,
                fill=colors["accent"],
                width=14,
                capstyle=tk.ROUND,
            )
        mark.create_oval(
            center - radius * 0.18,
            center - radius * 0.18,
            center + radius * 0.18,
            center + radius * 0.18,
            fill=colors["accent"],
            outline=colors["accent"],
        )
        mark.pack(side="left", padx=(0, 18))

        title_box = tk.Frame(banner, bg=colors["bg"])
        title_box.pack(side="left")

        title_row = tk.Frame(title_box, bg=colors["bg"])
        title_row.pack(anchor="w", pady=(6, 0))

        title = tk.Label(
            title_row,
            text="Claude",
            font=("Georgia", 32, "bold"),
            fg=colors["header_fg"],
            bg=colors["bg"],
            anchor="w",
        )
        title.pack(side="left")

        accent = tk.Label(
            title_row,
            text="✶",
            font=("Georgia", 24, "bold"),
            fg=colors["accent_dark"],
            bg=colors["bg"],
            anchor="w",
        )
        accent.pack(side="left", padx=(6, 0))

        code_label = tk.Label(
            title_row,
            text="Code",
            font=("Georgia", 32, "bold"),
            fg=colors["accent_dark"],
            bg=colors["bg"],
            anchor="w",
        )
        code_label.pack(side="left", padx=(12, 0))

        subtitle2 = tk.Label(
            title_box,
            text="RENDERER",
            font=("Futura", 26, "bold"),
            fg=colors["accent_dark"],
            bg=colors["bg"],
            anchor="w",
        )
        subtitle2.pack(anchor="w", pady=(6, 0))

        top = ttk.Frame(self.root, padding=12, style="Main.TFrame")
        top.pack(fill="x", padx=12)

        self.drop_label = tk.Label(
            top,
            text="Suelta aquí tus conversaciones Claude (.txt/.md/.odt)\n"
            "o haz clic para elegirlas manualmente",
            relief="ridge",
            borderwidth=2,
            height=4,
            bg=colors["drop_bg"],
            fg=colors["fg"],
            highlightbackground=colors["drop_border"],
            highlightcolor=colors["drop_border"],
            font=("Noto Sans", 12, "bold"),
        )
        self.drop_label.pack(fill="x")

        if DND_AVAILABLE:
            try:
                self.drop_label.drop_target_register(DND_FILES)  # type: ignore[attr-defined]
                self.drop_label.dnd_bind("<<Drop>>", self.on_drop)

                def on_enter(_event: object) -> None:
                    self.drop_label.config(bg=colors["drop_hover"])

                def on_leave(_event: object) -> None:
                    self.drop_label.config(bg=colors["drop_bg"])

                self.drop_label.dnd_bind("<<DragEnter>>", on_enter)
                self.drop_label.dnd_bind("<<DragLeave>>", on_leave)
            except Exception as e:
                self.drop_label.config(
                    text=f"Drag & Drop no disponible ({e}).\nHaz clic para añadir archivos…"
                )
        else:
            self.drop_label.config(
                text="Drag & Drop no disponible.\nHaz clic para añadir archivos…"
            )

        self.drop_label.bind("<Button-1>", lambda _e: self.on_add_files())

        buttons = ttk.Frame(top, style="Main.TFrame")
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

        self.btn_run = ttk.Button(
            buttons,
            text="RUN Renderer",
            style="Run.TButton",
            command=self.on_run,
        )
        self.btn_run.pack(side="right")

        mid = ttk.Frame(self.root, padding=12, style="Main.TFrame")
        mid.pack(fill="both", expand=True, padx=12)

        self.files_list = tk.Listbox(
            mid,
            height=12,
            selectmode="extended",
            bg=colors["list_bg"],
            fg=colors["list_fg"],
            highlightbackground=colors["drop_border"],
            highlightcolor=colors["drop_border"],
            selectbackground=colors["list_highlight"],
            selectforeground=colors["list_highlight_fg"],
        )
        self.files_list.pack(fill="both", expand=True, side="left")

        scroll = ttk.Scrollbar(mid, orient="vertical", command=self.files_list.yview)
        scroll.pack(side="left", fill="y")
        self.files_list.configure(yscrollcommand=scroll.set)

        bottom = ttk.Frame(self.root, padding=12, style="Main.TFrame")
        bottom.pack(fill="x", padx=12)

        self.status_var = tk.StringVar(value=f"Listo. {DND_STATUS_MSG}")
        ttk.Label(bottom, textvariable=self.status_var, style="Status.TLabel").pack(
            side="left", padx=10
        )

        self.log = tk.Text(
            self.root,
            height=8,
            bg=colors["log_bg"],
            fg=colors["log_fg"],
            insertbackground=colors["fg"],
            borderwidth=0,
            wrap="word",
        )
        self.log.pack(fill="both", expand=False, padx=12, pady=(0, 8))

        disclaimer = tk.Label(
            self.root,
            text="DISCLAIMER: este no es un proyecto vinculado ni oficial de Anthropic",
            font=("Noto Sans", 9),
            fg=colors["footer_fg"],
            bg=colors["bg"],
        )
        disclaimer.pack(fill="x", padx=16, pady=(0, 12))

    # ------------------------------------------------------------- Callbacks --
    def log_print(self, message: str) -> None:
        self.log.insert("end", message + "\n")
        self.log.see("end")
        self.root.update_idletasks()

    def on_add_files(self) -> None:
        paths = filedialog.askopenfilenames(
            title="Selecciona exportes Claude",
            filetypes=[
                ("Claude transcripts", "*.txt *.md *.odt"),
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
            messagebox.showinfo("Claude·Code Renderer", "Añade al menos un archivo.")
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
                self.log_print(f"  ★ MD:   {md_path}")
                self.log_print(f"  ★ HTML: {html_path}")
                ok += 1
            except Exception as exc:  # pragma: no cover
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
        prog="claudecode-renderer-gui",
        description="Interfaz gráfica drag & drop para exportes Claude en skin Claude-Code.",
    )
    parser.add_argument("--debug", action="store_true", help="Imprime información adicional")
    parser.add_argument("--version", action="store_true", help="Muestra la versión y sale")
    return parser.parse_args(argv)


__version__ = "0.1.0"


def _launch_gui(debug: bool = False) -> int:
    if debug:
        print("DEBUG: iniciando Claude-Code GUI")
        print("DEBUG: TKDND_LIBRARY =", os.environ.get("TKDND_LIBRARY"))
        print("DEBUG: DND_AVAILABLE =", DND_AVAILABLE, "|", DND_STATUS_MSG)
    try:
        app = ClaudeCodeRendererGUI()
        if debug:
            print("DEBUG: mainloop()")
        app.root.mainloop()
        return 0
    except Exception as exc:  # pragma: no cover
        import traceback

        tb = traceback.format_exc()
        print("ERROR en Claude-Code GUI:\n", tb, flush=True)
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Claude-Code Renderer — Error", f"{exc}\n\n{tb}")
            root.destroy()
        except Exception:
            pass
        return 1


def main(argv: list[str] | None = None) -> int:
    args = parse_cli(argv)
    if args.version:
        print(f"Claude-Code Renderer GUI {__version__}")
        return 0
    return _launch_gui(debug=args.debug)


if __name__ == "__main__":
    raise SystemExit(main())
