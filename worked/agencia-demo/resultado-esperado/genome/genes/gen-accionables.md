---
id: gen-accionables
trigger: "la fuente genera un pendiente con fecha límite (follow-up, renovación, tarea de cuenta)"
status: active
version: 1
---

El accionable nace con type: accionable, clase: evento, fecha_objetivo: YYYY-MM-DD y estado: {abierto|hecho|vencido}; NO se refuerza por reingesta y NO se borra al vencer (queda como histórico de cuenta). LINT lo revisa: si fecha_objetivo < hoy y estado: abierto, lo reporta como vencido sin cerrar y propone escalar o cerrar. Distinto de valido_hasta (gen-vigencia-temporal), que gobierna caducidad de contenido, no deadlines de tareas.

> Gen de sector sembrado mecánicamente por ONBOARD desde `onboard/company.yaml` (2026-07-12).
> Mutarlo pasa por [[gen-compuerta-mutacion]] como cualquier gen.
