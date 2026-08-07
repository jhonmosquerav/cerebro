---
tipo: propuesta-evolve
tarea: F0-12
status: approved
fecha: 2026-08-07
genes_afectados: [gen-migracion-genoma, gen-compuerta-mutacion]
origen: piloto Fase B, hallazgo H-10 · derivada del AUDIT 2026-08-07-e3f2a6d (M-01)
---

# Propuesta EVOLVE F0-12 — doctrina de distribución: migrar el genoma **entre** vaults sin romper el ledger

> **Bajo compuerta**: este archivo solo PROPONE. Nada se aplica sin OK del operador.

## Motivación

H-10 es el hallazgo más grave del piloto y no se ve hasta tener un vault vivo y un
producto que avanza: **el ledger del genoma se bifurca al clonar**. El piloto salió del
template en `5ce717b` con `events.jsonl` en 70 líneas; el piloto añadió 3 (`gene_added`
de su ONBOARD) y el template 5 (tanda F0-08…F0-11). La línea 71 de ambos declara el
mismo `prev` con contenido distinto: **dos cadenas de hash válidas desde el mismo
eslabón**, irreconciliables por merge textual — `git merge` produciría un archivo que
pasa el diff y **falla la cadena**.

Consecuencia: todo cliente queda en esta situación desde que corre ONBOARD, y cuando el
genoma del producto mejora **no hay camino declarado** para llevar esa mejora a un vault
desplegado sin romper la propiedad que da valor probatorio al ledger. El README promete
un producto clonable que evoluciona; el genoma no cubre el camino de esa evolución.

**No es un fallo del hash-chain** — la cadena hace exactamente lo que promete: detectar
que dos historias distintas no son la misma. El hueco es de **doctrina de distribución**,
que hoy no existe: [[gen-migracion-genoma]] v1 solo contempla migrar *dentro* de un
vault, y [[gen-compuerta-mutacion]] v2 no dice de quién es la cadena.

## Las tres salidas de `hallazgos.md`, evaluadas

1. **Separar los ledgers** (producto vs implantación) — correcta en la intuición, pero
   partir el archivo en dos rompe la trazabilidad única y complica cada herramienta.
2. **Rebase de eventos** — re-encadenar lo local sobre el nuevo final del template
   **reescribe hashes**: viola frontalmente el append-only del gen. Descartada.
3. **Actualizar solo `tools/`** — parche interino (así se desbloqueó B-02), pero
   institucionaliza la deriva entre lo que el gen dice y lo que la herramienta hace.
   No es doctrina.

## Doctrina propuesta: **cadena por vault + evento de adopción**

Refinamiento de la salida 1 que no parte ningún archivo: se re-declara **de quién es** la
cadena y se da nombre al acto de adoptar.

- `genome/events.jsonl` es la cadena de decisiones **de este vault**. Comparte prefijo
  con el template hasta el eslabón del clon; desde ahí **diverge legítimamente**. Dos
  cadenas de vaults distintos jamás se mezclan: ni merge, ni intercalado, ni rebase.
- **Camino declarado de actualización** (producto → implantación), bajo compuerta como
  toda mutación:
  1. Traer del release del template los archivos del genoma (genes y cápsulas) y
     `tools/` — **nunca su `events.jsonl`**.
  2. Registrar **una** línea `genome_adopted` en la cadena local vía `events append`:
     `signal` referencia el commit/tag del template y su `hash --scope genome`
     (state-hash del genoma adoptado); `diff` lista los genes que cambian de versión.
  3. Correr el pase de migración de [[gen-migracion-genoma]] contra el genoma nuevo.
  4. `verify` en verde antes y después.
- **Trazabilidad probatoria repartida sin perderse**: la historia fina de cómo el
  producto llegó a ese estado vive en la cadena del template, que viaja publicada con el
  producto; el evento de adopción la **referencia por hash, no la copia**. La cadena
  local prueba qué decidió este vault y cuándo — incluida cada adopción.
- Los genes de sector propios del vault (nacidos `gene_added` en su ONBOARD) conviven:
  la adopción no los toca; si un gen adoptado choca con uno local, el pase de migración
  lo reporta como hallazgo.

## Diffs propuestos

**[[gen-migracion-genoma]] v1 → v2** — sección nueva al final:

```
## Migración entre vaults (producto → implantación)

La cadena `genome/events.jsonl` es DE ESTE VAULT: comparte prefijo con el template
hasta el eslabón del clon y desde ahí diverge legítimamente. Cadenas de vaults
distintos jamás se mezclan (ni merge, ni intercalado, ni rebase — reescribir hashes
viola [[gen-compuerta-mutacion]]). Adoptar una mejora del template es una mutación
más, bajo compuerta: (1) traer genes/cápsulas y `tools/` del release — nunca su
`events.jsonl`; (2) UNA línea `genome_adopted` en la cadena local (`events append`)
cuyo `signal` referencia commit/tag y `hash --scope genome` del template y cuyo
`diff` lista los genes que cambian de versión; (3) correr el pase de migración de
este gen contra el genoma adoptado; (4) `verify` en verde antes y después. La
procedencia fina vive en la cadena del template, publicada con el producto: el
evento la referencia por hash, no la copia. Los genes de sector locales conviven
con lo adoptado; un choque entre ambos es hallazgo de migración, no se resuelve solo.
```

**[[gen-compuerta-mutacion]] v2 → v3** — párrafo nuevo antes de la verificación mecánica:

```
La cadena es DE ESTE VAULT. Adoptar genoma de otro origen (p. ej. una release del
template) se registra como UNA mutación `genome_adopted` según el camino declarado
en [[gen-migracion-genoma]]; importar, intercalar o re-encadenar líneas de la cadena
de otro vault está prohibido — el append-only protege la historia local, y la del
origen viaja con el origen.
```

Además: actualizar las dos líneas del índice de genes en `CLAUDE.md` (y espejo).

## Cambio de infraestructura que lo acompaña

Ninguno obligatorio: `events append` no restringe `type` (verificado en
`tools/cerebro_core/events.py` — valida claves, no vocabulario), así que `genome_adopted`
entra hoy. Deseable a futuro (no bloquea): que `verify` valide la referencia del evento
de adopción contra `hash --scope genome`.

## Evidencia

- `C:\cerebro-piloto\piloto\hallazgos.md` § H-10 (comprobación línea a línea del `prev`
  compartido con contenido distinto).
- `log.md` 2026-07-29 y `wiki/episodic/2026-07-29-30246132.md:65-68` ("el bloqueo real").
- AUDIT `2026-08-07-e3f2a6d`: M-01 confirmado por maker y auditor (vacío de doctrina;
  gen-migracion-genoma v1 verificado solo intra-vault).

## Severidad y honestidad sobre la prioridad

**Alta en el producto, invisible en el template.** En este repo ningún invariante está
violado (por eso el AUDIT lo puntúa 21); el defecto vive en cada implantación desde su
primer minuto y bloqueaba en concreto traer las herramientas corregidas al piloto para
seguir B-02. Es la propuesta que convierte "clonable y que evoluciona" de promesa a
mecanismo.

## Orden de aplicación

1. Editar `genome/genes/gen-migracion-genoma.md`; `version: 2`; `events append` + commit.
2. Editar `genome/genes/gen-compuerta-mutacion.md`; `version: 3`; `events append` + commit.
3. Índice de genes en `CLAUDE.md` + `mirror --fix` (va con el commit 2).
4. Fila F0-12 en `docs/propuestas-evolve/README.md`; tests + `verify`.
