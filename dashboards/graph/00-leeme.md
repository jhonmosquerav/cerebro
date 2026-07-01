---
title: Lente de grafo (render interactivo) — léeme
type: meta
---

# Lente de grafo de CEREBRO (capa opcional, removible)

Render **interactivo** del grafo de conocimiento, complementario a los dashboards Dataview y al
reporte estático. Usa una herramienta externa —[graphify](https://github.com/safishamsi/graphify)—
como *lente*: produce un grafo de nodos clicable a partir de tus páginas de `wiki/`.

> **Es una lente, no la verdad.** Su salida vive en `graphify-out/` (gitignored, regenerable) y
> **nunca** se importa a `wiki/` ni a `genome/`. Si borras graphify, CEREBRO funciona igual.
> Regla: [[gen-visualizacion]]. Operación analítica asociada: [[gen-graph-lens]] (`GRAPH`).

## Principios que debes respetar (no negociables)

1. **Confidencialidad** ([[gen-confidencialidad]]): graphify **no** ve páginas
   `sensibilidad: confidencial`. Se garantiza **controlando la entrada** (staging filtrado), no
   confiando en un flag.
2. **Backend a tu elección**: `claude` (conexión Claude Code), `local` (Ollama) o `structural`
   (sin LLM), registrado en `graph_lens.backend` del manifiesto y preguntado una vez. El invariante
   no es el backend: es que **lo `confidencial` nunca entra a la lente**.
3. **Derivado**: la salida es regenerable y no versionada; no es fuente de verdad.

## Requisitos

- `wiki/` con contenido (tras `ONBOARD` + `INGEST`). Con la wiki vacía no hay nada que graficar.
- graphify instalado **fuera del repo** (no es dependencia de CEREBRO):
  `pip install graphifyy` (o `pipx install graphifyy`).
- El backend que elijas: `claude` no necesita nada extra (ya usas Claude Code); `local` requiere
  [Ollama](https://ollama.com) corriendo; `structural` no usa LLM.

## Cómo correrlo (manual)

1. **Staging filtrado** — copia a un dir temporal solo las páginas no confidenciales:

   ```bash
   # bash — staging filtrado (excluye confidenciales) + verificación bloqueante
   mkdir -p graphify-out/staging
   # patrón tolerante a espacios y comillas alrededor del valor
   PAT="sensibilidad:[[:space:]]*[\"']?confidencial"
   grep -rLE "$PAT" wiki --include='*.md' | xargs -I{} cp --parents {} graphify-out/staging/
   # si algún confidencial se coló, ABORTA antes de invocar graphify
   if grep -rlE "$PAT" graphify-out/staging --include='*.md' >/dev/null 2>&1; then
     echo "ABORT: confidencial en staging — no se invoca graphify" >&2
     rm -rf graphify-out/staging; exit 1
   fi
   ```

   ```powershell
   # PowerShell — preserva rutas relativas (no aplana) + verificación bloqueante
   New-Item -ItemType Directory -Force graphify-out\staging | Out-Null
   $pat  = 'sensibilidad:\s*["'']?confidencial'
   $wiki = (Resolve-Path wiki).Path
   Get-ChildItem wiki -Recurse -Filter *.md |
     Where-Object { -not (Select-String -Path $_.FullName -Pattern $pat -Quiet) } |
     ForEach-Object {
       $dest = Join-Path 'graphify-out\staging' $_.FullName.Substring($wiki.Length).TrimStart('\')
       New-Item -ItemType Directory -Force (Split-Path $dest) | Out-Null
       Copy-Item $_.FullName $dest
     }
   if (Get-ChildItem graphify-out\staging -Recurse -Filter *.md | Select-String -Pattern $pat -Quiet) {
     Remove-Item -Recurse -Force graphify-out\staging
     throw "ABORT: confidencial en staging — no se invoca graphify"
   }
   ```

2. **Construye el grafo** (con el backend de `graph_lens.backend`):

   ```bash
   graphify ./graphify-out/staging --mode deep
   ```

3. **Abre** `graphify-out/graph.html` en el navegador.

## Salida

En `graphify-out/` (todo gitignored):
- `graph.html` — visor interactivo de nodos.
- `graph.json` — grafo consultable (lo lee la operación `GRAPH`).
- `GRAPH_REPORT.md` — nodos clave y preguntas sugeridas.

## Validación (la primera vez)

- [ ] Usó el backend elegido (`graph_lens.backend`); con `local`/`structural`, **cero** llamadas externas.
- [ ] **Cero** páginas `sensibilidad: confidencial` en el grafo (ni títulos ni relaciones).
- [ ] Los nodos corresponden a páginas reales de `wiki/`.
- [ ] No se escribió nada en `wiki/` ni en `genome/`; `git status` no muestra `graphify-out/`.

> ¿graphify no instalado o no quieres usarlo? Ignora esta carpeta: el resto de CEREBRO no depende
> de ella.
