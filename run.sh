#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="${SCRIPT_DIR}/thirdparty/vendor:${PYTHONPATH:-}"
: "${TKDND_LIBRARY:=${SCRIPT_DIR}/thirdparty/tkdnd/linux-x64}"
export TKDND_LIBRARY
exec python3 "${SCRIPT_DIR}/geminirenderer_gui.py" "$@"

