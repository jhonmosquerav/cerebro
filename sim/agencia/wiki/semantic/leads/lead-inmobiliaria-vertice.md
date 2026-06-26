---
title: Lead — Inmobiliaria Vértice
type: entidad
tier: semantic
tags: [lead, inmobiliaria, sql, en-negociacion]
confidence: 0.85
created: 2026-06-22
last_reinforced: 2026-06-22
decay_rate: medium
estado: en-negociacion-sin-followup
sources:
  - "[[raw/2026-05-12-call-inmobiliaria-vertice]]"
  - "[[raw/2026-05-15-propuesta-inmobiliaria-vertice]]"
relations:
  usa:
    - "[[bot-captacion-leads]]"
    - "[[objecion-bot-malo]]"
    - "[[objecion-precio-alto]]"
  depende_de: []
  contradice: []
  reemplaza: []
  recibio_propuesta: ["[[propuesta-vertice-PROP-2026-038]]"]
  tiene_followup: ["[[followup-vertice-2026-05-16]]"]
advertencia:
  - "propuesta [[propuesta-vertice-PROP-2026-038]] con precio vencido 2026-06-14; validar precio antes de avanzar en negociación."
  - "follow-up [[followup-vertice-2026-05-16]] vencido 2026-05-16; junta decisión 2026-05-19 ya pasó. Validar si lead sigue activo o se perdió."
---

# Lead — Inmobiliaria Vértice

Inmobiliaria con 4 agentes y ~200 consultas/mes (web + WhatsApp); pierde ~50% de leads por
respuesta lenta y falta de calificación. Contacto: Laura Méndez (Directora Comercial).

- **Necesidad**: SLA de primera respuesta + calificación (presupuesto, zona, compra/renta).
- **Fit**: alto, encaja con [[bot-captacion-leads]]. Volumen alto = tier de mantenimiento medio.
- **Objeciones planteadas**: [[objecion-bot-malo]] ("ya tuvimos un bot malo") y
  [[objecion-precio-alto]] (la competencia cotizó USD 8,000 de setup).
- **Estado**: recibió [[propuesta-vertice-PROP-2026-038]]; decisión en junta del lunes 2026-05-19.
- **Pendiente**: [[followup-vertice-2026-05-16]] antes de su junta.

> Si firma, este lead se convertirá a cliente vía [[gen-lead-a-cliente]] (no se borra: se
> enlaza `reemplaza_por` hacia la página de cliente y se conserva su historial).
