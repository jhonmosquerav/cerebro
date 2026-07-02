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

1. **Confidencialidad** ([[gen-confidencialidad]]): graphify solo ve páginas que declaran
   **explícitamente** `sensibilidad: publico` o `sensibilidad: interno` — **allowlist,
   fail-closed**. Página `confidencial`, sin campo, con typo en el valor o con frontmatter
   ilegible **no entra** al staging. Se garantiza **controlando la entrada** (staging filtrado),
   no confiando en un flag.
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

1. **Staging por allowlist (fail-closed)** — copia a un dir temporal **solo** las páginas cuyo
   frontmatter declara **explícitamente** `sensibilidad: publico` o `sensibilidad: interno`.
   Página sin campo, con valor no reconocido (typo) o con frontmatter ilegible **no entra**, y
   queda listada con su motivo en `graphify-out/excluidas.txt` (reporte derivado y local,
   gitignored; revísalo, no lo copies a `wiki/`). Ojo: el `default_sensibilidad` del manifiesto
   **no rescata** páginas aquí — la lente exige declaración explícita en la propia página; una
   página meta sin campo queda fuera del grafo hasta que declare `sensibilidad: publico`.

   ```bash
   # bash — staging por ALLOWLIST (fail-closed): solo entra lo explicitamente permitido.
   # Patrón tolerante a espacios, comillas y mayúsculas; rutas con espacios soportadas.
   [ -d wiki ] || { echo "ABORT: no se ve wiki/ (corre esto desde la raiz del repo)" >&2; exit 1; }
   STAGING="graphify-out/staging"
   REPORTE="graphify-out/excluidas.txt"
   ALLOW="^sensibilidad:[[:space:]]*[\"']?(publico|interno)[\"']?[[:space:]]*$"
   DENY="^sensibilidad:[[:space:]]*[\"']?confidencial"
   rm -rf "$STAGING"
   mkdir -p "$STAGING"
   : > "$REPORTE"
   find wiki -type f -name '*.md' | while IFS= read -r f; do
     rel="${f#wiki/}"
     # frontmatter = bloque entre el primer y el segundo '---'; sin cierre => ilegible
     fm=$(awk 'NR==1 { if ($0 ~ /^---[[:space:]]*$/) { infm=1; next } else exit }
               infm && /^---[[:space:]]*$/ { closed=1; exit }
               infm { print }
               END { if (!closed) exit 1 }' "$f") || fm=""
     if [ -z "$fm" ]; then
       printf '%s\tsin frontmatter legible\n' "$rel" >> "$REPORTE"
     elif printf '%s\n' "$fm" | grep -iqE "$DENY"; then
       printf '%s\tconfidencial\n' "$rel" >> "$REPORTE"
     elif printf '%s\n' "$fm" | grep -iqE "$ALLOW"; then
       mkdir -p "$STAGING/$(dirname "$rel")"
       cp "$f" "$STAGING/$rel"
     else
       printf '%s\tsin sensibilidad explicita permitida\n' "$rel" >> "$REPORTE"
     fi
   done
   [ -s "$REPORTE" ] && { echo "Excluidas del staging (motivo en $REPORTE):"; cat "$REPORTE"; }
   # DOBLE CERROJO: TODO archivo del staging debe declarar el marcador permitido;
   # cualquier archivo sin el => ABORTA antes de invocar graphify.
   SIN_MARCA=$(find "$STAGING" -type f -name '*.md' | while IFS= read -r f; do
     grep -iqE "$ALLOW" "$f" || printf '%s\n' "$f"
   done)
   if [ -n "$SIN_MARCA" ]; then
     echo "ABORT: archivo(s) sin marcador de sensibilidad permitido en staging:" >&2
     printf '%s\n' "$SIN_MARCA" >&2
     rm -rf "$STAGING"
     exit 1
   fi
   N=$(find "$STAGING" -type f -name '*.md' | wc -l)
   if [ "$N" -eq 0 ]; then
     echo "AVISO: staging vacio - ninguna pagina declara sensibilidad permitida (fail-closed)." >&2
   fi
   echo "Staging listo: $N pagina(s) permitida(s)."
   ```

   ```powershell
   # PowerShell — ALLOWLIST fail-closed; preserva rutas relativas (no aplana).
   # Regex insensible a mayúsculas por defecto, tolerante a espacios y comillas.
   $wiki = (Resolve-Path wiki).Path   # aborta si no se corre desde la raíz del repo
   $staging = 'graphify-out\staging'
   $reporte = 'graphify-out\excluidas.txt'
   $allow = '^sensibilidad:\s*["'']?(publico|interno)["'']?\s*$'
   $deny  = '^sensibilidad:\s*["'']?confidencial'
   if (Test-Path $staging) { Remove-Item -Recurse -Force $staging }
   New-Item -ItemType Directory -Force $staging | Out-Null
   $excluidas = @()
   Get-ChildItem wiki -Recurse -Filter *.md | ForEach-Object {
     $rel = $_.FullName.Substring($wiki.Length).TrimStart('\')
     $lineas = @(Get-Content -LiteralPath $_.FullName)
     $fm = @()  # frontmatter = bloque entre el primer y el segundo '---'; sin cierre => ilegible
     if ($lineas.Count -gt 2 -and $lineas[0] -match '^---\s*$') {
       for ($i = 1; $i -lt $lineas.Count; $i++) {
         if ($lineas[$i] -match '^---\s*$') { if ($i -gt 1) { $fm = @($lineas[1..($i-1)]) }; break }
       }
     }
     $motivo = $null
     if ($fm.Count -eq 0) { $motivo = 'sin frontmatter legible' }
     elseif ($fm -match $deny) { $motivo = 'confidencial' }
     elseif (-not ($fm -match $allow)) { $motivo = 'sin sensibilidad explicita permitida' }
     if ($motivo) {
       $excluidas += ("{0}`t{1}" -f $rel, $motivo)
     } else {
       $dest = Join-Path $staging $rel
       New-Item -ItemType Directory -Force (Split-Path $dest) | Out-Null
       Copy-Item -LiteralPath $_.FullName -Destination $dest
     }
   }
   Set-Content -Path $reporte -Value $excluidas -Encoding utf8
   if ($excluidas) { Write-Host "Excluidas del staging (motivo en $reporte):"; $excluidas | ForEach-Object { Write-Host $_ } }
   # DOBLE CERROJO: TODO archivo del staging debe declarar el marcador permitido
   $sinMarca = @(Get-ChildItem $staging -Recurse -Filter *.md |
     Where-Object { -not (Select-String -LiteralPath $_.FullName -Pattern $allow -Quiet) })
   if ($sinMarca.Count -gt 0) {
     Remove-Item -Recurse -Force $staging
     throw "ABORT: archivo(s) sin marcador de sensibilidad permitido en staging: $($sinMarca.Name -join ', ')"
   }
   $n = @(Get-ChildItem $staging -Recurse -Filter *.md).Count
   if ($n -eq 0) { Write-Warning 'staging vacio: ninguna pagina declara sensibilidad permitida (fail-closed).' }
   Write-Host "Staging listo: $n pagina(s) permitida(s)."
   ```

2. **Construye el grafo** (con el backend de `graph_lens.backend`):

   ```bash
   graphify ./graphify-out/staging --mode deep
   ```

3. **Abre** `graphify-out/graph.html` en el navegador.

## Salida

En `graphify-out/` (todo gitignored):
- `staging/` — copia filtrada por allowlist (la única entrada que ve graphify).
- `excluidas.txt` — reporte del paso 1: qué páginas NO entraron al staging y por qué motivo.
- `graph.html` — visor interactivo de nodos.
- `graph.json` — grafo consultable (lo lee la operación `GRAPH`).
- `GRAPH_REPORT.md` — nodos clave y preguntas sugeridas.

## Validación (la primera vez)

- [ ] Usó el backend elegido (`graph_lens.backend`); con `local`/`structural`, **cero** llamadas externas.
- [ ] **Todo** archivo del staging declara explícitamente `sensibilidad: publico|interno`
      (el doble cerrojo del paso 1 terminó sin abortar).
- [ ] `graphify-out/excluidas.txt` revisado: nada que debiera estar en el grafo quedó fuera por
      typo o campo ausente (si falta algo, corrige el frontmatter de la página y repite el paso 1).
- [ ] **Cero** páginas `sensibilidad: confidencial` en el grafo (ni títulos ni relaciones).
- [ ] Los nodos corresponden a páginas reales de `wiki/`.
- [ ] No se escribió nada en `wiki/` ni en `genome/`; `git status` no muestra `graphify-out/`.

## Nota de cambio (2026-07-02): fail-open → fail-closed

> El filtro de staging pasó de **deny-list fail-open** (una página sin campo `sensibilidad`, o
> con typo en el valor, entraba al staging y podía salir por un backend externo) a **allowlist
> fail-closed** (solo entra lo que declara explícitamente `publico|interno`; el resto queda
> listado con motivo en `excluidas.txt`). La verificación bloqueante también se invirtió: antes
> comprobaba la **ausencia** de `confidencial`; ahora exige la **presencia** del marcador
> permitido en TODO archivo del staging (doble cerrojo). Se conservan las protecciones previas
> (patrón tolerante a espacios/comillas, ahora también a mayúsculas; rutas relativas preservadas;
> abort antes de invocar graphify) y se eliminó `cp --parents` (GNU-only, rompía en macOS/BSD).
> Origen: evaluación `audit/evaluations/2026-07-01-810f24e/` (hallazgo sev-4; backlog A-07).

> ¿graphify no instalado o no quieres usarlo? Ignora esta carpeta: el resto de CEREBRO no depende
> de ella.
