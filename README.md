# CodexRenderer — ODT/TXT → Markdown → HTML (tema Alacritty/Codex)

Render de notas/sesiones a **HTML oscuro estilo terminal** (Alacritty/Codex) a partir de `.odt` o `.txt`.
Aplica reglas semánticas para:
- **Bloques de código** (`\`\`\`kotlin`, `\`\`\`bash`, `\`\`\`json`, …).
- **Diffs**: líneas que empiezan por `+`/`-` → bloque `\`\`\`diff` (verde/rojo).
- **Pensamientos IA**: líneas que empiezan por `•` → verde + cursiva.

El CSS se **embebe** en el HTML final, por lo que se ve igual en cualquier carpeta.

---

## Requisitos

- **Python 3.10+**
- **Pandoc** (`sudo apt install -y pandoc`)
- Paquetes Python:
  - `odfpy` (para leer `.odt`)

### Instalación recomendada (venv)

```bash
cd ~/CodexRenderer
python3 -m venv venv
source venv/bin/activate
pip install -U pip odfpy
sudo apt install -y pandoc
chmod +x convert_codex.sh
```
### USO RÁPIDO

```bash
./convert_codex.sh samples/MiSesion.odt


> Si prefieres `requirements.txt`, sustituye `pip install -U pip odfpy` por:

> pip install -r requirements.txt
