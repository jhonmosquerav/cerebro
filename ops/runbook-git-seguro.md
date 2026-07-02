---
title: Git seguro para clones operativos de CEREBRO
tipo: runbook
tarea: A-08
fecha: 2026-07-02
---

# Runbook — git seguro (clones de CEREBRO con datos reales)

Para el **clon operativo**: el repo donde corriste `ONBOARD` y vive conocimiento real de
una empresa. Motivación (eval `2026-07-01-810f24e`, panel de seguridad): el remoto del
template es **GitHub público**, un `git push` publica **toda la historia** —no solo el
estado actual—, y lo borrado sigue recuperable: en este mismo repo, un fixture con PII
simulada eliminado en la "limpieza a template público" se recupera hoy con
`git show 246f8df~1:sim/_auditoria-fixture/wiki/semantic/confidencial/expediente-x.md`.
Con datos reales de clínica o bufete, ese mismo mecanismo sería una brecha.

**Regla de partida — dos repos, dos regímenes:**

| Repo | Remoto | Qué puede contener |
|---|---|---|
| Template público (`github.com/jhonmosquerav/cerebro`) | público | SOLO plantilla neutra: genoma, blueprints, docs. Jamás datos de una empresa |
| Clon operativo (tu empresa) | **privado obligatorio, o ninguno** | wiki/raw reales; lo `confidencial` puede versionarse aquí — nunca salir a un remoto no privado |

## 1. Remoto privado obligatorio

Al crear el clon operativo, decide UNA de dos:

- **Sin remoto** (válido): borra el origin heredado del template y respalda con
  `ops/backup/` (cifrado, off-site):

  ```bash
  git remote remove origin
  ```

