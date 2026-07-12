---
id: gen-version-clausula
trigger: "la fuente es una versión nueva de un contrato o cláusula-tipo ya existente"
status: active
version: 1
---

Crea página nueva de la versión y marca relation 'reemplaza' hacia la anterior, que pasa a confidence<=0.4 y tag 'historico'; nunca borres la vieja (rastro de negociación). Las cláusulas-tipo reutilizables se enlazan vía 'instancia' desde los contratos que las usan, para rastrear qué contratos hay que revisar cuando cambia la cláusula base.

> Gen de sector sembrado mecánicamente por ONBOARD desde `onboard/company.yaml` (2026-07-12).
> Mutarlo pasa por [[gen-compuerta-mutacion]] como cualquier gen.
