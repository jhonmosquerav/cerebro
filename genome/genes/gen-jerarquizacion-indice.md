---
id: gen-jerarquizacion-indice
trigger: anclar una página nueva / una sección de index.md supera el umbral de anclas
status: active
version: 2
---

El índice crece con política, no con fe en la curación. `index.md` se mantiene corto
(~1 pantalla: secciones de ≤`hub_umbral` anclas, áreas partidas a 1 línea) porque el
anclado es **determinista** y toda sección que supere el umbral se parte en **página-hub**.
Consumidores: INGEST ancla ([[gen-ingest]], cápsula [[ingesta-de-fuente]]), CONSOLIDATE
parte ([[gen-consolidate]]), QUERY navega index → hub → página ([[gen-query]]).

## Anclado determinista (sustituye el "si aplica" de INGEST)
Una página **SE ancla** si y solo si cumple TODO:
1. `sensibilidad != confidencial` ([[gen-confidencialidad]]: lo confidencial jamás se
   ancla, ni en `index.md` ni en un hub);
2. tier `semantic/` o `procedural/` (lo de `working/` y `episodic/` no se ancla: llega al
   índice solo cuando CONSOLIDATE lo promueve; excepción declarada: el puntero rotatorio
   "lo más reciente" por tier que mantiene CHECKPOINT ([[gen-checkpoint]], paso 3) es
   navegación meta, no ancla de conocimiento, y no cuenta para `hub_umbral`);
3. `clase != evento` ([[gen-clase-temporal]]: los eventos se alcanzan por su síntesis
   ([[gen-sintesis-de-volumen]]) o por su entidad, no anclados uno a uno).
Sin zona gris: cumple los tres → se ancla SIEMPRE; falla uno → no se ancla.
**Dónde:** en la sección de su **área** dentro de `index.md`; si el área ya tiene hub, en
`hub-<área>.md` (esa área ya no crece en el index). Área = la categoría de la taxonomía
del manifiesto a la que pertenece la página (= su subcarpeta bajo el tier, slug exacto de
la carpeta); una página en la raíz del tier ancla en la línea general del tier.
**Idempotente:** verifica antes de añadir — re-anclar una página ya anclada es no-op. Cada
página vive en exactamente UN punto de la jerarquía (index o su hub, nunca ambos).

## Umbral y partición en hubs (parte CONSOLIDATE, nunca INGEST)
Cuando una sección/área acumula más de **`hub_umbral`** anclas (configurable en
`onboard/company.yaml`; default **7** — más de ~7 ítems ya no se escanean de un vistazo),
CONSOLIDATE la parte:
1. crea `wiki/<tier>/hub-<área>.md` con TODAS las anclas del área (agrupadas por
   subcarpeta o `type` cuando son muchas);
2. sustituye la sección del área en `index.md` por una sola línea:
   `**<área>** → [[hub-<área>]]`;
3. deja una línea en `log.md`. Partir es cambio de CONTENIDO, no de genoma: no pasa por
   la compuerta.
INGEST nunca parte: si al anclar ve la sección sobre el umbral, ancla normal y deja en
`log.md` la señal `seccion <área> sobre hub_umbral` para el próximo CONSOLIDATE.
**Idempotencia de partición:** la identidad del hub es su ruta — misma área → mismo
`hub-<área>.md`; si ya existe, se ACTUALIZA (merge de anclas sin duplicar líneas), jamás
nace un `hub-<área>-2`. Re-partir un área ya partida es no-op. Si una sección interna de
un hub supera a su vez el umbral, aplica la misma regla de forma recursiva
(`hub-<área>-<subclave>.md`): la jerarquía index → hub → sub-hub → página mantiene todo
lo anclado alcanzable en ≤3 saltos.

## Página-hub (`type: hub`)
`type: hub` queda definido por este gen (LINT lo reconoce como esquema, chequeo (e)). El
hub es estructura de navegación derivada del índice, no conocimiento con fuente:
frontmatter completo de [[gen-frontmatter-obligatorio]] con `confidence: 1.0`,
`decay_rate: low`, `sources: []`, `relations: {}`; su cuerpo son las anclas `[[...]]` del
área. Nunca queda huérfano (`index.md` lo enlaza; él enlaza sus anclas) y NUNCA lista
páginas `confidencial`. Plantilla:

    ---
    title: Hub — <área>
    type: hub
    tier: <tier del área>
    tags: [hub, <área>]
    confidence: 1.0
    created: <hoy>
    last_reinforced: <hoy>
    decay_rate: low
    sources: []
    relations: {}
    ---
