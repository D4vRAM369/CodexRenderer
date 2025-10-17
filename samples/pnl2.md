```
defcon@defcon-B450M-S2H:~/CodexRenderer$ # 1) Ir al proyecto (no a ~/venv/CodexRenderer, sino a ~/CodexRenderer)
```
cd ~/CodexRenderer

```
# 2) (si usas la lib odfpy en el venv) activar el venv
```
source venv/bin/activate  # si no existe, omite esta línea

\# 3) Ejecutar el pipeline sobre tu ODT
./convert_codex.sh "Codex_sesion_ScanYourStock.odt"
→ Convirtiendo Codex_sesion_ScanYourStock.odt a Markdown...
OK -> Codex_sesion_ScanYourStock.md
→ Renderizando Codex_sesion_ScanYourStock.md como HTML con estilo Codex...
✅ Hecho: Codex_sesion_ScanYourStock.html
```
(venv) defcon@defcon-B450M-S2H:~/CodexRenderer$ codex .
```

╭──────────────────────────────────────────────────╮
```
│ >_ OpenAI Codex (v0.46.0)                        │
```
│                                                  │
│ model:     gpt-5-codex medium   /model to change │
│ directory: ~/CodexRenderer                       │
╰──────────────────────────────────────────────────╯

  To get started, describe a task or try one of these commands:

  /init - create an AGENTS.md file with instructions for Codex
  /status - show current session configuration
  /approvals - choose what Codex can do without approval
  /model - choose what model and reasoning effort to use
  /review - review any changes and find issues

<span class="prompt">› .</span>

<span class="ait"><em>Explored └ List ls</em></span>

─ Worked for 7s ──────────────────────────────────────────────────────────────────────────────────────────────────────

<span class="ait"><em>Current directory files: alacritty.css, Codex_sesion_ScanYourStock.html, Codex_sesion_ScanYourStock.md, Codex_sesion_ScanYourStock.odt, convert_codex.sh, README.md, requirements.txt, txt_odt_to_md.py, and venv/. Let me know what you'd like to do next.</em></span>

<span class="prompt">› Dime en que se basa la codebase de este proyecto</span>

<span class="ait"><em>Explored └ Read README.md, convert_codex.sh, txt_odt_to_md.py, requirements.txt</em></span>

─ Worked for 11s ─────────────────────────────────────────────────────────────────────────────────────────────────────

<span class="ait"><em>El proyecto gira alrededor de una canalización de conversión de documentos centrada en Markdown y Pandoc:</em></span>

<span class="ait"><em>convert_codex.sh:1 orquesta el flujo completo: si recibe .odt o .txt llama a un script Python que genera Markdown</em></span>
```
    y, una vez obtenido, ejecuta Pandoc para producir HTML con una hoja de estilo oscura tipo terminal (Codex/
    Alacritty) que también crea si no existe.
```
<span class="ait"><em>txt_odt_to_md.py:1 es el núcleo: usa odfpy para leer .odt, detecta bloques de código o diffs con heurísticas,</em></span>
```
    aplica escapes necesarios y puede incrustar CSS cuando se solicita; siempre emite Markdown “limpio”.
```
<span class="ait"><em>requirements.txt:1 fija odfpy como dependencia única externa; el resto se basa en la biblioteca estándar y en</em></span>
```
    Pandoc instalado en el sistema.
```

  En conjunto, la base del código es una utilidad CLI que transforma notas en ODT/TXT hacia Markdown y luego a HTML
  con estética de terminal.

<span class="prompt">› Quiero que me digas como funciona en formato PBL</span>

<span class="ait"><em>Formato PBL</em></span>

