---
id: gen-ciclo-de-vida
trigger: reforzar, degradar, promover o archivar páginas de wiki/ (CONSOLIDATE, LINT, QUERY, INGEST)
status: active
version: 4
---

La memoria por capas deja de ser metáfora: estos son los **números** del ciclo de vida.
Son defaults del genoma base, sobreescribibles por empresa en el bloque `ciclo_de_vida` de
`onboard/company.yaml` (esquema en `company.example.yaml`). Valores **razonados, no
calibrados**: el piloto Fase 0 los medirá y este gen se re-versionará con evidencia.

**Ventanas de decaimiento** (`decay_ventana_dias`). `decay_rate` significa "días sin
refuerzo antes de empezar a decaer": `high` = 14 · `medium` = 60 · `low` = 180. Default al
crear o mover una página, si no lo declara: `working/` y `episodic/` = high, `semantic/` =
medium, `procedural/` = low; `clase: evento` siempre high ([[gen-clase-temporal]]) y
`type: sintesis` low ([[gen-sintesis-de-volumen]]). El `decay_rate` declarado en la página
gana sobre el default del tier.

**Refuerzo** — qué cuenta y su efecto: (1) una fuente nueva que confirma el contenido
(INGEST / BULK INGEST) pone `last_reinforced: hoy`, se añade a `sources` y sube
`confidence` según su tipo (`refuerzo_delta`): oficial +0.10, interna +0.05, blanda +0.03 y
solo si concuerda — un tipo declarado solo en `source_trust` (p. ej. `doctrina`) usa el
delta del tipo estándar de trust inmediatamente inferior (conservador), salvo que el
manifiesto declare el suyo en `ciclo_de_vida.refuerzo_delta`—; (2) citar la página para sostener una respuesta de QUERY refresca
`last_reinforced` (el uso reinicia el reloj) pero **no** sube `confidence` (uso no es
verificación); (3) agregar eventos nuevos a una página `type: sintesis` refuerza la
síntesis. Techo del refuerzo automático: `confidence` nunca supera
`min(max(source_trust de sus fuentes) + 0.10, 0.95)` — con los `source_trust` del
manifiesto de ejemplo, una página solo-blanda topa en 0.5: lo blando corrobora, no
sustituye ([[gen-confianza-por-fuente]]). Las `clase: evento` no se refuerzan, nunca.

**Degradación** (la aplica CONSOLIDATE; LINT la detecta como "vencido blando"): por cada
ventana completa transcurrida sin refuerzo, `confidence -= 0.05` (`decaimiento_delta`). Al
aplicarla se anota `decay_aplicado: YYYY-MM-DD` y las ventanas siguientes se cuentan desde
`max(last_reinforced, decay_aplicado)`: re-correr CONSOLIDATE no descuenta dos veces
(idempotencia). Excepción: en `clase: evento` la degradación **no toca** `confidence` (que
algo ocurrió no se vuelve falso); su ciclo es el archivo por antigüedad. La vigencia dura
([[gen-vigencia-temporal]]) es ortogonal: ni el refuerzo ni el uso "des-vencen" un
`valido_hasta` pasado ni una `vigencia` no-vigente.

**Promoción `working → semantic`** (CONSOLIDATE la aplica directo y la reporta) cuando se
cumplen TODAS: `clase: estable` · `confidence ≥ 0.70` · ≥2 fuentes en `sources` **o** ≥2
páginas distintas que la referencian · edad ≥7 días desde `created` **y** ≥1 refuerzo
posterior (`last_reinforced > created`, proxy verificable de "confirmada en más de una
sesión") · sin `riesgo_inyeccion: true` ([[gen-anti-inyeccion]]: la cuarentena bloquea
promoción y fusión hasta revisión humana) · sin `contradice` abierta ·
`sensibilidad ≠ confidencial` ([[gen-confidencialidad]] prohíbe promoverlas).
Procesos repetidos promueven a
`procedural/` con las mismas condiciones. Al promover: mover el archivo a la carpeta de
taxonomía que corresponda (los `[[wiki-links]]` van por nombre y no se rompen), ajustar
`decay_rate` al default del tier destino salvo declaración explícita, y dejar línea en
`log.md`.

**Suelo y archivo** (CONSOLIDATE lo **propone**, aplica solo tras OK): página
`clase: estable` con `confidence ≤ 0.30` (`piso_archivo`) y sin refuerzo → mover a
`wiki/archive/` añadiendo `archivado: YYYY-MM-DD` (frontmatter intacto salvo la
actualización `id_pagina`/`id_alias` de [[gen-identidad-de-pagina]], `raw/` jamás se
toca, el ancla en `index.md` se retira). `clase: evento` con `fecha_evento` a más de 180
días (`archivo_eventos_dias`) → candidata a archivo, de bajo riesgo si ya está agregada en
una síntesis; los resúmenes de `episodic/` siguen esta misma regla de eventos. **Nunca** se
archiva una página con `estado` operativo abierto ([[gen-entidad-con-estado]], accionables
de sector). Lo archivado no se cita en QUERY salvo pedido explícito de histórico.
