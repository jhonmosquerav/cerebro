---
tipo: propuesta-evolve
tarea: F0-11
status: pending
fecha: 2026-07-29
genes_afectados: [gen-onboard]
origen: piloto Fase B, hallazgo H-07
---

# Propuesta EVOLVE F0-11 — `gen-onboard` v5 → v6: avisar cuando la taxonomía no cubre los tipos declarados

> **Bajo compuerta**: este archivo solo PROPONE. Nada se aplica sin tu OK.

## Motivación

El genoma declara cinco tipos de página: `concepto | entidad | fuente | sintesis | sop`.
La taxonomía de carpetas la escribe el operador en `onboard/company.yaml`. **Nada comprueba
que la segunda cubra a la primera.**

En el piloto escribí una taxonomía con ocho carpetas —`sistemas, conceptos,
organizaciones, formatos, autores, specs, benchmarks, normativa`— y **ninguna para
`sintesis`**. `onboard apply` la aplicó sin decir nada; el validador del manifiesto la dio
por buena; LINT tampoco tenía nada que objetar, porque el defecto solo se manifiesta
cuando intentas crear una página de ese tipo y descubres que no hay dónde ponerla.

En este caso no dolió, pero por suerte y no por diseño: la decisión correcta resultó ser
no crear páginas de tipo `fuente` (la trazabilidad va en el campo `sources`, y una página
por documento habría duplicado el manifiesto dentro de la wiki). Con `sintesis` sí habría
dolido: el manifiesto declara `sintesis_umbral: 3`, o sea que el propio vault se
compromete a generar síntesis en cuanto haya 3 eventos con clave común — y no tiene
carpeta para ellas. Se descubriría a mitad de una operación CONSOLIDATE.

**Coste de descubrirlo tarde**: crear la carpeta a posteriori es trivial, pero cambia la
taxonomía después de que `onboard apply` fijó el hash de estado. Deja de ser reproducible
desde el manifiesto, que es la garantía que ONBOARD vende.

## Diff propuesto (v5 → v6)

Añadir al final de la parte mecánica del gen:

```
La herramienta AVISA (no aborta) cuando la `taxonomy` del manifiesto no ofrece
destino para alguno de los tipos de página que el genoma declara —en particular
`sintesis`, que el propio manifiesto se compromete a producir al fijar
`sintesis_umbral`—. Es aviso y no error porque una empresa puede decidir
legítimamente no usar un tipo; lo que no puede es descubrirlo a mitad de un
CONSOLIDATE. Cambiar la taxonomía después de aplicar rompe la reproducibilidad
desde el manifiesto: el aviso llega cuando corregirlo es gratis.
```

## Cambio de infraestructura que lo acompaña

- `manifest.py` o `onboard.py`: comprobar la cobertura tipo → carpeta y emitir aviso en la
  salida de `onboard apply` (y en `manifest.validate`, para que `verify` lo vea).
- Tests: un manifiesto sin destino para `sintesis` produce el aviso y **sigue aplicando**.

## Evidencia

- `C:\cerebro-piloto`: `onboard/company.yaml` con 8 carpetas y ningún destino para
  `sintesis` ni `fuente`; `onboard apply` lo aceptó en silencio (corrida del 2026-07-27).
- `piloto/hallazgos.md`, hallazgo H-07.

## Severidad y honestidad sobre la prioridad

**Baja.** Es la más pequeña de la tanda del piloto y la que menos urge: no corrompe datos
ni métricas, solo deja una trampa para más adelante. Si hay que recortar el gate, esta es
la primera que se cae — y lo digo aquí para no venderla como más importante de lo que es.

## Orden de aplicación

1. Infra (`manifest.py`/`onboard.py` + tests).
2. Editar `genome/genes/gen-onboard.md`; `version: 6`.
3. `python tools/cerebro.py events append --type gene_edited --target gen-onboard --signal "F0-11: avisar si la taxonomia no cubre los tipos declarados (H-07 del piloto)" --diff "v5 -> v6 (aviso de cobertura tipo -> carpeta)"`
4. Commit + `python tools/cerebro.py mirror --fix` si aplica.
