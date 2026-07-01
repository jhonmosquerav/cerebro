---
title: CEREBRO — índice
type: meta
updated: 2026-06-30
---

# 🧠 CEREBRO — mapa principal

Punto de entrada del cerebro. El agente lee este archivo primero y navega desde aquí
por las relaciones `[[...]]`. Mantener corto: solo páginas-ancla, no todo el contenido.

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

## Visualización (opcional, removible)
- Paneles Dataview: `dashboards/00-leeme.md`. Lente de grafo interactiva: `dashboards/graph/00-leeme.md`. Regla: [[gen-visualizacion]].

## Memoria (anclas por tier)
Aún vacío. Conforme ingieras fuentes, enlaza aquí las páginas-ancla de cada área.

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
