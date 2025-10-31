from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable

from .claudecode_core import convert_path
from .geminirenderer_core import ensure_pandoc  # reutilizamos la comprobación existente

__all__ = ["main"]


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="claude-coderenderer",
        description="Renderizador estilo Claude-Code: Markdown + HTML con tema naranja y estrella.",
    )
    parser.add_argument("inputs", nargs="+", help="Archivos .txt/.md/.odt a procesar.")
    parser.add_argument(
        "-o",
        "--out-dir",
        default=None,
        help="Directorio de salida. Por defecto usa la carpeta del archivo.",
    )
    parser.add_argument(
        "--skip-pandoc-check",
        action="store_true",
        help="No verifica que pandoc esté instalado antes de procesar.",
    )
    return parser


def _iter_inputs(raw_inputs: Iterable[str]) -> Iterable[Path]:
    for raw in raw_inputs:
        yield Path(raw).expanduser().resolve()


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if not args.skip_pandoc_check:
        try:
            ensure_pandoc()
        except Exception as exc:  # pragma: no cover
            print(f"[X] {exc}", file=sys.stderr)
            return 1

    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else None
    errors = 0

    for src in _iter_inputs(args.inputs):
        if not src.exists():
            print(f"[!] No existe: {src}", file=sys.stderr)
            errors += 1
            continue
        target_dir = out_dir or src.parent
        try:
            md_path, html_path = convert_path(src, target_dir)
            print(f"[ok] {src.name} -> {md_path} | {html_path}")
        except Exception as exc:  # pragma: no cover
            print(f"[X] Error en {src.name}: {exc}", file=sys.stderr)
            errors += 1

    return 0 if errors == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
