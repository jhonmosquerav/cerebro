# Caso Fase B — el piloto con corpus real, con métricas y sin fe

**Fecha de cierre: 2026-08-07.** Este documento sustituye a la narrativa de la simulación
borrada (evaluación `2026-07-01-810f24e`): es el caso B-06 del backlog, con cada claim
anclado a un artefacto verificable. Marca el salto **TRL 4 → TRL 5** (validación en
entorno relevante: vault vivo, corpus real, operaciones reales).

## El montaje

- **Vault**: clon del template en `C:\cerebro-piloto` (creado 2026-07-27 desde `5ce717b`;
  remoto con push deshabilitado para que el corpus no entre al producto).
- **Entidad**: "Observatorio de Memoria Agéntica" (entidad de trabajo, sin datos
  personales; corpus 100% de fuentes públicas de terceros).
- **Corpus**: 73 documentos en 6 ejes (contrato-agente, grafo-conocimiento,
  gobernanza-auditoría, memoria-agéntica, ecosistemas, reproducibilidad), 6,5 MB.
  **No se versiona** (sería redistribución): se versionan `corpus/fuentes.tsv` y
  `corpus/corpus-manifest.jsonl` (url + sha256 + licencia + fecha) — un tercero
  re-descarga y verifica con `corpus/descargar.py --verify`.
- **Genoma**: el del template adoptado por la doctrina F0-12 — primer evento
  `genome_adopted` real (línea 74 de la cadena del piloto, referencia
  `template@9692dd2`, hash genome `afb2a9aa…`), más 3 genes de sector propios.

## Las métricas (B-02, B-03, B-04)

| Métrica | Resultado | Verificación |
|---|---|---|
| Cobertura de ingesta (B-02) | **72/73 fuentes** (la 73ª: PDF sin extractor, salto declarado) | `ingest-ledger.jsonl` (72 líneas con procedencia origen→derivado→páginas) |
| Lotes con lint en 0 errores | **11/11** | 1 commit por lote en el historial del piloto |
| Idempotencia (B-03) | re-corrida salta **72/72** por ledger; **0 duplicados**; 0 `id_pagina` repetidos en 71 páginas | algoritmo de [[gen-identidad-de-pagina]], ejecutado mecánicamente |
| Recall QUERY (B-04) | **20/20** preguntas doradas (meta ≥16/20), **20 por navegación pura** desde `index.md`, 0 fallback léxico | agente fresco sin acceso al corpus ni a la sesión de ingesta |
| Salud final | **99/100** (cobertura 99: PDF NIST; deriva 96: bug de resolución de tools, abajo) | `cerebro health` sobre `574adb0` |
| AUDIT poblado (B-05) | corrida `2026-08-07-a09385e`: 10 candidatos confirmados, top-3 aplicado | `audit/runs/` del piloto, maker≠auditor en disco |

**Identidad verificable del estado final del piloto** (para re-derivar cualquier claim):
commit `574adb0` · hash genome `9b9d69e1…` · hash knowledge `b93b8845…` ·
`genome/events.jsonl` 74 líneas encadenadas · 80 páginas de wiki (30 conceptos,
17 sistemas, 8 specs, 6 formatos, 5 normativa, 2 benchmarks, hubs y tiers de memoria).

## Lo que el piloto probó del genoma (con evidencia de uso, no de lectura)

- **F0-12 funciona**: la adopción template→vault preservó las dos cadenas, el pase de
  migración cerró los FM-04 pendientes vía `campos_extra`, y los 3 genes de sector
  locales convivieron sin conflicto.
- **La idempotencia es por algoritmo**, no por prosa: ledger + hash + `id_pagina`
  determinista dieron 0 duplicados con 23 páginas multi-fuente legítimas.
- **El índice escala con política**: 3 secciones superaron `hub_umbral` y el recall no
  degradó; CONSOLIDATE las partió en páginas-hub cuando le tocó (no antes).
- **Los genes de calidad operaron solos**: el agente QUERY emitió advertencias de
  vigencia (spec MCP con sucesora) y de confianza (0.75/0.6) sin que se le pidieran;
  gen-comparacion-declarada bloqueó comparaciones asimétricas en 11 lotes.

## Los límites, sin maquillar

1. Las 20 preguntas doradas las redactó el orquestador de la misma corrida (no un
   tercero ciego); mitigación: respuestas esperadas ancladas a frases del corpus y agente
   QUERY sin acceso al corpus.
2. `nist-ai-rmf` (PDF) quedó fuera: no hay extractor de PDF. Deuda declarada.
3. La deriva de `health` marca 96 por un **bug de tools** (M-05 del AUDIT): el resolutor
   del xray colisiona wikilinks con archivos homónimos de `corpus/texto/`. Va al backlog
   de infra del template.
4. 5 LNK-03 falsos positivos reaparecerán en cada lint: no existe la marca
   "revisado-y-rechazado" (candidato a EVOLVE).
5. El piloto corrió entero en un día por un solo operador+agente; no mide colaboración
   multi-operador ni deriva de largo plazo.

## Lo que alimenta el siguiente ciclo (EVOLVE con compuerta)

~20 candidatos a EVOLVE anotados lote a lote en el `log.md` del piloto, agrupables en:
reglas de agrupación de ingesta (entidad+satélites, benchmark→página-capacidad,
renombre de entidad), extensibilidad restante (vocabulario `type` cerrado en código vs
taxonomía del manifiesto — la misma asimetría que H-08 resolvió para campos),
confianza con fuentes mixtas y capturas parciales, higiene de señales (LNK-03
revisado-y-rechazado, exclusión de nombres de archivo), y AUDIT (rúbrica que aplana
vacíos, desempate agotable, orden xray→health en el snapshot). **Ninguno aplicado**:
esperan redacción de propuesta y gate, como manda [[gen-compuerta-mutacion]].
