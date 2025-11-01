# ⚡️ CodexRenderer — ODT/TXT → Markdown → HTML (tema Alacritty/Codex)
[🌍 English version](README_english-version.md)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-GPLv3-green)
![Platform](https://img.shields.io/badge/Platform-Linux-lightgrey)
![Made_with](https://img.shields.io/badge/Made_with-Love_&_Coffee-ff69b4)
[![coffee](https://img.shields.io/badge/Buy_me_a_coffee-☕-5F7FFF)](https://www.buymeacoffee.com/D4vRAM369)

<img width="891" height="620" alt="CodexRenderer preview" src="https://github.com/user-attachments/assets/aacffd84-bf30-455a-84c9-c46a8828b4b1" />

> 🧠 **Convierte sesiones enteras de Codex en CLI copiadas y pegadas** en `.odt` o `.txt` a un **HTML oscuro estilo terminal** (Alacritty/Codex).  
> Ideal para logs, prompts de IA, diarios técnicos o documentación minimalista.

---

## 🖼️ Ejemplos visuales 

Capturas de un archivo `sample.odt` procesado por **CodexRenderer**, mostrando el resultado final en HTML oscuro estilo Alacritty.

<img width="2440" height="833" alt="image" src="https://github.com/user-attachments/assets/12e68318-5e65-450f-bd85-abe30ae78c39" />
<img width="2493" height="850" alt="image" src="https://github.com/user-attachments/assets/9f96fcfc-87b0-4d64-a33a-26ce6bcebd5d" />

---

## 📁 Estructura del proyecto

```bash
CodexRenderer/
├── pyproject.toml
├── convert_codex.sh
├── convert_gemini.sh
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
│       ├── assets/
│       │   └── alacritty.css
│       └── thirdparty/
│           └── tkdnd/ … (vendorizado)
├── tests/
│   ├── test_cli.py
│   └── test_gui_import.py
└── .github/workflows/
    ├── ci.yml
    └── release.yml
```

---

## 🧉 Descripción

CodexRenderer **renderiza notas/sesiones** a HTML con un tema visual basado en la Terminal *Alacritty*.  
Aplica reglas semánticas automáticas sobre el texto plano o documentos `.odt` para resaltar contenido según su función:

| Tipo de línea | Ejemplo | Renderizado |
|----------------|----------|-------------|
| 🧠 **Pensamientos IA** (`•`) | `• esto es una idea interna` | *Verde + cursiva* |
| 🟩 **Líneas añadidas** (`+`) | `+ nueva línea añadida` | Bloque `diff` verde |
| 🔴 **Líneas eliminadas** (`-`) | `- línea eliminada` | Bloque `diff` rojo |
| 💻 **Bloques de código** | `````bash ... ````` | Tema oscuro estilo terminal |

El **CSS se embebe directamente** en el HTML final, garantizando un mismo aspecto en cualquier carpeta o sistema.

---

## 🌠 Extensión: GeminiRenderer GUI

**GeminiRenderer** es la evolución visual de CodexRenderer, con interfaz gráfica (Tkinter + tkinterdnd2).  
Permite convertir por *Drag & Drop* o selección múltiple (`.txt`, `.md`, `.odt`) a Markdown + HTML con el mismo tema **Codex/Alacritty**.

```bash
./run.sh --debug

📦 Requisitos adicionales:

sudo apt install -y python3-tk tkdnd pandoc


🧩 Dependencias vendorizadas:

thirdparty/vendor/tkinterdnd2/

thirdparty/tkdnd/linux-x64/

---


## ⚙️ Requisitos

- 🐍 **Python 3.10+**
- 📦 **Pandoc**
  ```bash
  sudo apt install -y pandoc
  ```
- 🔹 Paquetes Python:
  - [`odfpy`](https://pypi.org/project/odfpy/) → para leer `.odt`

---

## 🧪 Instalación recomendada (entorno virtual)

```bash
cd ~/CodexRenderer
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[gui]"
sudo apt install -y pandoc  # requerido para generar HTML
```

Comandos disponibles tras la instalación editable:

```bash
codexrenderer --help           # CLI ODT/TXT/MD → MD/HTML
geminirenderer --help          # CLI estilo Gemini
geminirenderer-gui --debug     # GUI con drag & drop
codexrenderer-gui --debug      # GUI clásica (Codex)
```

### Opciones CLI útiles
- `--md-only`: crea únicamente el `.md` (útil en entornos sin Pandoc instalado).
- `--inline-css/--no-inline-css`: controla si el CSS del tema se embebe al inicio del Markdown.

---

## 🚀 Uso rápido

```bash
./convert_codex.sh samples/MiSesion.odt
```

Salida generada:
- 📝 `MiSesion.md`
- 🌐 `MiSesion.html` (con tema Alacritty/Codex embebido)

---

## 🧠 Reglas semánticas (resumen visual)

````markdown
• Pensamiento IA → *<span class="ia-thought">texto verde en cursiva</span>*

+ Línea añadida
- Línea eliminada
```bash
# Bloque de código
echo "Hello, Codex!"
```
````

---

## 🤰 Conversión por lotes

Convierte automáticamente todos los `.odt` y `.txt` de una carpeta:

```bash
find ./notas -type f \( -name '*.odt' -o -name '*.txt' \) -print0 \
| xargs -0 -I{} ./convert_codex.sh "{}"
```

---

## 🎨 Tema visual (Alacritty/Codex)

> 💚 Basado en el estilo limpio de Alacritty, con un toque retro tipo Matrix en el banner.

🖤 Fondo negro profundo  
💚 Verde neón (`#00ff80`)  
🧮 Tipografía monoespaciada    
💿 Código resaltado con bordes luminosos  

---

## 🗟️ Licencia

**CodexRenderer** está licenciado bajo [GNU GPL v3.0](./LICENSE).  
Esto garantiza que siga siendo **software libre**, permitiendo forks, mejoras y uso educativo sin cierre de código.

**Componentes de terceros incluidos**
- `tkinterdnd2` (vendorizado para la GUI): licencia en `src/codexrenderer/thirdparty/vendor/tkinterdnd2-0.4.3.dist-info/LICENSE`.
- TkDND (binarios nativos para arrastrar y soltar): archivos redistribuidos en `src/codexrenderer/thirdparty/tkdnd/` siguiendo su licencia original.

---

## 🚢 Checklist previa a un release

Para publicar una nueva versión en GitHub y PyPI:

1. Actualiza `pyproject.toml` y cualquier banner en el código con el número de versión deseado.
2. Instala dependencias de desarrollo y ejecuta la verificación completa:
   ```bash
   python -m pip install -e ".[gui]" pytest ruff black build twine
   ruff check .
   black --check .
   pytest
   ```
3. Genera los artefactos y valida metadatos:
   ```bash
   python -m build
   twine check dist/*
   ```
4. Haz commit de los cambios relevantes (evita subir `venv/`, `out/` o binarios temporales).
5. Etiqueta la versión (`git tag vX.Y.Z && git push --tags`) para disparar el workflow `release.yml`.
6. Revisa el draft automáticamente creado en GitHub Releases y añade notas de cambios antes de publicarlo.

---

## 💬 Créditos

Creado con 💻 y ☕ por **D4vRAM**  
> “Del texto crudo al código vivo — de la mente al render.” 🧠⚡️

---

### 🧉 Etiquetas

`#markdown` `#html` `#converter` `#terminal-theme` `#python` `#matrix` `#alacritty` `#opensource`

[![Buy Me a Coffee](https://img.buymeacoffee.com/button-api/?text=Buy%20me%20a%20coffee&emoji=☕&slug=D4vRAM369&button_colour=5F7FFF&font_colour=ffffff&font_family=Inter&outline_colour=000000&coffee_colour=FFDD00)](https://www.buymeacoffee.com/D4vRAM369)
