---
tipo: propuesta-evolve
tarea: F0-06
status: approved
fecha: 2026-07-26
genes_afectados: [gen-lint]
depende_de: [F0-01]
---

# Propuesta EVOLVE F0-06 — `gen-lint` v5 → v6: enlace sugerido (LNK-03)

> **Bajo compuerta**: este archivo solo PROPONE. Nada se aplica sin tu OK.

## Motivación

Los detectores de conectividad de LINT son los dos **reactivos**: LNK-01 avisa de
un enlace roto y LNK-02 de una huérfana; ambos solo hablan cuando el daño ya
existe. Falta el **preventivo**: la página que menciona en prosa a otra página
existente y no la enlaza. Esa es la causa raíz de las huérfanas, no un síntoma.

Evidencia propia, no teórica: el episódico `2026-07-02-f1fc904c` nació huérfano
el 2026-07-02, `log.md` lo arrastró como lastre de conectividad (salud 87/100)
desde el 2026-07-12, y se cerró **a mano** el 2026-07-26. Trece días de deriva
silenciosa por una relación que el texto ya implicaba. El repaso de ecosistemas
comparables (2026-07-26) mostró que varios auto-insertan el `[[wikilink]]` al
escribir; CEREBRO **no puede hacer eso** —violaría la compuerta y la regla de no
sobrescribir lo que no creaste tú— pero sí puede *proponerlo*, que es su modo
nativo de operar.

## Diff propuesto (v5 → v6)

En la lista de detectores del gen, añadir:

```
(f) enlaces sugeridos — MECÁNICO: `lint` emite LNK-03 (severidad `info`) por
cada página de `wiki/` que menciona en prosa el basename, `title` o `id_alias`
de otra página existente sin enlazarla. Es una PROPUESTA, no un defecto: el
agente decide si la relación es real y, si lo es, la aplica editando la página
(cuerpo o `relations`) — el detector JAMÁS reescribe la página, ni siquiera
cuando la mención es inequívoca. Dos invariantes acotan el detector: nunca
propone como destino una página `sensibilidad: confidencial` (nombrarla
expondría su título, metadato reidentificador — [[gen-confidencialidad]]) y
nunca toma como origen una página en cuarentena `riesgo_inyeccion: true` (su
texto es dato no confiable y no debe dirigir la topología del grafo —
[[gen-anti-inyeccion]]). Se excluyen del rastreo el código en bloque y en
línea, las URLs y los wikilinks ya puestos.
```

Y en la fila de `LINT` de `CLAUDE.md` (tabla de operaciones), tras "verbos y
campos fuera de esquema": añadir "enlaces sugeridos (LNK-03, preventivo)".

## Evidencia

- `tools/cerebro_core/graph.py` (`sugerencias`, `texto_buscable`) +
  `tools/cerebro_core/lint.py` (`_check_link_suggestions`).
- `tests/test_graph.py`: 15 casos del sugeridor, incluidos los dos invariantes
  de seguridad, el tope por página, la frontera de token con guion
  («gen-lint» no dispara dentro de «gen-lint-v5») y la exclusión de
  código/URL/wikilink.
- En el repo real, el detector encuentra hoy **5 positivos verdaderos** en
  `wiki/episodic/2026-07-02-86919843.md` (menciona `gen-bulk-ingest`,
  `gen-clase-temporal`, `gen-confianza-por-fuente`, `gen-consolidate` y
  `gen-frontmatter-obligatorio` en texto plano mientras sí enlaza a otros genes
  en la misma frase). El fixture `vault-limpio` sigue con 0 hallazgos: el
  detector no introduce ruido de base.
- Severidad `info` a propósito: no altera `exit_code` ni el score de `health`
  (`_CONECT_CODES` sigue siendo `{LNK-01, LNK-02}`), así que no puede volver
  rojo un CI que hoy está verde.

## Riesgo y por qué es aceptable

Falsos positivos: una mención puede ser casual ("consolidate" como verbo común).
Se mitigó con longitud mínima de término (5), coincidencia por palabra completa
sin cortar tokens con guion, y tope de 5 sugerencias por página. Como es `info`
y el agente juzga antes de aplicar, un falso positivo cuesta una línea de
reporte, no una edición equivocada.

## Orden de aplicación

1. Editar `genome/genes/gen-lint.md` con el diff; `version: 6`.
2. Editar la fila `LINT` de `CLAUDE.md`.
3. `python tools/cerebro.py events append --type gene_edited --target gen-lint --signal "F0-06: LNK-03 enlace sugerido, detector preventivo de conectividad" --diff "v5 → v6 (detector f: enlaces sugeridos, info, con invariantes de confidencialidad y cuarentena)"`
4. Commit + `python tools/cerebro.py mirror --fix`.
