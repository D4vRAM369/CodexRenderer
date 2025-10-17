# ⚡️ CodexRenderer — ODT/TXT → Markdown → HTML (tema Alacritty/Codex)
[🌍 English version](README_english-version.md)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-GPLv3-green)
![Platform](https://img.shields.io/badge/Platform-Linux-lightgrey)
![Made_with](https://img.shields.io/badge/Made_with-Love_&_Coffee-ff69b4)
[![coffee](https://img.shields.io/badge/Buy_me_a_coffee-☕-5F7FFF)](https://www.buymeacoffee.com/D4vRAM369)


<img width="891" height="620" alt="CodexRenderer preview" src="https://github.com/user-attachments/assets/aacffd84-bf30-455a-84c9-c46a8828b4b1" />

> 🧠 **Convierte sesiones enteras de Codex en CLI copiadas y pegadas** en `.odt` o `.txt` a un **HTML oscuro estilo terminal** (Alacritty/Codex).\
> Ideal para logs, prompts de IA, diarios técnicos o documentación minimalista.

---

## 📁 Estructura del proyecto

```bash
CodexRenderer/
├── README.md
├── requirements.txt
├── convert_codex.sh
├── codex_renderer.py
├── themes/
│   └── codex.css
├── samples/
│   ├── MiSesion.odt
│   └── ejemplo.txt
├── .gitignore
└── .github/
    └── workflows/
        └── ci.yaml
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
python3 -m venv venv
source venv/bin/activate
pip install -U pip odfpy
sudo apt install -y pandoc
chmod +x convert_codex.sh
```

> 💡 También puedes usar `requirements.txt`:
> ```bash
> pip install -r requirements.txt
> ```

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

---

## 💬 Créditos

Creado con 💻 y ☕ por **D4vRAM**  
> “Del texto crudo al código vivo — de la mente al render.” 🧠⚡️

---

### 🧉 Etiquetas

`#markdown` `#html` `#converter` `#terminal-theme` `#python` `#matrix` `#alacritty` `#opensource`

[![Buy Me a Coffee](https://img.buymeacoffee.com/button-api/?text=Buy%20me%20a%20coffee&emoji=☕&slug=D4vRAM369&button_colour=5F7FFF&font_colour=ffffff&font_family=Inter&outline_colour=000000&coffee_colour=FFDD00)](https://www.buymeacoffee.com/D4vRAM369)
