#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="${SCRIPT_DIR}/src${PYTHONPATH:+:$PYTHONPATH}"
: "${TKDND_LIBRARY:=${SCRIPT_DIR}/src/codexrenderer/thirdparty/tkdnd/linux-x64}"
export TKDND_LIBRARY
exec python3 -m codexrenderer.geminirenderer_gui "$@"