<span class="ait"><em>Situación problema: Necesitas transformar rápidamente notas o reportes en .odt/.txt para presentarlos como HTML</em></span>
```
    con estética de terminal, sin perder fragmentos de código, diffs o bullets “de IA”.
```
<span class="ait"><em>Producto esperado: Página HTML oscura estilo Codex/Alacritty que conserva formato Markdown y resaltado de código,</em></span>
```
    generada automáticamente a partir de un único archivo fuente.
```
<span class="ait"><em>Preguntas guía: ¿Cómo automatizar la lectura de .odt y .txt? ¿Cómo detectar y formatear código/diffs en Markdown?</em></span>
```
    ¿Cómo acoplar todo con una conversión a HTML estéticamente consistente?
  - Plan de trabajo: (1) Ejecutar convert_codex.sh archivo.ext. (2) Si el archivo es .odt/.txt, txt_odt_to_md.py lo
    convierte a Markdown aplicando heurísticas para bloques de código, listas y diffs. (3) Generar alacritty.css si no
    existe. (4) Llamar a Pandoc para renderear *.md a HTML con el CSS y Pygments.
  - Recursos clave: Script Bash convert_codex.sh, script Python txt_odt_to_md.py, librería odfpy (en requirements.txt)
    para leer ODT, Pandoc instalado en el sistema.
  - Criterios de evaluación: El HTML final debe mantener el formato original (código, diffs, bullets), aplicar el tema
    oscuro, y el flujo completo debe ejecutarse con un solo comando sobre archivos .odt, .txt o .md.
```

<span class="prompt">› ¿Que es Pandoc?¿Y como es posible?</span>

<span class="ait"><em>Pandoc es un conversor universal de documentos en línea de comandos. Soporta un gran número de formatos de entrada</em></span>
```
  y salida (Markdown, HTML, LaTeX, ODT, DOCX, PDF vía LaTeX, etc.) y se encarga de parsear el documento fuente a una
```
  representación intermedia para después reconstruirlo en el formato destino.

  Es posible porque Pandoc implementa parsers y generadores para cada formato que entiende. Cuando le pides, por
  ejemplo, “Markdown → HTML”, lee el Markdown, lo transforma a su estructura interna abstracta (un árbol de bloques
  e inlines), y a partir de ahí lo serializa como HTML aplicando las reglas concretas del formato objetivo. Gracias
  a ese núcleo intermedio puede encadenar casi cualquier conversión entre formatos soportados sin que tengas que
  escribir tú los pasos intermedios.

<span class="prompt">› dame un script o comando para inyectar un archivo en otro usando criptografía, y damelo su equivalente no solo en</span>
  Python o Bash, también Kotlin, Java, C, C+, C#, JavaScript si es posible y cualquiera que se te ocurra, y explica el
  workflow con enfoque PBL

<span class="ait"><em>Presenting cryptographic embedding snippets</em></span>

  I’m preparing concise but functional code snippets for embedding an encrypted file into a carrier file using AES-GCM
  and base64-encoded JSON metadata, showing the core embedding logic and noting required libraries across languages
  like Kotlin, Java, Python, Bash, and more. This way, the user gets practical examples with consistent format markers
  and clear workflow guidance.

─ Worked for 54s ─────────────────────────────────────────────────────────────────────────────────────────────────────

<span class="ait"><em>Idea General</em></span>

<span class="ait"><em>Genera una clave simétrica derivada de una contraseña con PBKDF2 para evitar claves débiles repetidas.</em></span>
<span class="ait"><em>Cifra el archivo a incrustar (payload) con AES-GCM o AES-CBC+HMAC, de modo que el contenido quede ilegible sin</em></span>
```
    la clave.
  - Codifica el resultado (por ejemplo en Base64) y lo agrega al archivo contenedor junto con metadatos (salt, IV,
    tag) entre marcadores reconocibles.
```
<span class="ait"><em>Para extraer, el mismo esquema lee los marcadores, decodifica, verifica el tag y descifra usando la misma</em></span>
```
    contraseña.
```

```
  Implementaciones (ejemplo marcador <!--BEGIN_EMBED-->)
```

```python
  Python (requiere cryptography):
```

```python
  #!/usr/bin/env python3
  import base64, hashlib, json, secrets, sys
  from pathlib import Path
  from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
  from cryptography.hazmat.primitives import hashes
  from cryptography.hazmat.primitives.ciphers.aead import AESGCM
```

  MARK_BEGIN = "\n<!--BEGIN_EMBED-->\n"
  MARK_END = "\n<!--END_EMBED-->\n"

```python
  def derive_key(passphrase: str, salt: bytes) -> bytes:
      kdf = PBKDF2HMAC(
          algorithm=hashes.SHA256(), length=32,
          salt=salt, iterations=120_000,
      )
      return kdf.derive(passphrase.encode())
```

