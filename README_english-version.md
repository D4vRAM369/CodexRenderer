# ⚡️ CodexRenderer — ODT/TXT → Markdown → HTML (Alacritty/Codex theme)

[🇪🇸 Versión en español](README.md)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-GPLv3-green)
![Platform](https://img.shields.io/badge/Platform-Linux-lightgrey)
![Made_with](https://img.shields.io/badge/Made_with-Love_&_Coffee-ff69b4)
[![coffee](https://img.shields.io/badge/Buy_me_a_coffee-☕-5F7FFF)](https://www.buymeacoffee.com/D4vRAM369)


<img width="891" height="620" alt="CodexRenderer preview" src="https://github.com/user-attachments/assets/aacffd84-bf30-455a-84c9-c46a8828b4b1" />


> 🧠 **Convert entire Codex CLI sessions copied and pasted** in `.odt` or `.txt` to **terminal-style dark HTML** (Alacritty/Codex).\
> Ideal for logs, AI prompts, technical journals or minimalist documentation.

---

## 📁 Project structure

```bash
CodexRenderer/
├── pyproject.toml
├── convert_codex.sh
├── convert_gemini.sh
├── run.sh
├── src/
│   └── codexrenderer/
│       ├── cli.py
│       ├── codex.py
│       ├── codexrenderer_gui.py
│       ├── gemini_cli.py
│       ├── geminirenderer_core.py
│       ├── geminirenderer_gui.py
│       ├── assets/
│       │   └── alacritty.css
│       └── thirdparty/
│           └── tkdnd/ …
├── tests/
│   ├── test_cli.py
│   └── test_gui_import.py
└── .github/workflows/
    ├── ci.yml
    └── release.yml
```

---

## 🧉 Description

CodexRenderer **renders notes/sessions** to HTML with a visual theme based on the *Alacritty* Terminal.
Applies automatic semantic rules on plain text or `.odt` documents to highlight content based on its function:

| Line type | Example | Rendering |
|----------------|----------|-------------|
| 🧠 **IA Thoughts** (`•`) | `• this is an internal idea` | *Green + italics* |
| 🟩 **Lines added** (`+`) | `+ new line added` | Green `diff` block |
| 🔴 **Lines removed** (`-`) | `-line removed` | Red `diff` block |
| 💻 **Code blocks** | `````bash ... ````` | Terminal style dark theme |

The **CSS is embedded directly** into the final HTML, guaranteeing the same appearance in any folder or system.

---

## 🌠 Extension: GeminiRenderer GUI

**GeminiRenderer** is the visual evolution of CodexRenderer, with a graphical interface (Tkinter + tkinterdnd2).

It allows you to convert via *Drag & Drop* or multiple selection (`.txt`, `.md`, `.odt`) to Markdown + HTML with the same **Codex/Alacritty** theme.

 ```bash
./run.sh --debug

📦 Additional Requirements:

sudo apt install -y python3-tk tkdnd pandoc

🧩 Vendorized Dependencies:

thirdparty/vendor/tkinterdnd2/

thirdparty/tkdnd/linux-x64/

---

## ⚙️ Requirements

- 🐍 **Python 3.10+**
- 📦 **Pandoc** 
```bash 
sudo apt install -y pandoc 
```
- 🔹 Python Packages: 
- [`odfpy`](https://pypi.org/project/odfpy/) → to read `.odt`

---

## 🧪 Recommended installation (virtual environment)

```bash
cd ~/CodexRenderer
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[gui]"
sudo apt install -y pandoc  # required to render HTML
```

Available commands after the editable install:

```bash
codexrenderer --help           # CLI ODT/TXT/MD → MD/HTML
geminirenderer --help          # Gemini-style CLI
geminirenderer-gui --debug     # Drag & drop GUI
codexrenderer-gui --debug      # Classic Codex GUI
```

### Handy CLI options
- `--md-only`: produces just the Markdown file (ideal when Pandoc is not present).
- `--inline-css/--no-inline-css`: toggle embedding the theme CSS at the top of the Markdown output.

---

## 🚀 Quick use

```bash
./convert_codex.sh samples/MySession.odt
```

Generated output:
- 📝 `MySession.md`
- 🌐 `MiSesion.html` (with embedded Alacritty/Codex theme)

---

## 🧠 Semantic rules (visual summary)

``markdown
• IA Thought → *<span class="ia-thought">green italic text</span>*

+ Added line
- Line removed
```bash
# Code block
echo "Hello, Codex!"
```
````

---

## 🤰 Batch conversion

Automatically convert all `.odt` and `.txt` in a folder:

```bash
find ./notes -type f \( -name '*.odt' -o -name '*.txt' \) -print0 \
| xargs -0 -I{} ./convert_codex.sh "{}"
```

---

## 🎨 Visual theme (Alacritty/Codex)

> 💚 Based on Alacritty's clean style, with a retro Matrix-like touch to the banner.

🖤 ​​Deep black background
💚 Neon green (`#00ff80`)
🧮 Monospaced typography
💿 Code highlighted with luminous borders

---

## 🗟️ License

**CodexRenderer** is licensed under [GNU GPL v3.0](./LICENSE).
This ensures that it remains **free software**, allowing forks, improvements and educational use without code closure.

**Bundled third-party components**
- `tkinterdnd2` (vendored for the GUI) – see `src/codexrenderer/thirdparty/vendor/tkinterdnd2-0.4.3.dist-info/LICENSE`.
- TkDND native binaries for drag & drop – redistributed under their original license in `src/codexrenderer/thirdparty/tkdnd/`.

---

## 💬 Credits

Created with 💻 and ☕ by **D4vRAM**
> “From raw text to living code — from mind to render.” 🧠⚡️

---

### 🧉 Tags

`#markdown` `#html` `#converter` `#terminal-theme` `#python` `#matrix` `#alacritty` `#opensource`

[![Buy Me a  Coffee](https://img.buymeacoffee.com/button-api/?text=Buy%20me%20a%20coffee&emoji=☕&slug=D4vRAM369&button_colour=5F7FFF& font_colour=ffffff&font_family=Inter&outline_colour=000000&coffee_colour=FFDD00)](https://www.buymeacoffee.com/D4vRAM369)
