#!/usr/bin/env bash
set -euo pipefail
# Ejecuta el launcher desde el árbol fuente sin instalar.
PYTHON="${PYTHON:-python3}"
export PYTHONPATH="$(pwd)/src${PYTHONPATH:+:${PYTHONPATH}}"
exec "$PYTHON" -m codexrenderer.launcher "$@"