```json
  def embed(payload, carrier, out, passphrase):
      salt = secrets.token_bytes(16)
      iv = secrets.token_bytes(12)
      key = derive_key(passphrase, salt)
      cipher = AESGCM(key)
      ciphertext = cipher.encrypt(iv, Path(payload).read_bytes(), None)
      blob = {
          "alg": "AES/GCM/NoPadding",
          "salt": base64.b64encode(salt).decode(),
          "iv": base64.b64encode(iv).decode(),
          "data": base64.b64encode(ciphertext).decode(),
      }
      with open(out, "wb") as fh:
          fh.write(Path(carrier).read_bytes())
          fh.write(MARK_BEGIN.encode())
          fh.write(json.dumps(blob, separators=(",", ":")).encode())
          fh.write(MARK_END.encode())
```

  if __name__ == "__main__":
```python
      if len(sys.argv) != 5:
          raise SystemExit("Uso: python embed.py payload.bin carrier.bin salida.bin 'pass'")
      embed(*sys.argv[1:4], passphrase=sys.argv[4])
```

```python
  Bash (usa openssl + base64):
```

```
  #!/usr/bin/env bash
```
  set -euo pipefail
```
  payload="$1"; carrier="$2"; out="$3"; pass="$4"
```

```
  tmp=$(mktemp)
```
  openssl enc -aes-256-cbc -pbkdf2 -salt -pass pass:"$pass" -in "$payload" -out "$tmp"
  {
```
    cat "$carrier"
    echo ""
    echo "<!--BEGIN_EMBED-->"
    echo "alg=openssl-aes-256-cbc"
    echo -n "data="
    base64 < "$tmp" | tr -d '\n'
    echo ""
    echo "<!--END_EMBED-->"
```
  } > "$out"
  rm "$tmp"

```python
  Kotlin (JVM estándar):
```

```python
  import java.nio.file.*
  import java.security.SecureRandom
  import java.util.Base64
  import javax.crypto.Cipher
  import javax.crypto.SecretKeyFactory
  import javax.crypto.spec.GCMParameterSpec
  import javax.crypto.spec.PBEKeySpec
  import javax.crypto.spec.SecretKeySpec
```

```kotlin
  fun embed(payloadPath: String, carrierPath: String, outPath: String, passphrase: String) {
      val payload = Files.readAllBytes(Path.of(payloadPath))
      val carrier = Files.readAllBytes(Path.of(carrierPath))
      val random = SecureRandom()
```

```kotlin
      val salt = ByteArray(16).also(random::nextBytes)
      val iv = ByteArray(12).also(random::nextBytes)
```

```kotlin
      val factory = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256")
      val spec = PBEKeySpec(passphrase.toCharArray(), salt, 120_000, 256)
      val secret = SecretKeySpec(factory.generateSecret(spec).encoded, "AES")
```

```kotlin
      val cipher = Cipher.getInstance("AES/GCM/NoPadding")
      cipher.init(Cipher.ENCRYPT_MODE, secret, GCMParameterSpec(128, iv))
      val cipherText = cipher.doFinal(payload)
```

```kotlin
      val blob = """
```
  {"alg":"AES/GCM/
```json
  NoPadding","salt":"${Base64.getEncoder().encodeToString(salt)}","iv":"${Base64.getEncoder().encodeToString(iv)}","da
  ta":"${Base64.getEncoder().encodeToString(cipherText)}"}
  """.trim()
```

```
      Files.write(Path.of(outPath), carrier +
          "\n<!--BEGIN_EMBED-->\n".toByteArray() +
          blob.toByteArray() +
          "\n<!--END_EMBED-->\n".toByteArray()
      )
```
  }

```python
  Java (idéntico a Kotlin pero en clase):
```

```java
  import java.nio.file.*;
  import java.security.SecureRandom;
  import java.util.Base64;
  import javax.crypto.*;
  import javax.crypto.spec.*;
```

```java
  public class Embedder {
      private static byte[] deriveKey(char[] pass, byte[] salt) throws Exception {
          SecretKeyFactory f = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256");
          PBEKeySpec spec = new PBEKeySpec(pass, salt, 120_000, 256);
          return f.generateSecret(spec).getEncoded();
      }
```

