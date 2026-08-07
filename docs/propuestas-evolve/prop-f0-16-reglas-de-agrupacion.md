---
tipo: propuesta-evolve
tarea: F0-16
status: approved
fecha: 2026-08-07
genes_afectados: [gen-ingest]
origen: piloto B-02 — 5 criterios de sesión recurrentes en 11 lotes (lotes 3, 7, 8, 10)
---

# Propuesta EVOLVE F0-16 — `gen-ingest` v4 → v5: las reglas de agrupación que el piloto destiló

## Motivación

Cinco decisiones de clasificación se repitieron lote a lote resueltas "por criterio de
sesión" — exactamente lo que un genoma existe para no dejar suelto. Si el criterio vive
en la memoria de una sesión, la siguiente ingesta clasifica distinto y la idempotencia
semántica se pierde aunque la mecánica aguante.

## Diff (v4 → v5) — párrafo nuevo de reglas de agrupación

1. N documentos cortos del mismo emisor sobre features de un mismo objeto → **una
   entidad agregadora + conceptos satélite**, no una página por documento.
2. Un benchmark se ancla con `mide` a una **página-capacidad**; si no existe, se crea.
3. `cita` apunta a la página que el trabajo citado **sostiene** (no hay páginas-fuente).
4. Concepto vs entidad/sistema se decide por **lo que la fuente sostiene** (mecánica
   descrita y autodescripción), jamás por el nombre propio.
5. Renombre declarado ("X, formerly Y") → página nueva con `reemplaza` documentando el
   renombre; la página anterior no se degrada si su fuente sigue siendo válida.
