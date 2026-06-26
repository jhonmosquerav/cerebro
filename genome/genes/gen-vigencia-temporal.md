---
id: gen-vigencia-temporal
trigger: páginas con caducidad (precios, protocolos, normas, stock, ofertas, certificaciones)
status: active
version: 2
---

Vigencia **dura**, distinta del decaimiento blando de `confidence`. Una página cuyo
contenido caduca en una fecha concreta lleva `valido_hasta: YYYY-MM-DD` en el frontmatter.
QUERY, LINT y CONSOLIDATE comparan `valido_hasta` contra la fecha de hoy: si ya pasó, la
información se marca vencida y **QUERY la advierte SIEMPRE** antes de citarla, con
independencia de `confidence` o `decay_rate`. En dominios de seguridad (salud, legal), una
página vencida sin `reemplaza` se eleva como hallazgo **prioritario** de LINT. Una versión
nueva `reemplaza` a la vencida; el histórico no se borra.

La vigencia también puede ser **por evento**, no solo por fecha: una página con
`vigencia: derogada | no-vigente | en-revision` se trata como vencida **dura** (la elevan QUERY,
LINT y AUDIT) aunque su `valido_hasta` no haya pasado o no exista. Útil donde la caducidad la
dispara un evento externo (una sentencia, una reforma normativa, una retractación), no el
calendario. Complementa [[gen-frontmatter-obligatorio]].