```java
      public static void embed(String payload, String carrier, String out, String passphrase) throws Exception {
          byte[] data = Files.readAllBytes(Path.of(payload));
          byte[] container = Files.readAllBytes(Path.of(carrier));
          SecureRandom rng = new SecureRandom();
          byte[] salt = rng.generateSeed(16);
          byte[] iv = rng.generateSeed(12);
```

```java
          SecretKeySpec key = new SecretKeySpec(deriveKey(passphrase.toCharArray(), salt), "AES");
          Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
          cipher.init(Cipher.ENCRYPT_MODE, key, new GCMParameterSpec(128, iv));
          byte[] ct = cipher.doFinal(data);
```

```java
          String blob = String.format(
              "{\"alg\":\"AES/GCM/NoPadding\",\"salt\":\"%s\",\"iv\":\"%s\",\"data\":\"%s\"}",
              Base64.getEncoder().encodeToString(salt),
              Base64.getEncoder().encodeToString(iv),
              Base64.getEncoder().encodeToString(ct)
          );
          Files.write(Path.of(out),
              concatenate(container, ("\n<!--BEGIN_EMBED-->\n" + blob + "\n<!--END_EMBED-->\n").getBytes())
          );
      }
```

```java
      private static byte[] concatenate(byte[] a, byte[] b) {
          byte[] r = new byte[a.length + b.length];
          System.arraycopy(a, 0, r, 0, a.length);
          System.arraycopy(b, 0, r, a.length, b.length);
          return r;
      }
```
  }

```python
  C (OpenSSL EVP):
```

  #include <openssl/evp.h>
  #include <openssl/rand.h>
  #include <stdio.h>
  #include <stdlib.h>

```java
  int main(int argc, char **argv) {
      if (argc != 5) { fprintf(stderr, "Uso: embed payload carrier out pass\n"); return 1; }
      FILE *fp = fopen(argv[1], "rb");
      FILE *fc = fopen(argv[2], "rb");
      FILE *fo = fopen(argv[3], "wb");
      if (!fp || !fc || !fo) { perror("open"); return 1; }
```

```java
      fseek(fp, 0, SEEK_END); long plen = ftell(fp); rewind(fp);
      unsigned char *payload = malloc(plen); fread(payload, 1, plen, fp);
```

```java
      unsigned char salt[16], iv[12];
      RAND_bytes(salt, sizeof salt);
      RAND_bytes(iv, sizeof iv);
```

```java
      unsigned char key[32];
      PKCS5_PBKDF2_HMAC(argv[4], strlen(argv[4]), salt, sizeof salt, 120000, EVP_sha256(), sizeof key, key);
```

```java
      EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
      EVP_EncryptInit_ex(ctx, EVP_aes_256_gcm(), NULL, NULL, NULL);
      EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_IVLEN, sizeof iv, NULL);
      EVP_EncryptInit_ex(ctx, NULL, NULL, key, iv);
```

```java
      int outlen;
      unsigned char *cipher = malloc(plen + 16);
      EVP_EncryptUpdate(ctx, cipher, &outlen, payload, plen);
      int total = outlen;
      EVP_EncryptFinal_ex(ctx, cipher + total, &outlen); total += outlen;
```

```java
      unsigned char tag[16];
      EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_GET_TAG, sizeof tag, tag);
```

```java
      // write carrier
      int c; while ((c = fgetc(fc)) != EOF) fputc(c, fo);
      fprintf(fo, "\n<!--BEGIN_EMBED-->\n");
      // base64 via openssl BIO for brevity omitted, assume helper
      // ...
      fprintf(fo, "\n<!--END_EMBED-->\n");
      // cleanup omitted
      return 0;
```
  }

```
  (Completar con BIO_f_base64 o librería favorita para serializar salt, iv, cipher, tag en Base64).
```

```python
  C++ (mismo concepto con OpenSSL o libsodium):
```

  // Requiere OpenSSL y C++17
  #include <openssl/evp.h>
  #include <openssl/rand.h>
  #include <filesystem>
  #include <fstream>
  #include <vector>

