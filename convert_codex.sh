#!/usr/bin/env bash
# --- Codex/Alacritty Workflow integrado ---
# Convierte .odt/.txt → .md (usando txt_odt_to_md.py)
# y luego .md → .html (Pandoc + CSS oscuro embebido)
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

EXT="${ABS_INPUT##*.}"

# ---- 1) ODT/TXT → MD (si aplica)
if [[ "$EXT" == "odt" || "$EXT" == "txt" ]]; then
  BASENAME_NOEXT="$(basename "$ABS_INPUT" ."$EXT")"
  MD_OUT="$OUTDIR/${BASENAME_NOEXT}.md"
  echo "→ Convirtiendo $(basename "$ABS_INPUT") a Markdown…"
  python3 "$SCRIPT_DIR/txt_odt_to_md.py" "$ABS_INPUT" -o "$MD_OUT"
  ABS_INPUT="$MD_OUT"
fi

# Recalcular nombres
EXT="${ABS_INPUT##*.}"
if [[ "$EXT" != "md" ]]; then
  echo "Error: tras la conversión se esperaba .md, obtenido: $ABS_INPUT" >&2
  exit 1
fi
BASENAME_NOEXT="$(basename "$ABS_INPUT" .md)"
HTML_OUT="$OUTDIR/${BASENAME_NOEXT}.html"

# ---- 2) CSS (crear si no existe)
CSS_FILE="$SCRIPT_DIR/alacritty.css"
if [[ ! -f "$CSS_FILE" ]]; then
  cat > "$CSS_FILE" <<'CSS'
html,body{background:#0b0b0b;color:#ddd;font-family:'JetBrains Mono','Fira Code',monospace;line-height:1.45;margin:0;padding:24px}
a{color:#8ab4f8;text-decoration:none}
a:hover{text-decoration:underline}
pre,code{font-family:'JetBrains Mono','Fira Code',monospace}
div.sourceCode,pre.sourceCode,pre,code{background:#000;color:#ddd;border-radius:8px}
div.sourceCode{padding:12px;overflow:auto}
pre{padding:12px;overflow:auto}
code{background:#111;padding:0 4px;border-radius:4px}
pre>code{background:transparent;padding:0}
.gi{color:#00e676}.gd{color:#ff5252}
.ait{color:#00c853;font-style:italic}     /* pensamiento IA */
.q{color:#80d8ff;font-weight:600}         /* preguntas (?…, > PNL …) */
.prompt{color:#ffd54f;font-weight:600}    /* líneas que empiezan por >, ›, » */
h1,h2,h3{color:#e6e6e6;margin-top:1.2em}
CSS
fi
CSS_PATH="$(realpath -m "$CSS_FILE")"

# ---- 3) MD → HTML (CSS embebido + resaltado)
echo "→ Renderizando $(basename "$ABS_INPUT") a HTML (tema Codex/Alacritty)…"
pandoc "$ABS_INPUT" \
  -f markdown+raw_html-tex_math_dollars-tex_math_single_backslash \
  -t html5 -s \
  --embed-resources \
  --css "$CSS_PATH" \
  --highlight-style=pygments \
  -o "$HTML_OUT" \
  --metadata title="$BASENAME_NOEXT"

echo "✅ Hecho: $HTML_OUT"

