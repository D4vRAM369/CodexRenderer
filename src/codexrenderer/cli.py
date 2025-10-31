from __future__ import annotations
import argparse
import sys
from pathlib import Path
from . import codex

__all__ = ["main"]

def convert_file(input_path: Path, out_dir: Path, to: str = "html") -> Path:
    """
    Convierte archivos usando el motor de codex.
    """
    out_dir.mkdir(parents=True, exist_ok=True)

    if to.lower() == "md":
        md_path, _ = codex.convert_file(input_path, out_dir, inline_css=False, embed_css=False)
        return md_path
    else:
        md_path, html_path = codex.convert_file(input_path, out_dir, inline_css=True, embed_css=True)
        return html_path if html_path else md_path

def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="codexrenderer",
        description="Convierte ODT/TXT a Markdown/HTML con tema Codex/Alacritty."
    )
    p.add_argument("inputs", nargs="+", help="Rutas a ficheros .odt o .txt")
    p.add_argument("-o", "--out-dir", default="out", help="Directorio de salida (por defecto: out)")
    p.add_argument("--to", choices=["html","md"], default="html", help="Formato de salida")
    args = p.parse_args(argv)

    out_dir = Path(args.out_dir)
    errors = 0

    for raw in args.inputs:
        src = Path(raw)
        if not src.exists():
            print(f"[!] No existe: {src}", file=sys.stderr)
            errors += 1
            continue
        try:
            out_path = convert_file(src, out_dir, to=args.to)
            print(f"[ok] {src} -> {out_path}")
        except Exception as ex:
            print(f"[X] Error en {src}: {ex}", file=sys.stderr)
            errors += 1

    return 0 if errors == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())

