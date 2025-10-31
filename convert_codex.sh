#!/usr/bin/env bash
# --- Codex/Alacritty Workflow integrado ---
# Delegado al paquete Python `codexrenderer` (CLI oficial)
# Convierte .odt/.txt/.md -> Markdown + HTML con CSS embebido
# Autor: D4vRAM (Brian)

set -euo pipefail

# ---- Ayuda / uso
if [[ "${1:-}" == "-h" || "${1:-}" == "--help" || -z "${1:-}" ]]; then
  cat <<'USO'
Uso:
  ./convert_codex.sh <entrada.(odt|txt|md)> [--outdir RUTA]

Descripción:
  - Si la entrada es .odt o .txt: primero genera un .md con reglas Codex.
  - Luego renderiza el .md a .html con tema Alacritty/Codex.
  - El CSS se EMBEBE en el HTML (no depende de rutas).

Opciones:
  --outdir RUTA    Directorio de salida (por defecto, el de la entrada).
USO
  exit 0
fi

INPUT="$1"; shift || true

# ---- Flags opcionales
OUTDIR=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --outdir) OUTDIR="${2:-}"; shift 2 || true ;;
    *) echo "Opción no reconocida: $1" >&2; exit 1 ;;
  esac
done

# ---- Rutas
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ABS_INPUT="$(realpath -m "$INPUT")"
IN_DIR="$(dirname "$ABS_INPUT")"
[[ -z "$OUTDIR" ]] && OUTDIR="$IN_DIR"
mkdir -p "$OUTDIR"

# Asegura que el paquete src/ sea importable sin instalar
export PYTHONPATH="${SCRIPT_DIR}/src${PYTHONPATH:+:$PYTHONPATH}"

echo "→ Ejecutando CodexRenderer CLI…"
python3 -m codexrenderer.cli "$ABS_INPUT" -o "$OUTDIR"
echo "✅ Conversión finalizada en $OUTDIR"
