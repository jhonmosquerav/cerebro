---
eval_id: 2026-07-01-810f24e
fecha: 2026-07-01
tipo: snapshot
ejercicio: evaluacion-multidisciplinar
---

# 00 — Snapshot de identidad de la evaluación

Identidad reproducible de esta **evaluación multidisciplinar externa**. No es una corrida de
la operación `AUDIT` ([[gen-auto-auditoria]] produce ≤3 propuestas accionables); es un
ejercicio puntual de **valoración de lo desarrollado + planeación por escenarios**, que
hereda las convenciones de reproducibilidad de `audit/runs/` (claveado a SHA, maker≠auditor,
artefactos numerados).

## Estado de git
- `git -C D:/cerebro rev-parse --short HEAD` → `810f24e`
- `git status --porcelain` → **vacío (árbol limpio)** al inicio de la evaluación.
- HEAD: `fix(index): anclas de GRAPH/gen-graph-lens + visualizacion (AUDIT C7)`
- **eval-id = `2026-07-01-810f24e`** (`<YYYY-MM-DD>-<short-SHA>`). Misma base ⇒ evaluación
  re-derivable con el mismo protocolo.

> Nota de transparencia: la carpeta `audit/evaluations/2026-07-01-810f24e/` se crea DESPUÉS
> de capturar el SHA; la identidad canónica es `810f24e`, capturado con árbol limpio.

## Objeto evaluado
Plantilla CEREBRO **pre-ONBOARD**: genoma de 20 genes + 1 cápsula, 28 eventos en
`genome/events.jsonl`, 5 blueprints sectoriales, capa de visualización opcional, hooks
declarados (stub), `wiki/` y `raw/` vacíos (solo `.gitkeep`), 1 corrida AUDIT previa
(`audit/runs/2026-06-30-7c840d0/`).

## Protocolo (reproducible)
Panel de **6 evaluadores disciplinares independientes** (agentes con contexto aislado,
solo-lectura), cada uno con una metodología estándar de industria; **auditoría cruzada
adversarial** de cada informe por un auditor que no lo escribió (barrera maker≠auditor, el
mismo estándar que CEREBRO se exige en [[gen-auto-auditoria]]); y una fase final de
**escenarios** con insumo exclusivamente en hallazgos que sobrevivieron la auditoría.

| # | Lente | Metodología de industria |
|---|---|---|
| 1 | Arquitectura de software | ISO/IEC 25010 + mini-ATAM (SEI): trade-offs, puntos de sensibilidad, no-riesgos |
| 2 | Gestión del conocimiento | APQC KM Capability Assessment (niveles 1–5 por dimensión) |
| 3 | Gobernanza y auditabilidad | COBIT 2019 (diseño/cumplimiento de controles) + ISO 31000 (riesgo residual) |
| 4 | Ingeniería agéntica | Checklist 12-Factor Agents + context engineering (estado real de hooks, enforcement, idempotencia) |
| 5 | Seguridad de la información | STRIDE + OWASP Top 10 for LLM Applications + controles ISO 27001 |
| 6 | Producto y estrategia | TRL (NASA/Horizon Europe 1–9) + análisis de diferenciación + SWOT (insumo de escenarios) |

**Escenarios:** metodología Peter Schwartz / Global Business Network (Shell): fuerzas
motrices → impacto×incertidumbre → 2 incertidumbres críticas ortogonales → matriz 2×2 →
4 escenarios con señales tempranas → apuestas robustas. Horizonte 18–24 meses.

## Reglas del encargo (aplicadas a los 13 agentes)
1. Solo lectura: ningún agente escribe, edita ni toca git.
2. Toda afirmación cita evidencia como ruta relativa del repo.
3. Distinguir lo **diseñado/documentado** de lo **validado en vivo** (estado pre-ONBOARD).
4. Escala 0–5: 0 inexistente · 1 incipiente · 2 parcial · 3 adecuado · 4 sólido · 5 ejemplar.
5. El insumo de escenarios excluye afirmaciones refutadas por la auditoría cruzada.

## Artefactos de esta evaluación
- `00-snapshot.md` — este archivo (identidad + protocolo).
- `10-panel.md` — los 6 informes disciplinares (puntuaciones, evidencia).
- `20-auditor.md` — veredictos de la auditoría cruzada + confiabilidad por informe.
- `30-valoracion.md` — valoración consolidada: scorecard, TRL, veredicto global.
- `40-escenarios.md` — fuerzas motrices, matriz 2×2, 4 escenarios, apuestas robustas.
