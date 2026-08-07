---
tipo: propuesta-evolve
tarea: F0-17
status: approved
fecha: 2026-08-07
genes_afectados: [gen-confianza-por-fuente]
origen: piloto B-02 — johnny-decimal (lote 4), fuentes mixtas (lotes 4 y 10), familias de specs parciales (lotes 6 y 11)
---

# Propuesta EVOLVE F0-17 — `gen-confianza-por-fuente` v2 → v3: la confianza se ancla a la captura, no solo al emisor

## Motivación

Tres casos reales que el mapeo tipo-de-fuente→confianza no cubría: (a) el autor de un
método hablando de su método, pero en una **landing comercial** sin la mecánica (primera
mano por emisor, débil por captura); (b) páginas sostenidas por **fuentes de tipos
mixtos** (paper 0.75 + README 0.6); (c) **familias de specs capturadas solo por su
documento raíz** (PROV 3/12, in-toto solo README). Los tres se resolvieron con criterio
de sesión; dos se repitieron.

## Diff (v2 → v3) — párrafo nuevo

La `confidence` se ancla a **la captura concreta**, no solo al tipo del emisor: una
landing o resumen del propio autor no hereda el rango de su documentación técnica —
se asimila al escalón que la captura sostiene y se declara. Página con fuentes de tipos
mixtos: toma el **piso** de las fuentes que la sostienen y declara la frontera de cada
una por sección. Cobertura parcial de un conjunto (familia de specs por su raíz): la
sección de frontera es obligatoria y la `confidence` califica solo lo capturado.
