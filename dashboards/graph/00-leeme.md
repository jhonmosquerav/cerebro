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
2. **Backend local**: usa Ollama u otro backend local. **Nada sale de tu máquina.** Esto mantiene
   el principio "sin servidores" y protege lo interno además de lo confidencial.
3. **Derivado**: la salida es regenerable y no versionada; no es fuente de verdad.

## Requisitos

- `wiki/` con contenido (tras `ONBOARD` + `INGEST`). Con la wiki vacía no hay nada que graficar.
- graphify instalado **fuera del repo** (no es dependencia de CEREBRO):
  `pip install graphifyy` (o `pipx install graphifyy`).
- Un backend local (p. ej. [Ollama](https://ollama.com)) corriendo.

## Cómo correrlo (manual)

1. **Staging filtrado** — copia a un dir temporal solo las páginas no confidenciales:

   ```bash
   # bash
   mkdir -p graphify-out/staging
   # excluye toda página con 'sensibilidad: confidencial' en su frontmatter
   grep -rL 'sensibilidad: confidencial' wiki --include='*.md' \
     | xargs -I{} cp --parents {} graphify-out/staging/
   ```

   ```powershell
   # PowerShell
   New-Item -ItemType Directory -Force graphify-out\staging | Out-Null
   Get-ChildItem wiki -Recurse -Filter *.md |
     Where-Object { -not (Select-String -Path $_.FullName -Pattern 'sensibilidad:\s*confidencial' -Quiet) } |
     ForEach-Object { Copy-Item $_.FullName (Join-Path 'graphify-out\staging' $_.Name) }
   ```

2. **Construye el grafo** (backend local):

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

- [ ] Corrió **100% local** (sin llamadas a APIs externas).
- [ ] **Cero** páginas `sensibilidad: confidencial` en el grafo (ni títulos ni relaciones).
- [ ] Los nodos corresponden a páginas reales de `wiki/`.
- [ ] No se escribió nada en `wiki/` ni en `genome/`; `git status` no muestra `graphify-out/`.

> ¿graphify no instalado o no quieres usarlo? Ignora esta carpeta: el resto de CEREBRO no depende
> de ella.
