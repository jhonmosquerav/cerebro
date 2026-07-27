---
tipo: propuesta-evolve
tarea: F0-07
status: pending
fecha: 2026-07-26
genes_afectados: [gen-graph-lens, gen-jerarquizacion-indice]
---

# Propuesta EVOLVE F0-07 — `gen-graph-lens` v3 → v4: las señales estructurales dejan de depender de un backend externo

> **Bajo compuerta**: este archivo solo PROPONE. Nada se aplica sin tu OK.

## Motivación

`gen-graph-lens` v3 delega **todas** las señales del grafo a una lente externa
(graphify) que es "OPCIONAL y removible". La consecuencia práctica no estaba
declarada: **hoy, en un clon limpio sin graphify instalado, CEREBRO no sabe
quiénes son sus hubs.** Y eso no es cosmético —

- [[gen-jerarquizacion-indice]] parte una sección en página-hub *al superar
  `hub_umbral`*; el umbral vive en el manifiesto pero **nada medía el grado**;
- [[gen-consolidate]] espera "god-nodes/hubs → candidatos"; sin lente, no llegan;
- [[gen-lint]] quería las islas como "segunda opinión" sobre LNK-02; sin lente,
  no hay segunda opinión.

O sea: tres genes activos declaran consumir señales que el camino por defecto no
produce. El repaso de ecosistemas comparables (2026-07-26) dejó claro por qué
esto era evitable: componentes conexas, grado, puentes y caminos son **topología
pura** (BFS + Hopcroft-Tarjan), no necesitan modelo ni servidor. Lo que sí
necesita modelo es la parte semántica (comunidades por modularidad, "conexiones
sorprendentes"), y esa se queda donde está.

La frontera que propone esta mutación es exactamente esa: **estructural adentro,
semántico afuera**.

## Diff propuesto (v3 → v4)

Añadir al inicio del cuerpo del gen, antes del párrafo actual:

```
GRAPH tiene dos mitades con garantías distintas. La mitad ESTRUCTURAL es
mecánica, determinista y sin dependencias: `python tools/cerebro.py graph
[--scope wiki|genome|all]` deriva componentes conexas, grado, hubs contra el
`hub_umbral` del manifiesto, huérfanas, puntos de articulación (páginas-puente
cuya pérdida parte el grafo) y camino más corto entre dos páginas
(`graph <origen> <destino>`). Corre siempre, también en un clon sin graphify, y
da el mismo resultado en cada máquina — es la fuente canónica de las señales de
hub para [[gen-jerarquizacion-indice]] y [[gen-consolidate]], y de islas para
[[gen-lint]]. Al no salir del proceso no necesita copia staging: el filtro de
allowlist rige solo para lo que se exporta a un motor externo. La mitad
SEMÁNTICA (comunidades por modularidad, conexiones sorprendentes, resúmenes
narrados) sigue siendo de la lente externa descrita abajo, con su staging
fail-closed intacto. Si ambas discrepan, manda la estructural: es reproducible.
```

En `gen-jerarquizacion-indice` (v2 → v3), donde dice que una sección se parte al
superar `hub_umbral`, precisar la medición:

```
El grado se mide con `python tools/cerebro.py graph --scope all` (columna
`hubs`), no a ojo.
```

Y en la fila `GRAPH` de `CLAUDE.md`: "Corre una lente de grafo externa (local,
opcional)" → "Deriva señales estructurales de forma mecánica y sin dependencias
(`graph`), y opcionalmente corre una lente externa para lo semántico".

## Evidencia

- `tools/cerebro_core/graph.py` + `tests/test_graph.py` (14 casos de topología,
  incluido un camino de 3000 nodos que confirma que la implementación iterativa
  no desborda la recursión de Python).
- Corrida real sobre este repo (`--scope all`, 31 nodos / 111 aristas):
  1 sola componente, 0 huérfanas, 10 hubs con grado ≥ 7 — encabezados por
  `gen-frontmatter-obligatorio` y `gen-jerarquizacion-indice` (grado 13).
- Hallazgo que ninguna herramienta anterior podía dar: **`index.md` es el único
  punto de articulación del grafo completo.** Quitarlo desconecta el vault. Es
  la confirmación estructural del principio 3 ("navega SIEMPRE desde
  `index.md`") y, al mismo tiempo, la medida de su fragilidad: toda la
  navegabilidad cuelga de un archivo. Vale la pena decidir si eso es diseño
  aceptado o riesgo a mitigar — pero ahora es un número, no una intuición.
- Sobre `--scope genome` (27 nodos): `company-profile.md` sale como isla, lo
  cual es correcto en el template (sin ONBOARD corrido nadie lo enlaza).

## Lo que esta propuesta NO hace

No toca el invariante duro de confidencialidad: la allowlist fail-closed del
staging sigue igual para la lente externa. No implementa detección de
comunidades (modularidad) ni centralidad de intermediación: son útiles pero no
deterministas de la misma forma, y meterlas aquí borraría la frontera que esta
propuesta quiere trazar. No importa nada a `wiki/` — la salida sigue siendo
derivada y regenerable.

## Orden de aplicación

1. Editar `genome/genes/gen-graph-lens.md`; `version: 4`.
2. Editar `genome/genes/gen-jerarquizacion-indice.md`; `version: 3`.
3. Editar la fila `GRAPH` de `CLAUDE.md`.
4. Dos eventos (1 por gen), p. ej.:
   `python tools/cerebro.py events append --type gene_edited --target gen-graph-lens --signal "F0-07: mitad estructural mecánica y sin dependencias; semántica sigue en la lente externa" --diff "v3 → v4 (comando graph: componentes, grado, hubs, puentes, camino)"`
5. Commit por mutación + `python tools/cerebro.py mirror --fix`.