```java
  std::string b64(const std::vector<unsigned char>& in);
```

  void embed(const std::string& payload, const std::string& carrier,
```java
             const std::string& out, const std::string& pass) {
      std::vector<unsigned char> data(std::filesystem::file_size(payload));
      std::ifstream(payload, std::ios::binary).read(reinterpret_cast<char*>(data.data()), data.size());
      std::ifstream carrierFile(carrier, std::ios::binary);
      std::ofstream outFile(out, std::ios::binary);
```

```java
      std::vector<unsigned char> salt(16), iv(12);
      RAND_bytes(salt.data(), salt.size());
      RAND_bytes(iv.data(), iv.size());
```

```java
      std::vector<unsigned char> key(32);
      PKCS5_PBKDF2_HMAC(pass.c_str(), pass.size(), salt.data(), salt.size(),
                        120000, EVP_sha256(), key.size(), key.data());
```

```java
      EVP_CIPHER_CTX* ctx = EVP_CIPHER_CTX_new();
      EVP_EncryptInit_ex(ctx, EVP_aes_256_gcm(), nullptr, nullptr, nullptr);
      EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_IVLEN, iv.size(), nullptr);
      EVP_EncryptInit_ex(ctx, nullptr, nullptr, key.data(), iv.data());
```

```java
      std::vector<unsigned char> cipher(data.size() + 16);
      int len = 0, total = 0;
      EVP_EncryptUpdate(ctx, cipher.data(), &len, data.data(), data.size()); total += len;
      EVP_EncryptFinal_ex(ctx, cipher.data() + total, &len); total += len;
      cipher.resize(total);
      std::vector<unsigned char> tag(16);
      EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_GET_TAG, tag.size(), tag.data());
      EVP_CIPHER_CTX_free(ctx);
```

```java
      outFile << carrierFile.rdbuf();
      outFile << "\n<!--BEGIN_EMBED-->\n";
      outFile << "{\"alg\":\"AES/GCM/NoPadding\",\"salt\":\"" << b64(salt)
              << "\",\"iv\":\"" << b64(iv) << "\",\"tag\":\"" << b64(tag)
              << "\",\"data\":\"" << b64(cipher) << "\"}\n";
      outFile << "<!--END_EMBED-->\n";
```
  }

```python
  C# (.NET 6+):
```

  using System;
  using System.IO;
  using System.Security.Cryptography;
  using System.Text;
  using System.Text.Json;

```java
  class Embedder {
      public static void Embed(string payload, string carrier, string output, string passphrase) {
          byte[] data = File.ReadAllBytes(payload);
          byte[] carrierBytes = File.ReadAllBytes(carrier);
```

```java
          byte[] salt = RandomNumberGenerator.GetBytes(16);
          byte[] key = new Rfc2898DeriveBytes(passphrase, salt, 120_000,
                            HashAlgorithmName.SHA256).GetBytes(32);
```

```java
          using var aes = new AesGcm(key);
          byte[] nonce = RandomNumberGenerator.GetBytes(12);
          byte[] cipher = new byte[data.Length];
          byte[] tag = new byte[16];
          aes.Encrypt(nonce, data, cipher, tag);
```

```java
          var blob = new {
              alg = "AES/GCM/NoPadding",
              salt = Convert.ToBase64String(salt),
              iv = Convert.ToBase64String(nonce),
              tag = Convert.ToBase64String(tag),
              data = Convert.ToBase64String(cipher)
          };
          using var fs = new FileStream(output, FileMode.Create, FileAccess.Write);
          fs.Write(carrierBytes);
          var marker = Encoding.UTF8.GetBytes("\n<!--BEGIN_EMBED-->\n" +
              JsonSerializer.Serialize(blob) + "\n<!--END_EMBED-->\n");
          fs.Write(marker);
      }
```
  }

```python
  JavaScript (Node.js):
```

```java
  #!/usr/bin/env node
  const fs = require('node:fs');
  const crypto = require('node:crypto');
```

```java
  const [payload, carrier, out, passphrase] = process.argv.slice(2);
  if (!out) {
    console.error('Uso: node embed.js payload carrier salida pass');
    process.exit(1);
```
  }
```java
  const data = fs.readFileSync(payload);
  const carrierData = fs.readFileSync(carrier);
```

```java
  const salt = crypto.randomBytes(16);
  const key = crypto.pbkdf2Sync(passphrase, salt, 120000, 32, 'sha256');
  const iv = crypto.randomBytes(12);
  const cipher = crypto.createCipheriv('aes-256-gcm', key, iv);
  const encrypted = Buffer.concat([cipher.update(data), cipher.final()]);
  const tag = cipher.getAuthTag();
```

