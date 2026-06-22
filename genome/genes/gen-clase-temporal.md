---
id: gen-clase-temporal
trigger: crear una página de wiki/ (distinguir conocimiento estable de evento fechado)
status: active
version: 1
---

Toda página declara `clase: estable | evento` (default `estable`). Las `evento` (una NCR, un
ticket, una orden, un incidente, una call) exigen `fecha_evento: YYYY-MM-DD`, nacen con
`decay_rate: high` y **no se refuerzan por reingesta**: cada evento es un registro distinto,
no se fusiona ni sube su `confidence` al re-verlo. Las `estable` (ficha de producto, concepto,
SOP) son conocimiento durable. Una página `estable` puede declarar
`volatile_fields: [{campo, valido_a}]` para campos que envejecen más rápido que la página
(precio, stock), reusando la semántica de [[gen-vigencia-temporal]] a nivel de campo.
CONSOLIDATE y LINT actúan según `clase`: los eventos no se promueven como conocimiento durable
(pero sí se agregan, ver [[gen-sintesis-de-volumen]]). Es base de [[gen-entidad-con-estado]].
