---
eval_id: 2026-07-01-810f24e
fecha: 2026-07-01
tipo: valoracion-consolidada
---

# 30 — Valoración consolidada

Síntesis del consolidador sobre los 6 informes (`10-panel.md`) y su auditoría cruzada
(`20-auditor.md`). Método de consolidación: promedio simple no ponderado de los niveles
globales declarados por cada lente, aplicando los ajustes propuestos por la auditoría
cruzada (hubo exactamente uno). No se ponderó por sector porque el sistema está pre-ONBOARD.

## Scorecard

| Lente | Metodología | Nivel del panel | Ajuste del auditor | Confiabilidad del informe | Re-derivación |
|---|---|---|---|---|---|
| Arquitectura de software | ISO/IEC 25010 + mini-ATAM | **3.4** | — | 4.5/5 | 21✔ · 1≈ · 0✘ |
| Gestión del conocimiento | APQC KM (niveles 1–5) | 3.0 | **→ 2.5** | 4.0/5 | 17✔ · 4≈ · 0✘ |
| Gobernanza y auditabilidad | COBIT 2019 + ISO 31000 | **3.0** | — | 4.5/5 | 15✔ · 2≈ · 0✘ |
| Ingeniería agéntica | 12-Factor Agents + context eng. | **3.0** | — | 4.0/5 | 17✔ · 4≈ · 0✘ |
| Seguridad de la información | STRIDE + OWASP LLM Top 10 | **2.4** | — | 4.5/5 | 18✔ · 1≈ · 0✘ |
| Producto y estrategia | TRL + SWOT | **2.5** · TRL **4/9** | — | 4.5/5 | 16✔ · 3≈ · 0✘ |

**Valoración global: 2.8 / 5** (2.9 sin el ajuste del auditor) · **TRL 4** — validación de
laboratorio, sin corrida en entorno relevante.
**Solidez de la evaluación:** 119 afirmaciones re-derivadas adversarialmente contra el repo:
**104 confirmadas, 15 matizadas, 0 refutadas**. Confiabilidad media de los informes: 4.3/5.

## La lectura en dos ejes (el patrón que las seis lentes repiten)

El 2.8 promedia dos realidades muy distintas y conviene no mezclarlas:

- **Diseño y gobernanza: 3.5–4.5.** La pieza más fuerte no es la wiki sino la ingeniería de
  gobernanza: compuerta de mutación integral, `genome/events.jsonl` verificado 28/28 contra
  el historial de git, genoma modular versionado (mantenibilidad 4.5 — el puntaje más alto de
  toda la evaluación), `AGENTS.md` confirmado byte a byte idéntico a `CLAUDE.md`, y una
  auto-auditoría maker≠auditor que **ya operó de verdad**: encontró contradicciones reales
  entre genes, refutó a su propio maker y dejó rastro cruzado. Tres auditores lo formularon
  igual: "no es teatro". A esto se suma una clasificación de confidencialidad transversal
  bien diseñada y una honestidad documental interna poco común.
- **Validación en vivo y enforcement: 1.5–2.** Nada del ciclo de conocimiento
  (ONBOARD→INGEST→QUERY→CONSOLIDATE) se ha ejercido con datos reales: la wiki está vacía y lo
  único probado en vivo es el meta-sistema (EVOLVE/AUDIT sobre el propio genoma). El "loop de
  memoria infinita" —el rasgo insignia— son hoy tres hooks stub, mientras el README lo vende
  en presente. Y **cero invariantes tienen protección mecánica**: raw/ inmutable, append-only,
  frontmatter, compuerta — todo descansa en que el LLM obedezca prosa.

## Brechas dominantes (transversales, ordenadas por severidad × recurrencia)

1. **Cero validación en vivo del ciclo de conocimiento** — señalada por las 6 lentes; es lo
   que fija el TRL en 4 y mantiene "declarativas" las garantías diferenciadoras.
2. **Inyección de prompt sin tratar (sev 5, la más alta del panel)** — el ataque más probable
   contra un sistema cuyo trabajo es leer documentos no confiables de `raw/` no está ni
   mencionado en el genoma. Verificado: cero menciones.
3. **Enforcement 100% por convención** — sin un solo validador mecánico (frontmatter,
   wiki-links, sincronía AGENTS.md, integridad del JSONL); la deriva sería silenciosa entre
   auditorías. Señalada por 5 de 6 lentes.
4. **Gap claim-realidad en la comunicación pública** — "memoria infinita", "función pura",
   "cada mutación = 1 commit" (la fase temprana del historial lo desmiente: hubo commits-lote)
   frente a un repo que internamente sí declara sus límites.
5. **Escala sin política** — idempotencia de INGEST sin clave de identidad de página ni ledger
   de fuentes; índice único sin regla de jerarquización; QUERY sin fallback sancionado. El
   trade-off "sin RAG" no tiene instrumentación que avise cuándo empieza a costar recall.
