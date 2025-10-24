#!/usr/bin/env bash
# --- Codex/Alacritty Workflow integrado ---
# Convierte .odt/.txt → .md (usando txt_odt_to_md.py)
# y luego .md → .html (usando Pandoc + CSS oscuro)
# Autor: D4vRAM (Brian) 🔥

INPUT="$1"
if [ -z "$INPUT" ]; then
  echo "Uso: ./convert_codex.sh archivo.odt | archivo.txt | archivo.md"
  exit 1
fi

EXT="${INPUT##*.}"
BASENAME="${INPUT%.*}"

# 1️⃣ Si el archivo es ODT o TXT → convertir a MD primero
if [[ "$EXT" == "odt" || "$EXT" == "txt" ]]; then
  echo "→ Convirtiendo $INPUT a Markdown..."
  python3 txt_odt_to_md.py "$INPUT" -o "${BASENAME}.md"
  INPUT="${BASENAME}.md"
fi

# 2️⃣ Crear CSS si no existe
CSS_FILE="alacritty.css"
if [ ! -f "$CSS_FILE" ]; then
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
.gi{color:#00e676}.gd{color:#ff5252}.ait,em{color:#00c853;font-style:italic}
h1,h2,h3{color:#e6e6e6;margin-top:1.2em}
CSS
fi

# 3️⃣ Convertir Markdown → HTML
echo "→ Renderizando ${INPUT} como HTML con estilo Codex..."
pandoc "$INPUT" \
  -f markdown+raw_html-tex_math_dollars-tex_math_single_backslash \
  -t html5 -s \
  --css "$CSS_FILE" \
  --highlight-style=pygments \
  -o "${BASENAME}.html" \
  --metadata title="${BASENAME}"

echo "✅ Hecho: ${BASENAME}.html"

