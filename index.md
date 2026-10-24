---
title: CEREBRO — índice
type: meta
updated: 2026-10-23
---

# 🧠 CEREBRO — mapa principal

Punto de entrada del cerebro. El agente lee este archivo primero y navega desde aquí
por las relaciones `[[...]]`. Mantener corto: solo páginas-ancla, no todo el contenido;
si una sección supera `hub_umbral` anclas, se parte en página-hub y aquí queda solo
`[[hub-<área>]]` ([[gen-jerarquizacion-indice]]).

## Estado
- Fase: **scaffolding listo** — pendiente correr `ONBOARD`.
- Empresa: _(sin configurar — ver [[company-profile]])_

## Genoma
- Reglas y operaciones: ver `CLAUDE.md`.
- Genes activos: carpeta `genome/genes/`.
- Cápsulas: [[ingesta-de-fuente]].
- Auditoría de mutaciones: `genome/events.jsonl`.
- Auto-auditoría: operación `AUDIT` → corridas en `audit/runs/`. Regla: [[gen-auto-auditoria]].
- Lente de grafo: operación `GRAPH` → salida derivada en `graphify-out/` (no versionada). Regla: [[gen-graph-lens]].
- Deriva declarado↔evidencia: operación `XRAY` → corridas en `audit/xray/`. Regla: [[gen-xray]].
- Perfil de instalación: `profile:` del manifiesto → `ONBOARD` lo aplica a `genome/perfil.md` (capacidades activas; sin archivo = completo). Regla: [[gen-perfiles]].
- Catálogo de blueprints: `onboard/blueprints/catalog.yaml` (versión, `min_cerebro`, historial) → `python tools/cerebro.py blueprints` dice si el manifiesto está al día. Regla: [[gen-onboard]], adopción por versión en [[gen-migracion-genoma]].

## Visualización (opcional, removible)
- Paneles nativos (Bases; Dataview opcional): `dashboards/00-leeme.md`. Plantillas por `type`: `templates/00-leeme.md`. Lente de grafo interactiva: `dashboards/graph/00-leeme.md`. Regla: [[gen-visualizacion]].

## Memoria (anclas por tier)
Aún vacío. Conforme ingieras fuentes, ancla aquí según [[gen-jerarquizacion-indice]]
(determinista: ni confidencial, ni working/episodic, ni `clase: evento`).

- **working/** — _(observaciones recientes)_
- **episodic/** — _(resúmenes de sesión)_
- **semantic/**
  - conceptos — _(vacío)_
  - entidades — _(vacío)_
  - fuentes — _(vacío)_
  - síntesis — _(vacío)_
- **procedural/** — _(SOPs y procesos)_

## Cómo empezar
1. Corre `ONBOARD` para adaptar el cerebro a tu empresa.
2. Suelta fuentes en `raw/` y corre `BULK INGEST`.
3. Consulta con `QUERY <tema>`.
4. Mantén con `LINT` y `CONSOLIDATE` cada 1–2 semanas.
