---
run_id: 2026-06-25-9d6819a
role: orquestador
gen_auto_auditoria_version: 2
date: 2026-06-25
confirmados: 8
N: 3
---

# Propuestas — AUDIT 2026-06-25-9d6819a

`N = min(3, confirmados) = min(3, 8) = 3`

Selección: top-3 por impacto. Desempates aplicados según v2 (prioridad de clase, ruta
alfabética). Todas quedan `status: pending`; el humano aprueba/rechaza una por una.

---

## P1 — Deprecar gen-fix-precio-abierto (contradicción entre genes activos)

```yaml
id: P1
fecha: 2026-06-25
score: 52
status: pending
```

**Motivo:** Dos genes activos con trigger idéntico y reglas directamente opuestas generan
comportamiento no-determinista en QUERY: cualquier agente que encuentre un precio puede
tanto citarlo incondicionalmente como abstenerse de hacerlo, según qué gen evalúe primero.
La contradicción es explícita (`gen-fix-precio-vigencia` la declara en su cuerpo).

**Evidencia:**
- `[[gen-fix-precio-abierto]]` — `trigger: la fuente menciona un precio`, `status: active`;
  regla: "cita SIEMPRE tal cual, sin importar su fecha de vigencia"
- `[[gen-fix-precio-vigencia]]` — mismo trigger, `status: active`; regla: "NUNCA se cita
  un precio cuya fecha de vigencia ya pasó. Contradice directamente a [[gen-fix-precio-abierto]]."

**Diff:**
```diff
# genome-applied/gen-fix-precio-abierto.md
  ---
  id: gen-fix-precio-abierto
  trigger: la fuente menciona un precio
- status: active
+ status: deprecated
+ deprecated_by: gen-fix-precio-vigencia
+ deprecated_date: 2026-06-25
+ motivo: "Regla subsumida y contradicha por gen-fix-precio-vigencia (norma vigente)"
  version: 1
  ---
```

> Toca genoma → requiere [[gen-compuerta-mutacion]] (events.jsonl + version bump +
> commit + re-sync AGENTS.md) y posterior [[gen-migracion-genoma]].

---

## P2 — Marcar protocolo-bloqueo-loto como requiere-revalidacion (info vencida en seguridad)

```yaml
id: P2
fecha: 2026-06-25
score: 52
status: pending
```

**Motivo:** El protocolo de seguridad física LOTO lleva 176 días vencido
(`valido_hasta: 2026-01-01`). `prensa-p1` lo cita operativamente como guía de
intervención. Citarlo como vigente es un riesgo de seguridad física real.

**Evidencia:**
- `[[protocolo-bloqueo-loto]]` — `valido_hasta: 2026-01-01` < 2026-06-25; dominio de
  seguridad física confirmado por `tags: [seguridad, protocolo]` y contenido
- `[[prensa-p1]]` — `relations: tratada_segun: ["[[protocolo-bloqueo-loto]]"]` (cita
  operativa de primer nivel)

**Diff:**
```diff
# wiki/semantic/seguridad/protocolo-bloqueo-loto.md
  ---
  title: Protocolo de bloqueo y etiquetado (LOTO)
  ...
  valido_hasta: 2026-01-01
+ estado: requiere-revalidacion
+ advertencia: "Protocolo vencido 2026-01-01; no citar como vigente hasta nueva validación"
  ---

- Procedimiento de bloqueo y etiquetado para intervenir la prensa de forma segura.
- Vencido el 2026-01-01: requiere revalidación antes de citarse como vigente.
+ Procedimiento de bloqueo y etiquetado para intervenir la prensa de forma segura.
+ VENCIDO 2026-01-01 — NO VIGENTE. Revalidar antes de cualquier uso operativo.
```

> Toca wiki → cambio directo + línea en `log.md` + commit.

---

## P3 — Actualizar cliente-acme a estado inactivo (violación de invariante impuesta por gen-entidad-con-estado)

```yaml
id: P3
fecha: 2026-06-25
score: 42
status: pending
```

**Motivo:** `[[cliente-acme]]` mantiene `estado: activo` pese a que `[[caso-acme]]`
registra la baja en mayo 2026. La entidad no fue actualizada in-place tras el evento,
violando [[gen-entidad-con-estado]] (que manda actualizar in-place con evento de respaldo).
La relación `contradice: ["[[cliente-acme]]"]` en `caso-acme` hace el defecto explícito.

**Evidencia:**
- `[[cliente-acme]]` — `estado: activo`; cuerpo: "cliente activo, con contrato vigente"
- `[[caso-acme]]` — `relations: contradice: ["[[cliente-acme]]"]`; cuerpo: "Acme fue dado
  de baja en mayo 2026"

**Diff:**
```diff
# wiki/semantic/clientes/cliente-acme.md
  ---
  title: Cliente Acme
  ...
- estado: activo
+ estado: inactivo
+ fecha_baja: 2026-05-20
+ motivo_baja: "cierre de cuenta registrado en [[caso-acme]]"
  last_reinforced: 2026-06-01
  ...
  ---

- Acme S.A. — cliente **activo**, con contrato vigente.
+ Acme S.A. — cliente **inactivo** desde 2026-05-20 (ver [[caso-acme]]).
```

> Toca wiki → cambio directo + línea en `log.md` + commit.

---

## Tabla de propuestas

| id | clase (canónica v2) | sev | alcance | score | status |
|---|---|---|---|---|---|
| P1 | contradicción entre genes activos | 5 | 2 | **52** | pending |
| P2 | info vencida en dominio de seguridad | 5 | 2 | **52** | pending |
| P3 | violación de invariante impuesta por un gen | 4 | 2 | **42** | pending |

**Candidatos confirmados excluidos del top-3** (quedan en backlog, no generan propuesta
en esta corrida):

| id | clase | score | razón de exclusión |
|---|---|---|---|
| C4 | regla obsoleta/deprecable (gen del genoma) | 32 | impacto < top-3 |
| C8 | redundancia (duplicado) — confidencial | 22 | impacto < top-3 |
| C7 | redundancia (duplicado) | 22 | impacto < top-3 |
| C6 | vacío (categoría sin cobertura) | 21 | impacto < top-3 |
| C5 | vacío (link roto) | 21 | impacto < top-3 |

---

## Nota de confidencialidad

Ninguno de los candidatos C8 (expedientes confidenciales) alcanzó el top-3 por impacto.
Las propuestas P1–P3 no involucran páginas con `sensibilidad: confidencial`.
En este artefacto no se transcribe ningún valor sensible de los expedientes auditados.
