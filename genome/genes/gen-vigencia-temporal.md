---
id: gen-vigencia-temporal
trigger: páginas con caducidad (precios, protocolos, normas, stock, ofertas, certificaciones)
status: active
version: 1
---

Vigencia **dura**, distinta del decaimiento blando de `confidence`. Una página cuyo
contenido caduca en una fecha concreta lleva `valido_hasta: YYYY-MM-DD` en el frontmatter.
QUERY, LINT y CONSOLIDATE comparan `valido_hasta` contra la fecha de hoy: si ya pasó, la
información se marca vencida y **QUERY la advierte SIEMPRE** antes de citarla, con
independencia de `confidence` o `decay_rate`. En dominios de seguridad (salud, legal), una
página vencida sin `reemplaza` se eleva como hallazgo **prioritario** de LINT. Una versión
nueva `reemplaza` a la vencida; el histórico no se borra. Complementa [[gen-frontmatter-obligatorio]].
