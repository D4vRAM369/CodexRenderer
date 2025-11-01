# ⚡️ CodexRenderer — ODT/TXT → Markdown → HTML (Alacritty/Codex theme)

[🇪🇸 Versión en español](README.md)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-GPLv3-green)
![Platform](https://img.shields.io/badge/Platform-Linux-lightgrey)
![Made_with](https://img.shields.io/badge/Made_with-Love_&_Coffee-ff69b4)
[![coffee](https://img.shields.io/badge/Buy_me_a_coffee-☕-5F7FFF)](https://www.buymeacoffee.com/D4vRAM369)

<img width="891" height="620" alt="CodexRenderer preview" src="https://github.com/user-attachments/assets/aacffd84-bf30-455a-84c9-c46a8828b4b1" />

> 🧠 **Convert entire Codex CLI sessions pasted from `.odt` or `.txt`** into **terminal-style dark HTML** (Alacritty/Codex).  
> Built for logs, AI prompts, technical journals, or minimalist documentation.

---

## 🖼️ Visual examples

Screenshots from `sample.odt` processed by **CodexRenderer**, showcasing the final Alacritty-style dark HTML output.

<img width="2440" height="833" alt="image" src="https://github.com/user-attachments/assets/12e68318-5e65-450f-bd85-abe30ae78c39" />
<img width="2493" height="850" alt="image" src="https://github.com/user-attachments/assets/9f96fcfc-87b0-4d64-a33a-26ce6bcebd5d" />

---

## 📁 Project structure

```bash
CodexRenderer/
├── CodexRunner.spec
├── cli_entry.py
├── convert_codex.sh
├── convert_gemini.sh
├── gui_entry.py
├── pyproject.toml
├── requirements.txt
├── run.sh
├── src/
│   └── codexrenderer/
│       ├── __init__.py
│       ├── cli.py
│       ├── codex.py
│       ├── codexrenderer_gui.py
│       ├── gemini_cli.py
│       ├── geminirenderer_core.py
│       ├── geminirenderer_gui.py
│       ├── claudecode_cli.py
│       ├── claudecode_gui.py
│       ├── assets/
│       │   └── alacritty.css
│       └── thirdparty/
│           ├── tkdnd/ …
│           └── vendor/
│               └── tkinterdnd2/ …
├── thirdparty/
│   └── vendor/
│       └── tkinterdnd2/ …
├── tests/
│   ├── test_cli.py
│   └── test_gui_import.py
├── build/
├── dist/
└── .github/workflows/
    ├── ci.yml
    └── release.yml
```

---

## 🧉 Description

CodexRenderer **renders notes/sessions** to HTML with a visual theme inspired by the *Alacritty* terminal.  
It applies automatic semantic rules over plain text or `.odt` documents to highlight content based on its role:

| Line type                   | Example                       | Rendering                     |
|-----------------------------|-------------------------------|-------------------------------|
| 🧠 **IA Thoughts** (`•`)       | `• this is an internal idea`   | Green + italics               |
| 🟩 **Lines added** (`+`)       | `+ new line added`             | Green diff block              |
| 🔴 **Lines removed** (`-`)     | `- line removed`               | Red diff block                |
| 💻 **Code blocks**             | `````bash ... `````            | Terminal-style dark theme     |

The **CSS is embedded directly** into the generated HTML, ensuring identical visuals everywhere.

---

## 🌠 GUI extensions: GeminiRenderer & ClaudeCode

The **GeminiRenderer** and **ClaudeCodeRenderer** GUIs extend CodexRenderer with drag & drop support and tailored presets. Both share the vendored Tkinter + tkinterdnd2 stack and ship with the `run.sh` launcher.

- **GeminiRenderer GUI** adapts the Codex workflow to Gemini-style exports and pioneered the cross-platform TkDND integration.
- **ClaudeCode GUI** reuses the same conversion core with behavior tuned for Claude-based logs.

```bash
./run.sh --debug        # Auto-detects an available GUI and opens GeminiRenderer
codex-gemini --debug    # Launches the Gemini GUI
codex-claude --debug    # Launches the ClaudeCode GUI
```

📦 Additional requirements (for both GUIs):

```bash
sudo apt install -y python3-tk tkdnd pandoc
```

🧩 Vendored dependencies:

- `src/codexrenderer/thirdparty/vendor/tkinterdnd2/`
- `src/codexrenderer/thirdparty/tkdnd/<platform>/`
- `thirdparty/vendor/tkinterdnd2/` (support when running outside a venv)

---

## ⚙️ Requirements

- 🐍 **Python 3.10+**
- 📦 **Pandoc**
  ```bash
  sudo apt install -y pandoc
  ```
- 🔹 Python packages:
  - [`odfpy`](https://pypi.org/project/odfpy/) → `.odt` ingestion

---

## 🧪 Recommended installation (virtual environment)

```bash
cd ~/CodexRenderer
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[gui]"
sudo apt install -y pandoc  # required for HTML generation
```

Available commands after installing in editable mode:

```bash
codexrenderer --help           # CLI ODT/TXT/MD → MD/HTML
geminirenderer --help          # Gemini-styled CLI
geminirenderer-gui --debug     # Drag & drop GUI
codexrenderer-gui --debug      # Classic Codex GUI
claudecoderenderer --help      # Claude-styled CLI
claudecoderenderer-gui --debug # Claude GUI
codex-gemini --debug           # Gemini launcher alias
codex-claude --debug           # Claude launcher alias
```

### Handy CLI options

- `--md-only`: produce only Markdown (handy without Pandoc).
- `--inline-css/--no-inline-css`: toggle embedding the theme CSS at the top of the Markdown output.

---

## 🚀 Quick use

```bash
./convert_codex.sh ~/Documents/MySession.odt
```

Generated output:
- 📝 `MySession.md`
- 🌐 `MySession.html` (with embedded Alacritty/Codex theme)

---

## 🧠 Semantic rules (visual summary)

````markdown
• IA Thought → *<span class="ia-thought">green italic text</span>*

+ Added line
- Removed line
```bash
# Code block
echo "Hello, Codex!"
```
````

---

## 🤰 Batch conversion

Convert all `.odt` and `.txt` under a directory:

```bash
find ./notes -type f \( -name '*.odt' -o -name '*.txt' \) -print0 \
| xargs -0 -I{} ./convert_codex.sh "{}"
```

---

## 🎨 Visual theme (Alacritty/Codex)

> 💚 Inspired by Alacritty’s clean aesthetic, with a retro Matrix-style banner.

- 🖤 Deep black background 
- 💚 Neon green (`#00ff80`) 
- 🧮 Monospaced typography 
- 💿 Highlighted code with glowing borders 

---

## 📦 Packaging with PyInstaller (CodexRunner)

```bash
python -m pip install -r requirements.txt pyinstaller
pyinstaller CodexRunner.spec --clean --noconfirm
```

The executable is generated in `dist/CodexRunner/`. Compress that folder and attach it as an asset when drafting a release.

---

## 🗟️ License

**CodexRenderer** is released under [GNU GPL v3.0](./LICENSE), keeping the project open and fork-friendly.

**Bundled third-party components**
- Vendored `tkinterdnd2` (CLI/GUI and launcher): see `src/codexrenderer/thirdparty/vendor/tkinterdnd2-0.4.3.dist-info/LICENSE`.
- TkDND native binaries: redistributed in `src/codexrenderer/thirdparty/tkdnd/` and `thirdparty/vendor/tkinterdnd2/tkdnd/` under their original license.

---

## 🚢 Pre-release checklist

1. Update `pyproject.toml` and any banners to the target version.
2. Install development dependencies and run the full verification suite:
   ```bash
   python -m pip install -e ".[gui]" pytest ruff black build twine
   ruff check .
   black --check .
   pytest
   ```
3. Build distributables and validate metadata:
   ```bash
   python -m build
   twine check dist/*
   pyinstaller CodexRunner.spec --clean --noconfirm
   ```
4. Commit relevant changes (avoid checking in `venv/`, `out/`, or temporary binaries).
5. Tag the release (`git tag vX.Y.Z && git push --tags`) to trigger `release.yml`.
6. Review the auto-generated GitHub Release draft and add final release notes.

---

## 💬 Credits

Crafted with 💻 and ☕ by **D4vRAM**  
> “From raw text to living code — from mind to render.” 🧠⚡️

---

### 🧉 Tags

`#markdown` `#html` `#converter` `#terminal-theme` `#python` `#matrix` `#alacritty` `#opensource`

[![Buy Me a Coffee](https://img.buymeacoffee.com/button-api/?text=Buy%20me%20a%20coffee&emoji=☕&slug=D4vRAM369&button_colour=5F7FFF&font_colour=ffffff&font_family=Inter&outline_colour=000000&coffee_colour=FFDD00)](https://www.buymeacoffee.com/D4vRAM369)
