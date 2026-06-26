---
id: gen-fix-precio-vigencia
trigger: la fuente menciona un precio
status: active
version: 1
---

NUNCA se cita un precio cuya fecha de vigencia ya pasó. Si `valido_hasta < hoy`,
QUERY debe abstenerse de citarlo. Contradice directamente a [[gen-fix-precio-abierto]].
