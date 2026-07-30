---
tipo: propuesta-evolve
tarea: F0-08
status: approved
fecha: 2026-07-29
genes_afectados: [gen-frontmatter-obligatorio]
origen: piloto Fase B, hallazgo H-08
---

# Propuesta EVOLVE F0-08 — `gen-frontmatter-obligatorio` v6 → v7: los campos también se extienden

> **Bajo compuerta**: este archivo solo PROPONE. Nada se aplica sin tu OK.

## Motivación

Hay una **asimetría en el diseño actual** que el piloto destapó al primer intento de usar
un gen de sector.

`gen-frontmatter-obligatorio` v6 dice que `relations` "ya no es un set cerrado": se amplía
con los verbos que declaran los genes activos y con los `relation_types` del manifiesto. Y
el validador lo cumple — `schema.allowed_verbs(m.relation_types)` lee el manifiesto.

Los **campos** no recibieron ese mecanismo. `lint.py` compara contra
`schema.KNOWN_FIELDS`, un conjunto de 22 entradas **fijo en código**, sin ninguna entrada
del manifiesto ni de los genes sembrados.

Consecuencia, reproducida en el piloto: el gen `gen-comparacion-declarada` —sembrado por
`onboard apply`, es decir **aprobado por compuerta**— exige que toda página que use
`compara_con` declare el campo `dimension`. Al escribirlo, LINT respondió:

```
[AVISO] FM-04 wiki/semantic/formatos/claude-md.md — campo fuera de esquema: 'dimension'
        (ningún gen lo declara; decláralo vía EVOLVE o retíralo)
```

**"Ningún gen lo declara" es literalmente falso**: lo declara un gen activo del propio
vault. El mensaje culpa al usuario de un hueco de la herramienta.

Lo que importa no es el aviso suelto: es que **todo vault sectorial con genes que pidan
campos propios arranca con avisos permanentes**. Y un aviso que siempre está es un aviso
que se deja de leer — precisamente la erosión que el enforcement mecánico existe para
evitar. Además envenena el score: `FM-04` cuenta en `_HIGIENE_CODES`, así que la salud
baja para siempre por cumplir una regla aprobada.

## Diff propuesto (v6 → v7)

Donde el gen habla de la extensibilidad de `relations`, extender el mismo principio a los
campos. Añadir tras el párrafo de `relations`:

```
Los CAMPOS siguen la misma regla que los verbos: el núcleo es el listado de arriba
(obligatorios + opcionales de este gen), ampliable con (a) los campos que los genes
activos declaren como esquema y (b) los `campos_extra` que la empresa declare en
`onboard/company.yaml`. LINT valida cada campo contra esa UNIÓN y solo marca FM-04
lo que no aparezca en ninguna de las tres fuentes. Un gen sembrado que exige un
campo lo está declarando: pedirlo y que el validador lo rechace sería incoherente.
```

## Cambio de infraestructura que lo acompaña

- `onboard/company.example.yaml`: documentar el bloque opcional
  `campos_extra: [<campo>, …]`.
- `manifest.py`: exponer `campos_extra` (validando que sean cadenas).
- `schema.py`: `allowed_fields(campos_extra)` — simétrico a `allowed_verbs`.
- `lint.py`: `set(p.fm) - schema.allowed_fields(...)` en vez de `- schema.KNOWN_FIELDS`.
- Tests: un vault con `campos_extra` no produce FM-04; sin declarar, sí.

**Nota deliberada**: esta propuesta NO hace que los `seed_genes` se parseen para extraer
campos automáticamente. Sería frágil (habría que adivinar el nombre del campo desde la
prosa de la regla). La declaración explícita en el manifiesto es el camino honesto: el
blueprint que siembra el gen declara también su campo, y ambos pasan por la misma
compuerta.

## Evidencia

- Reproducido en `C:\cerebro-piloto`: `piloto/hallazgos.md`, hallazgo H-08, con la
  comparación de mecanismos verificada en `schema.py:119` (verbos) frente a
  `lint.py:119` (campos).
- Estado del piloto tras el lote de calibración: 2 avisos FM-04 permanentes,
  `higiene 83/100`, por cumplir un gen aprobado.

## Orden de aplicación

1. Infra primero (`schema.py`, `manifest.py`, `lint.py`, ejemplo de manifiesto, tests).
2. Editar `genome/genes/gen-frontmatter-obligatorio.md` con el diff; `version: 7`.
3. `python tools/cerebro.py events append --type gene_edited --target gen-frontmatter-obligatorio --signal "F0-08: los campos se extienden como los verbos (H-08 del piloto)" --diff "v6 -> v7 (union nucleo + genes + campos_extra del manifiesto)"`
4. Commit + `python tools/cerebro.py mirror --fix` si `CLAUDE.md` cambia.