```java
  const blob = JSON.stringify({
    alg: 'AES/GCM/NoPadding',
    salt: salt.toString('base64'),
    iv: iv.toString('base64'),
    tag: tag.toString('base64'),
    data: encrypted.toString('base64')
  });
```

  fs.writeFileSync(out,
```java
    Buffer.concat([
      carrierData,
      Buffer.from(`\n<!--BEGIN_EMBED-->\n${blob}\n<!--END_EMBED-->\n`)
    ])
  );
```

  Workflow PBL

<span class="ait"><em>Situación problema: proteger un archivo sensible ocultándolo dentro de otro y que solo usuarios autorizados puedan</em></span>
```
    recuperarlo.
```
<span class="ait"><em>Producto esperado: archivo contenedor que incluya el payload cifrado, con script/commandos portables para generar</em></span>
```
    y posteriormente extraer el contenido.
```
<span class="ait"><em>Preguntas guía: ¿Cómo derivo claves robustas desde una contraseña? ¿Qué modo de cifrado autenticado necesito?</em></span>
```
    ¿Cómo serializo salt/IV/tag para reutilizar el payload? ¿Qué marcadores simplifican la extracción?
  - Plan de trabajo: (1) Diseñar formato contenedor (marcadores + JSON/base64). (2) Implementar derivación de clave +
    cifrado (ejemplos anteriores). (3) Adjuntar al contenedor; documentar extracción inversa. (4) Probar con archivos
    pequeños y verificar que la autenticación detecta contraseñas incorrectas.
  - Recursos clave: Librerías crypto estándar (OpenSSL, cryptography, JCA), utilidades CLI (openssl, base64),
    documentación PBKDF2/AES-GCM, cualquier lenguaje con APIs equivalentes.
```
<span class="ait"><em>Criterios de evaluación: El payload solo se recupera con la contraseña; el contenedor permanece aceptable</em></span>
```
    para su uso original; el flujo es reproducible cross-lenguaje (mismo marcador+JSON); se documenta extracción
    y validaciones.
```

  Posibles siguientes pasos:

  1. Crear el script inverso de extracción/verificación en cada lenguaje para cerrar el ciclo.
  2. Automatizar pruebas con un archivo de muestra y validar integridad tras cifrar/descifrar.

<span class="prompt">› Y dime como ejecutar cada uno de ellos</span>

<span class="ait"><em>- Python: guardar el código en embed.py, instalar cryptography (pip install cryptography) y ejecutar python3</em></span>
```
    embed.py payload.bin carrier.txt salida.txt 'contraseña'.
  - Bash: guardar en embed.sh, dar permisos (chmod +x embed.sh), asegurarse de tener OpenSSL y usar ./embed.sh
    payload.bin carrier.txt salida.txt 'contraseña'.
```
<span class="ait"><em>Kotlin: compilar con kotlinc Embed.kt -include-runtime -d embed.jar; ejecutar java -jar embed.jar payload.bin</em></span>
```
    carrier.txt salida.txt 'contraseña'.
```
<span class="ait"><em>Java: compilar javac Embedder.java; ejecutar java Embedder payload.bin carrier.txt salida.txt 'contraseña'. - C: compilar cc embed.c -lcrypto -o embed; ejecutar ./embed payload.bin carrier.txt salida.txt 'contraseña'. - C++: compilar c++ embed.cpp -lcrypto -std=c++17 -o embed; ejecutar ./embed payload.bin carrier.txt salida.txt</em></span>
```
    'contraseña'.
  - C#: compilar dotnet new console -n EmbedApp (o usar csc Embedder.cs) y luego dotnet run --project EmbedApp
    payload.bin carrier.txt salida.txt 'contraseña'.
  - JavaScript (Node.js): guardar como embed.js, hacer chmod +x embed.js opcional y ejecutar node embed.js payload.bin
    carrier.txt salida.txt 'contraseña'.
```

  Siguientes pasos naturales:

  1. Implementar el script inverso de extracción en cada lenguaje para validar el embed.
  2. Probar el flujo con archivos pequeños y verificar la integridad tras extraer y comparar con el original.
