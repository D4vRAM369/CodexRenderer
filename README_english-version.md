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
├── README.md
├── requirements.txt
├── convert_codex.sh
├── codex_renderer.py
├── themes/
│ └── codex.css
├── samples/
│ ├── MySession.odt
│ └── example.txt
├── .gitignore
└── .github/ 
└── workflows/ 
└── ci.yaml
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
python3 -m venv venv
source venv/bin/activate
pip install -U pip odfpy
sudo apt install -y pandoc
chmod +x convert_codex.sh
```

> 💡 You can also use `requirements.txt`:
> ```bash
> pip install -r requirements.txt
> ```

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

---

## 💬 Credits

Created with 💻 and ☕ by **D4vRAM**
> “From raw text to living code — from mind to render.” 🧠⚡️

---

### 🧉 Tags

`#markdown` `#html` `#converter` `#terminal-theme` `#python` `#matrix` `#alacritty` `#opensource`

[![Buy Me a  Coffee](https://img.buymeacoffee.com/button-api/?text=Buy%20me%20a%20coffee&emoji=☕&slug=D4vRAM369&button_colour=5F7FFF& font_colour=ffffff&font_family=Inter&outline_colour=000000&coffee_colour=FFDD00)](https://www.buymeacoffee.com/D4vRAM369)
