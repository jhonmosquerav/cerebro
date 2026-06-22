---
id: gen-entidad-con-estado
trigger: entidad cuyo estado cambia en el tiempo (máquina, lead, caso, pedido, episodio)
status: active
version: 1
---

Una entidad con campo `estado` se actualiza **in-place**: nunca se duplica al cambiar de
estado (respeta la idempotencia). Pero todo cambio de estado debe **originarse en una página
`clase: evento`** ([[gen-clase-temporal]]) que la enlace, para que el historial quede en el
rastro de eventos y no se pierda en sobrescrituras. Cuando una entidad se transforma en otra
(lead→cliente), la anterior **no se borra**: se enlazan con relación tipada (`sucede_a` /
`proviene_de`) conservando trazabilidad. LINT marca toda entidad cuyo `estado` cambió sin un
evento de respaldo que lo justifique.