- **Remoto privado**: créalo privado desde el día cero (un repo que "luego se hace
  privado" ya filtró su historia):

  ```bash
  gh repo create mi-empresa/cerebro-operativo --private
  git remote set-url origin "git@github.com:mi-empresa/cerebro-operativo.git"
  ```

**Verificación de visibilidad** (repítela ante la duda; entra al checklist pre-push):

```bash
# con GitHub CLI (gh trae su propio --jq embebido; no requiere jq del sistema)
gh repo view "$(git remote get-url origin)" --json visibility --jq '.visibility'
# esperado: PRIVATE
```

Sin `gh`, o con remoto que no es GitHub: `git remote -v` + **revisión manual** — abre la
URL del remoto en una ventana del navegador **sin sesión iniciada**: si el repo se ve, es
público → ALTO. En otros proveedores (GitLab, Gitea, Azure), verifica la visibilidad en el
panel del proyecto.

## 2. Checklist pre-push (ejecutable, paso a paso)

Corre esto ANTES de cada `git push` desde un clon operativo. Sustituye `origin`/`main` si
usas otros nombres.

**Paso 1 — ¿a qué remoto voy a pushear?**

```bash
git remote -v
```

La URL debe ser la del remoto privado del clon. Si es el template público y trabajas con
datos reales: **detente aquí**.

**Paso 2 — ¿el remoto es privado?**

```bash
gh repo view "$(git remote get-url origin)" --json visibility --jq '.visibility'
# esperado: PRIVATE  — sin gh: revisión manual (ver §1)
```

**Paso 3 — ¿qué sale exactamente en este push?**

```bash
git fetch origin
git log --oneline 'origin/main..HEAD'
# archivos tocados por CUALQUIER commit saliente (incluye añadidos-y-borrados en medio):
git log --name-only --pretty=format: 'origin/main..HEAD' | sort -u
```

Revisa esa lista. Hacia el template público **nada** de `wiki/`, `raw/`,
`onboard/company.yaml` con datos reales, ni bitácoras operativas.

**Paso 4 — ¿algún `sensibilidad: confidencial` saliendo?**

```bash
PAT="sensibilidad:[[:space:]]*[\"']?confidencial"
# a) lo staged ahora mismo (antes de commitear)
git diff --cached | grep -nE "$PAT" || echo 'staged: limpio'
# b) el contenido de los commits que salen
git diff 'origin/main..HEAD' | grep -nE "$PAT" || echo 'diff saliente: limpio'
# c) barrido del ÁRBOL de cada commit saliente (cubre lo añadido y borrado en medio)
for c in $(git rev-list 'origin/main..HEAD'); do
  git grep -lE "$PAT" "$c" -- 'wiki/' 'raw/' && echo "confidencial en el árbol de $c"
done; echo 'barrido de historia saliente: hecho'
```

Interpretación: hacia el **remoto privado verificado** (pasos 1–2 en verde), que haya
confidenciales versionados es lo esperado. Hacia el **template público o cualquier remoto
dudoso**, una sola coincidencia = **ABORTA el push**.

**Paso 5 — ¿derivados y estado volátil ignorados y fuera del árbol?**

```bash
git check-ignore -v graphify-out || echo 'ALTO: graphify-out/ NO está ignorado'
git check-ignore -v .claude/hooks/.state || echo 'AVISO: .claude/hooks/.state/ aún sin ignorar (hooks A-02)'
# nada de eso debe estar TRACKEADO (ignorar no des-trackea): la salida debe ser vacía
git ls-files graphify-out .claude/hooks/.state
```

**Paso 6 — decisión.** Todo en verde → push. Cualquier ALTO → no hay push; si algo salió
en pushes anteriores, trata como incidente (§4).

## 3. Purga de historia con git-filter-repo (solo incidentes)

Para cuándo un secreto, credencial o PII quedó **commiteado**. `git rm` + commit **no
borra nada** (evidencia: el fixture de §arriba). La purga reescribe la historia: es
destructiva y tiene consecuencias (§3.3, §3.4) — no es mantenimiento rutinario.

**3.0 Antes de tocar nada**

1. Backup cifrado fresco: `bash ops/backup/backup.sh <destino>` (la purga es irreversible).
2. Si lo vertido es un secreto/credencial: **rótalo ya** (§4). Purgar no des-compromete.
3. Si el material vive en `raw/`: lee §3.4 — hoy el genoma lo prohíbe sin excepción.

**3.1 Requisitos**

```bash
python3 -m pip install --user git-filter-repo
git filter-repo --version
```

**3.2 Procedimiento** — siempre sobre un **clon espejo fresco**, nunca sobre el repo vivo
(git-filter-repo mismo rechaza repos no frescos, con razón):

```bash
git clone --mirror 'D:/cerebro-operativo' '/tmp/cerebro-purga.git'
cd '/tmp/cerebro-purga.git'

# opción A — purgar un ARCHIVO completo de toda la historia
git filter-repo --invert-paths --path 'raw/2026-07-02-export-clientes.csv'

# opción B — purgar una CADENA (p. ej. un token) conservando los archivos
printf '%s\n' 'TOKEN-VERTIDO-AQUI==>[PURGADO-2026-07-02]' > '/tmp/expresiones.txt'
git filter-repo --replace-text '/tmp/expresiones.txt'

# guarda el mapa commit-viejo → commit-nuevo ANTES de borrar el espejo
# (clon espejo/bare: filter-repo/commit-map · clon normal: .git/filter-repo/commit-map)
cp 'filter-repo/commit-map' '/ruta/segura/commit-map-<id-incidente>.txt'
```

**Verificación en el espejo purgado:**

```bash
git show '<SHA-antiguo>:raw/2026-07-02-export-clientes.csv'   # debe FALLAR (bad object)
git log --all --full-history -- 'raw/2026-07-02-export-clientes.csv'   # vacío (opción A)
git log -S 'TOKEN-VERTIDO-AQUI' --all   # vacío (opción B)
```

**Reemplazo del repo vivo** (sus reflogs y objetos aún contienen lo purgado):

```bash
mv 'D:/cerebro-operativo' 'D:/cerebro-operativo-CUARENTENA'   # NO lo borres aún
git clone '/tmp/cerebro-purga.git' 'D:/cerebro-operativo'
cd 'D:/cerebro-operativo' && git remote remove origin   # apuntaba al espejo temporal
# re-añade el remoto privado real; repón desde la CUARENTENA los archivos NO
# versionados que quieras conservar (revisándolos uno a uno);
# cuando todo verifique: borra cuarentena y espejo de forma definitiva.
```

**Si hay remoto:** `git push --force --mirror '<url-remoto-privado>'`. Advertencias:

- El force-push **no** limpia forks, clones ajenos ni cachés del proveedor; en GitHub los
  objetos huérfanos pueden seguir accesibles por SHA un tiempo — solicita la purga a
  soporte (doc oficial: *Removing sensitive data from a repository*).
- Si el remoto era **público** y pasó tiempo: asume publicación irreversible; manda la
  rotación del secreto y la evaluación de notificación (§4), no la purga.

**3.3 Consecuencia: SHAs reescritos → identidades de AUDIT invalidadas**

Los run-id de `audit/runs/<fecha>-<shortSHA>/` y los eval-id de `audit/evaluations/`
están claveados al SHA de git. Tras la purga, esos SHAs **ya no nombran ningún commit**
de la nueva historia. Qué hacer:

- **No renombres** las carpetas de corridas: son registro histórico de su época.
- Anota en `log.md` una línea `PURGA` con: id del incidente, ruta/cadena purgada,
  `HEAD-viejo → HEAD-nuevo`, y dónde archivaste el `commit-map` (convención sugerida:
  `ops/purgas/<id-incidente>/commit-map.txt` — el mapa contiene solo SHAs, no material
  sensible).
- Asume que las corridas previas **ya no son re-derivables** sobre el repo purgado (su
  snapshot cita SHAs muertos); siguen valiendo como evidencia de su momento, con el
  commit-map como puente.
- Los **backups anteriores contienen lo purgado**: destrúyelos y genera uno nuevo
  (`ops/backup/runbook-backup.md`, sección de rotación).

**3.4 `raw/` y el genoma — la excepción pendiente**

[[gen-raw-inmutable]] v1 (vigente) ordena: *"Nunca edites, renombres ni borres una fuente
en `raw/`"* — sin excepción alguna. **Purgar `raw/` hoy contradice el genoma.** Existe una
propuesta EVOLVE formal para añadir la excepción única y auditada de purga por incidente
(condiciones: incidente en `log.md` + aprobación explícita previa + línea en
`genome/events.jsonl` + re-AUDIT posterior):
`audit/evaluations/2026-07-01-810f24e/70-propuestas-evolve/prop-a08-excepcion-purga-gen-raw-inmutable.md`
(status: `pending`). Hasta que pase la compuerta ([[gen-compuerta-mutacion]]), **no purges
`raw/`**; en un incidente real, la compuerta puede ejercerse en el momento: primero se
aprueba y registra la mutación del gen, después se purga.

## 4. Respuesta a incidentes (mínima)

Secreto, credencial o PII vertidos en el repo (o pusheados):

1. **Detectar.** Vías: checklist pre-push (§2), revisión manual, aviso del proveedor.
   Barrido orientativo de secretos (complementa, no sustituye, la revisión humana):

   ```bash
   git grep -nIE 'BEGIN (RSA|OPENSSH|EC) PRIVATE KEY|api[_-]?key|secret|token' -- ':!ops/'
   ```

   Congela pushes del repo afectado desde ya.
2. **Contener** (antes de purgar):
   - Remoto expuesto: hazlo privado de inmediato o elimínalo (`git remote remove origin`);
     revoca tokens/deploy-keys de acceso al repo.
   - Secreto/credencial: **rótalo/revócalo en el sistema de origen**. Un secreto pusheado
     está comprometido aunque después se purgue.
   - PII expuesta en un remoto: evalúa obligaciones de notificación del responsable del
     tratamiento (crítico en salud/legal). Este runbook no es asesoría legal.
3. **Purgar** la historia (§3). Si toca `raw/`: solo con la excepción del gen aprobada
   por compuerta (§3.4).
4. **Registrar.** Línea `INCIDENTE` en `log.md` (id = `AAAA-MM-DD-slug`, qué se vertió,
   alcance, acciones, estado). Si hubo purga de `raw/`: además la línea en
   `genome/events.jsonl` que exige la excepción del gen, y lo de §3.3.
5. **Verificar y cerrar.** Checklist §2 en verde sobre el repo purgado; `git show` del
   SHA antiguo falla; backups viejos destruidos y backup nuevo con `--verify-restore` OK;
   re-AUDIT ([[gen-auto-auditoria]]) sobre el estado purgado.

## Relacionado

- `ops/backup/runbook-backup.md` — respaldo cifrado off-site + prueba de restauración (A-09).
- [[gen-confidencialidad]] — el eje `sensibilidad` que este checklist inspecciona.
- [[gen-raw-inmutable]] · propuesta pendiente `prop-a08-excepcion-purga-gen-raw-inmutable.md` (§3.4).
- `dashboards/graph/00-leeme.md` — el otro punto de salida controlada (staging de la lente).
