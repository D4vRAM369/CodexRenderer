#!/usr/bin/env bash
# GeminiRenderer workflow: convierte exportes Gemini CLI (.txt/.md/.odt)
# a Markdown enriquecido y HTML con el tema Gemini.

set -euo pipefail

usage() {
  cat <<'USO'
Uso:
  ./convert_gemini.sh <entrada.(txt|md|odt)> [--outdir RUTA]

Descripción:
  - Convierte exportes de Gemini CLI a Markdown enriquecido (.gemini.md).
  - Genera el HTML final (.gemini.html) con el CSS de Gemini embebido.

Opciones:
  --outdir RUTA    Directorio de salida (por defecto, el de la entrada).
USO
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" || -z "${1:-}" ]]; then
  usage
  exit 0
fi

INPUT="$1"; shift || true

OUTDIR=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --outdir)
      OUTDIR="${2:-}"
      shift 2 || true
      ;;
    *)
      echo "Opción no reconocida: $1" >&2
      exit 1
      ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ABS_INPUT="$(realpath -m "$INPUT")"
if [[ ! -f "$ABS_INPUT" ]]; then
  echo "Error: no existe $ABS_INPUT" >&2
  exit 1
fi

if [[ -z "$OUTDIR" ]]; then
  OUTDIR="$(dirname "$ABS_INPUT")"
fi
mkdir -p "$OUTDIR"
ABS_OUTDIR="$(realpath -m "$OUTDIR")"

export GEMINI_INPUT="$ABS_INPUT"
export GEMINI_OUTDIR="$ABS_OUTDIR"
export GEMINI_SCRIPT_DIR="$SCRIPT_DIR"

mapfile -t RESULT < <(python3 - <<'PY'
import os
import sys
from pathlib import Path

sys.path.insert(0, os.environ["GEMINI_SCRIPT_DIR"])

from geminirenderer_core import convert_path

input_path = Path(os.environ["GEMINI_INPUT"])
out_dir = Path(os.environ["GEMINI_OUTDIR"])
md_path, html_path = convert_path(input_path, out_dir)
print(md_path)
print(html_path)
PY
)

MD_PATH="${RESULT[0]}"
HTML_PATH="${RESULT[1]}"

echo "✅ Markdown: $MD_PATH"
echo "✅ HTML:     $HTML_PATH"
