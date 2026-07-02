---
title: Backup cifrado off-site + prueba de restauración
tipo: runbook
tarea: A-09
fecha: 2026-07-02
---

# Runbook — backup cifrado off-site de CEREBRO

Cierra el riesgo *"pérdida total del cerebro: borrado, ransomware o fallo del disco único"*
(eval `2026-07-01-810f24e`, panel de seguridad: hoy git en un solo disco es el único
mecanismo, y el remoto configurado es público — no sirve para datos reales). Herramienta:
`ops/backup/backup.sh`. Complementa a `ops/runbook-git-seguro.md` (remoto privado); un
remoto privado y este backup **no son excluyentes**: el bundle cifrado protege incluso si
decides no tener remoto alguno.

## Qué cubre cada backup (y qué no)

| Incluye | Qué es |
|---|---|
| `repo.bundle` | **Toda** la historia de git (todas las refs) — wiki, genoma, `events.jsonl`, corridas de audit |
| `no-versionados.tar.gz` | Archivos aún no versionados y no ignorados (trabajo en curso) |
| `cambios-sin-commit.patch` | Diff del árbol de trabajo vs HEAD al momento del backup |
| `MANIFEST.txt` | Fecha, HEAD, rama, parámetros de cifrado (para restaurar sin adivinar) |

**No cubre** (a propósito): `graphify-out/` (derivado regenerable), `.claude/hooks/.state/`
(estado volátil de hooks), nada ignorado por git. El paquete completo se cifra con
`openssl enc -aes-256-cbc -pbkdf2 -iter 600000 -salt` antes de tocar el destino: el medio
externo (o la nube que lo sincronice) **nunca ve el contenido en claro**.

## La passphrase

- **Generarla** (una sola vez, larga y aleatoria):

  ```bash
  openssl rand -base64 32
  ```

- **Dónde guardarla:** en tu gestor de contraseñas; opcionalmente una copia impresa en un
  lugar físico distinto al de los backups. Sin la passphrase, los backups son ruido:
  perderla = perderlo todo.
- **Dónde NO guardarla:** dentro del repo (ni en `raw/`, ni en `log.md`, ni en
  `.claude/settings.json`), ni en el mismo disco/carpeta donde dejas los `.tar.gz.enc`,
  ni en un chat con un agente.
- **Exportarla sin dejarla en el historial del shell:**

  ```bash
  read -r -s CEREBRO_BACKUP_PASSPHRASE && export CEREBRO_BACKUP_PASSPHRASE
  ```

## Uso manual (Git Bash)

```bash
# rutas en Git Bash con /: E:\backups\cerebro se escribe /e/backups/cerebro
read -r -s CEREBRO_BACKUP_PASSPHRASE && export CEREBRO_BACKUP_PASSPHRASE
bash ops/backup/backup.sh /e/backups/cerebro
```

El nombre del artefacto es `cerebro-backup-<fecha>-<shortSHA>.tar.gz.enc`, acompañado de su
`.sha256` y de un `COMO-RESTAURAR.txt` (sin secretos) con los comandos de restauración —
importante porque este runbook vive *dentro* del repo que estarías intentando recuperar.

## Cadencia recomendada

- **Tras cada sesión de ingesta** (`INGEST` / `BULK INGEST`) **o mutación de genoma**; como
  mínimo, **semanal**.
- **Commitea antes de respaldar**: el bundle solo lleva lo commiteado (el `.patch` cubre el
  resto, pero es una red, no un sustituto).
- **Retención sugerida:** las 8 más recientes + 1 por mes; rotación manual (borra las demás
  del destino).
- **Tras una purga de historia** (`ops/runbook-git-seguro.md` §3): los backups anteriores
  contienen lo purgado — **destrúyelos** y genera uno nuevo de inmediato. El modo
  `--verify-restore` detecta este caso (historias divergentes → FALLO explicado).

## Destinos off-site razonables en Windows

El destino se pasa **siempre como argumento** (sin default: un backup dentro del mismo
disco no protege nada; el script además rechaza destinos dentro del repo).

| Destino | Protege contra | Nota |
|---|---|---|
| Disco USB externo (`/e/backups/cerebro`) | fallo del disco interno, ransomware si lo **desconectas** tras el backup | el más simple; desconéctalo al terminar |
| Carpeta sincronizada a nube (OneDrive/Drive/Dropbox) | pérdida física del equipo | aceptable **porque el artefacto ya viaja cifrado**; la nube nunca ve claro |
| NAS local | fallo del disco | no protege contra incendio/robo del sitio; combínalo con nube |

**Honesto:** elegir, comprar y configurar el destino off-site real es decisión del
operador; el script solo exige que el directorio exista y sea externo al repo.

## Programación opcional (Programador de tareas de Windows)

1. Define la passphrase como variable de entorno **de usuario** (una vez, en `cmd.exe`):

   ```
   setx CEREBRO_BACKUP_PASSPHRASE "la-passphrase-generada"
   ```

   *Compromiso honesto:* `setx` la deja en el registro (`HKCU\Environment`), legible por
   cualquier proceso de tu usuario. Protege contra exposición remota/en la nube, **no**
   contra malware local con tu sesión. Si eso no te sirve, no programes: corre el backup
   a mano con `read -r -s`.

2. Crea la tarea (una línea, en `cmd.exe`; ajusta ruta de Git y destino):

   ```
   schtasks /Create /TN "CEREBRO backup semanal" /SC WEEKLY /D SUN /ST 20:00 /TR "\"C:\Program Files\Git\bin\bash.exe\" -lc 'bash /d/cerebro/ops/backup/backup.sh /e/backups/cerebro >> /e/backups/cerebro/backup.log 2>&1'"
   ```

3. Revisa `backup.log` en el destino tras la primera corrida programada. Si el disco
   externo no está conectado a esa hora, el script **falla con mensaje claro** (destino
   inexistente) — eso quedará en el log, no en silencio.

## Prueba de restauración (trimestral)

Un backup no probado es una hipótesis. Cada trimestre (y tras el primer backup):

```bash
read -r -s CEREBRO_BACKUP_PASSPHRASE && export CEREBRO_BACKUP_PASSPHRASE
bash ops/backup/backup.sh --verify-restore '/e/backups/cerebro/cerebro-backup-XXXX.tar.gz.enc'
```

Qué hace: valida el `.sha256`, **descifra a un temporal** (fuera del repo, se borra al
salir), extrae, verifica el tar interno, `git bundle verify` + `git clone` del bundle,
`git fsck` sobre el clon y compara `git rev-parse HEAD` con el repo vivo.

Cómo leer el resultado:

- `OK … idéntico` — el backup restaura exactamente el estado actual.
- `OK … ANTERIOR al estado actual` — íntegro, pero el repo avanzó: genera un backup nuevo.
- `FALLO` — passphrase incorrecta, archivo corrupto, o **historias divergentes** (típico
  tras una purga: rota los backups). El mensaje dice cuál.

Registra el resultado con una línea en `log.md`, por ejemplo:
`- BACKUP verify-restore: OK — cerebro-backup-20260702-...-810f24e.tar.gz.enc (sha256 ab12…)`.

## Restauración real (desastre)

Sigue el `COMO-RESTAURAR.txt` que acompaña a cada backup en el destino: descifrar con
openssl (mismos parámetros, pide la passphrase interactivamente), extraer, `git clone`
del bundle, reponer `no-versionados.tar.gz` y, si aplica, `git apply` del patch. No
requiere este repo ni este script — solo Git Bash y la passphrase.
