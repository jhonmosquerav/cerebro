---
id: gen-conflicto-interes
trigger: "se ingiere un cliente, caso o contraparte nuevo"
status: active
version: 1
---

Cruza el nuevo cliente/contraparte contra entities.clientes y entities.contrapartes existentes. Si una contraparte coincide con un cliente actual (o viceversa, o comparten matriz/grupo), marca relation 'contradice' + tag 'conflicto-interes' y ELEVA alerta en QUERY antes de aceptar el encargo. Si no hay coincidencia, deja constancia del chequeo pasado (no genera alerta).

> Gen de sector sembrado mecánicamente por ONBOARD desde `onboard/company.yaml` (2026-07-12).
> Mutarlo pasa por [[gen-compuerta-mutacion]] como cualquier gen.
