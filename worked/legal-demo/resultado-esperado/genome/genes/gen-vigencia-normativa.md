---
id: gen-vigencia-normativa
trigger: "se ingiere o actualiza una norma o jurisprudencia, o un evento (reforma, sentencia posterior) afecta a una existente"
status: active
version: 1
---

Añade campo 'vigencia: {vigente|en-revision|derogada}' (default 'vigente'). La invalidación es por EVENTO, no por fecha: cuando una página marca 'reemplaza'/'deroga'/'contradice' hacia una norma o precedente por cambio normativo o jurisprudencial, baja la afectada a 'vigencia: en-revision' y, si el cambio está confirmado en vigor, a 'derogada'. QUERY advierte SIEMPRE la vigencia no-vigente con independencia de antigüedad o decay_rate. Nunca borres la versión derogada (queda como rastro histórico).

> Gen de sector sembrado mecánicamente por ONBOARD desde `onboard/company.yaml` (2026-07-12).
> Mutarlo pasa por [[gen-compuerta-mutacion]] como cualquier gen.
