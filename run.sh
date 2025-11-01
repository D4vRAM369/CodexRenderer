#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="${SCRIPT_DIR}/thirdparty/vendor:${SCRIPT_DIR}/src${PYTHONPATH:+:$PYTHONPATH}"

if [ -z "${TKDND_LIBRARY:-}" ]; then
  if [ -d "${SCRIPT_DIR}/src/codexrenderer/thirdparty/tkdnd" ]; then
    TKDND_LIBRARY="${SCRIPT_DIR}/src/codexrenderer/thirdparty/tkdnd/linux-x64"
  elif [ -d "${SCRIPT_DIR}/thirdparty/tkdnd" ]; then
    TKDND_LIBRARY="${SCRIPT_DIR}/thirdparty/tkdnd/linux-x64"
  fi
fi

export TKDND_LIBRARY
exec python3 -m codexrenderer.geminirenderer_gui "$@"
