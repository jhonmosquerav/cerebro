---
tipo: propuesta-evolve
tarea: F0-13
status: approved
fecha: 2026-08-07
genes_afectados: [gen-auto-auditoria]
origen: AUDIT 2026-08-07-a09385e del piloto (hallazgo transversal del auditor + M-07)
---

# Propuesta EVOLVE F0-13 — `gen-auto-auditoria` v5 → v6: rúbrica que no aplana, desempate que no se agota, snapshot en orden

## Motivación (del primer AUDIT con wiki viva)

1. **La rúbrica aplana los vacíos**: la fila "vacío" fija `alcance = 1` (única fila
   con constante), así que un vacío que afecta 9 páginas (M-04) puntúa igual que uno
   de 1 — el ranking real lo terminan decidiendo los desempates, no el impacto. El
   maker contó objetos (correcto en espíritu, contra la letra); el auditor lo detectó.
2. **El desempate se agota**: con tres candidatos sobre `index.md` el criterio (3)
   "ruta alfabética" empata también; el auditor tuvo que inventar un 4º criterio.
3. **M-07**: el orquestador corrió `health --json` antes de `xray --write` y el
   snapshot quedó autocontradictorio (`deriva: null` junto a `xray.json`).

## Diff (v5 → v6)

- Fila de la rúbrica: `vacío / verbo-o-campo fuera de esquema: **conteo de objetos
  afectados por el MISMO defecto** (páginas, secciones o campos; 1 si es único)`.
- Desempate: añadir criterio (4) — menor número de línea del defecto en el archivo.
- Sección Detección: el orquestador corre `xray --write` ANTES de `health --json`.
