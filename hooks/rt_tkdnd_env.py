# hooks/rt_tkdnd_env.py
import os, sys
def _rp(*parts):
    base = getattr(sys, "_MEIPASS", os.path.dirname(__file__))
    return os.path.join(base, *parts)

# apunta al plugin TkDnD embebido en el bundle
tkdnd_dir = _rp("codexrenderer", "thirdparty", "tkdnd", "linux-x64")
if os.path.isdir(tkdnd_dir):
    os.environ.setdefault("TKDND_LIBRARY", tkdnd_dir)