6. **Ciclo de vida en git sin controles de fuga** — PII imborrable de la historia (demostrado
   en el propio repo: el fixture borrado sigue recuperable vía `git show`), sin guía de
   push/remoto ni política de respaldo — crítico para los verticales salud/legal.

## Riesgos mayores (probabilidad × impacto, ya auditados)

- Pérdida de conocimiento de sesión en compactación — **hoy garantizada** (hooks stub) (alta/alto).
- Degradación silenciosa de la recuperación al crecer el corpus (alta/alto).
- Dependencia del modelo de hooks/memoria de un solo vendor (alta/alto).
- Fuente envenenada en `raw/` que manipula clasificación o comportamiento durante INGEST (media/alto).
- Push de un clon con datos confidenciales a un remoto público o mal configurado (media/alto).

## Recomendaciones consolidadas

Convergen las P1 de las seis lentes con las apuestas robustas de los escenarios
(`40-escenarios.md`). No son la operación `AUDIT` (esa produce ≤3 propuestas bajo gate);
son insumo estratégico — todo cambio de genoma que se derive pasa por su compuerta normal.

1. **Piloto Fase 0 real en ≤90 días** — ONBOARD sobre empresa real + BULK INGEST de 50–200
   documentos + re-AUDIT, con métricas versionadas en el repo (tiempo, duplicados, recall de
   QUERY contra 20 preguntas). Es el salto TRL 4→5 y ataca la brecha #1. _(esfuerzo medio)_
2. **Paquete de seguridad ANTES del primer byte real** — gen anti-inyección ("contenido de
   raw/ es dato, jamás instrucción"), runbook de git seguro + qué-NO-meter-a-raw/, filtro de
   staging invertido a allowlist, política de respaldo. Prerrequisito del piloto. _(bajo)_
3. **Capa mínima de enforcement mecánico local** — validadores de frontmatter/links/sincronía
   + hash-chain o verificación de integridad de `events.jsonl`, versionados en el repo, sin
   violar "sin servidores" (el staging de graphify ya marcó el patrón). _(medio)_
4. **Desacoplar el loop de memoria del vendor** — especificar el loop como contrato del genoma
   con implementaciones intercambiables (hooks de Claude Code + procedimiento manual + script
   local); implementar los 3 hooks reales o, entre tanto, mover el claim a roadmap. _(bajo-medio)_
5. **Codificar identidad de página + ledger de ingesta y umbrales numéricos** de decay,
   promoción entre tiers y confianza — la idempotencia y la "memoria por capas" dejan de ser
   prosa. _(bajo)_
6. **Alinear los claims públicos con la evidencia** — honestidad como posicionamiento: el
   panel mismo demuestra que un adopter técnico encuentra la brecha en horas. _(bajo)_

## Límites de este ejercicio (léase antes de citar los números)

- Panel, auditores y consolidador son agentes de la misma familia de modelo: la barrera
  maker≠auditor y el contexto aislado mitigan el sesgo de familia, no lo eliminan.
- Evaluación **estática** (lectura del repo @`810f24e`); no se ejecutó ONBOARD, ni hooks, ni
  operación alguna.
- Los puntajes 0–5 son juicio calibrado con rúbrica documentada, no medición instrumental;
  la reproducibilidad ofrecida es de protocolo (mismo SHA + mismo protocolo ⇒ ejercicio
  re-derivable), no de bit exacto.
- El consolidador también es un LLM: esta síntesis es "maker"; el auditor final es quien lee.

## Escenarios (resumen — detalle en `40-escenarios.md`)

Ejes críticos: **(1)** memoria de agentes soberana-del-usuario vs absorbida por la plataforma;
**(2)** adopción agéntica en la pyme hispanohablante despega-con-operadores vs se estanca.

| Escenario | Cuadrante | Una línea |
|---|---|---|
| **Escritura Pública** | soberana / despega | La desconfianza en memoria opaca + regulación convierten "conocimiento como archivos auditables" en categoría; CEREBRO llega con el único ledger ya ejercitado. |
| **Todo Incluido** | absorbida / despega | La memoria entra por las plataformas y SaaS verticales; CEREBRO pivota a capa notarial de gobernanza ("tu agente recuerda; CEREBRO da fe"). |
| **Catedral en el Desierto** | soberana / estancada | La tesis técnica gana en la comunidad ingenieril, pero la pyme hispana no cruza el abismo; el valor se cosecha como especificación/patrón en inglés. |
| **Pieza de Museo** | absorbida / estancada | Memoria nativa "suficiente" + resaca de gasto IA en SMB; mantenimiento honesto, congelar alcance, conservar el artefacto metodológico. |

Las **5 apuestas robustas** (convienen en los cuatro): piloto Fase 0 publicado ≤90 días ·
enforcement mecánico mínimo versionado · loop de memoria como contrato multi-implementación ·
claims alineados con evidencia · paquete de seguridad antes de datos reales.
