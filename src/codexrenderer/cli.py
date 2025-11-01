from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import codex

__all__ = ["main"]


def convert_file(
    input_path: Path,
    out_dir: Path,
    *,
    write_html: bool,
    inline_css: bool,
) -> Path:
    """Convierte archivos usando el motor de Codex."""
    out_dir.mkdir(parents=True, exist_ok=True)

    md_path, html_path = codex.convert_file(
        input_path,
        out_dir,
        inline_css=inline_css,
        embed_css=write_html,
    )
    if write_html and html_path is not None:
        return html_path
    return md_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="codexrenderer",
        description="Convierte ODT/TXT a Markdown/HTML con tema Codex/Alacritty.",
    )
    parser.add_argument("inputs", nargs="+", help="Rutas a ficheros .odt, .txt o .md")
    parser.add_argument(
        "-o",
        "--out-dir",
        default="out",
        help="Directorio de salida (por defecto: out)",
    )
    parser.add_argument(
        "--to",
        choices=["html", "md"],
        default="html",
        help="Formato principal de salida (por defecto: html).",
    )
    parser.add_argument(
        "--md-only",
        action="store_true",
        help="Genera únicamente Markdown (equivalente a --to md).",
    )
    parser.add_argument(
        "--inline-css",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Incorpora el CSS en el Markdown generado (usa --no-inline-css para omitirlo).",
    )
    args = parser.parse_args(argv)

    if args.md_only:
        write_html = False
    else:
        write_html = args.to == "html"

    out_dir = Path(args.out_dir)
    errors = 0

    for raw in args.inputs:
        src = Path(raw)
        if not src.exists():
            print(f"[!] No existe: {src}", file=sys.stderr)
            errors += 1
            continue

        try:
            out_path = convert_file(
                src,
                out_dir,
                write_html=write_html,
                inline_css=args.inline_css,
            )
            print(f"[ok] {src} -> {out_path}")
        except Exception as ex:  # pragma: no cover - logging branch
            print(f"[X] Error en {src}: {ex}", file=sys.stderr)
            errors += 1

    return 0 if errors == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
