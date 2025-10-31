#!/usr/bin/env bash
# GeminiRenderer workflow: usa la CLI empaquetada (`codexrenderer.gemini_cli`).
# Convierte exportes Gemini (.txt/.md/.odt) a Markdown + HTML con tema Gemini.

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

# Permite ejecutar desde el repo sin instalar el paquete
export PYTHONPATH="${SCRIPT_DIR}/src${PYTHONPATH:+:$PYTHONPATH}"

python3 -m codexrenderer.gemini_cli "$ABS_INPUT" -o "$OUTDIR"
