---
run_id: 2026-06-25-f5c6000
scenario: produccion
fecha: 2026-06-25
gen_auditoria_version: 1
N: 3
confirmadas_por_auditor: 4
top_N: 3
status_global: approved
---

# 30 — Propuestas (top-3, status: pending)

N = min(3, 4 candidatos confirmados) = **3**
Ranking por impacto auditado: C1 (44) > C2 (31) > C3 (24)

---

## P1 — Actualizar checklist operativo de SOP-MTTO-01

**id:** P1
**fecha:** 2026-06-25
**candidato_origen:** C1
**clase:** contradicción entre páginas wiki
**severidad:** 4
**alcance:** 4
**score (impacto):** 44

**Motivo:**
El [[SOP-MTTO-01-preventivo-prensas]] declara en su sección "Brecha detectada" que el
checklist de mantenimiento preventivo NO incluye la verificación del tope de altura del
troquel, causa raíz documentada de [[NCR-2026-031]]. Sin embargo, el cuerpo operativo del
SOP (la lista de pasos que el técnico ejecuta) aún tiene solo 3 ítems y omite ese punto.
Cualquier técnico que siga el checklist vigente reproduce la causa raíz de la NCR. La
contradicción es interna a la misma página: body vs. sección Brecha.

**Evidencia:**
- [[SOP-MTTO-01-preventivo-prensas]] — sección "Checklist actual" (3 ítems) vs. sección
  "Brecha detectada" (exige ítem 4)
- [[MTTO-PR-200-2026-06]] — raw confirma recomendación de añadir ítem
- [[NCR-2026-031]] — evidencia de la NCR de severidad `mayor` producida por la omisión
- [[PR-200-prensa]] — `proximo_preventivo: 2026-07-19`: el defecto se re-ejecutaría en 24 días

**Diff:**
```diff
--- wiki/procedural/sops-mantenimiento/SOP-MTTO-01-preventivo-prensas.md (vigente)
+++ wiki/procedural/sops-mantenimiento/SOP-MTTO-01-preventivo-prensas.md (propuesto)
@@ Checklist actual @@
 1. Engrase de guías.
 2. Revisión de presión hidráulica (rango OK: 200–215 bar).
 3. Inspección visual de troquel.
+4. Verificar y registrar cota del tope de altura del troquel con galga patrón;
+   anotar valor medido (nominal: 45,0 mm ± 0,1 mm) en hoja de MTTO.
+
+# Borrar sección "Brecha detectada" una vez incorporado el ítem 4 al checklist operativo.
+# Actualizar: last_reinforced, sources (añadir ref. al raw de MTTO si no está ya).
```

**Nota de aprobación:** este cambio toca una página `type: sop` de `tier: procedural`
(no genoma). Se aplica como cambio directo en wiki + línea en `log.md` + commit.
No requiere [[gen-compuerta-mutacion]].

**status:** approved

---

## P2 — Declarar `relation_types` en company.yaml con los 17 verbos de dominio

**id:** P2
**fecha:** 2026-06-25
**candidato_origen:** C2
**clase:** vacío (categoría sin cobertura)
**severidad:** 2
**alcance:** 11
**score (impacto):** 31

**Motivo:**
El manifiesto ONBOARD `sim/produccion/company.yaml` no declara el bloque `relation_types`.
Las páginas wiki usan 17 verbos de relación fuera del núcleo `{usa, depende_de, contradice,
reemplaza}`. Sin esa declaración, un LINT contra el genoma nuevo
([[gen-frontmatter-obligatorio]] v3) marcaría todas las relaciones de trazabilidad como
"verbos huérfanos semánticos", degradando la auditabilidad del grafo completo. La capacidad
de extensión existe en el gen; falta el dato de onboard.

**Evidencia:**
- `sim/produccion/company.yaml` — ausencia del bloque `relation_types`
- [[LOTE-SM45-2606]], [[OP-2026-0417]], [[NCR-2026-031]], [[MTTO-PR-200-2026-06]],
  [[PR-200-prensa]], [[soporte-motor-SM45]], [[L1-estampado]], [[AceroNorte]],
  [[SOP-CAL-03-inspeccion-dimensional]], [[SOP-MTTO-01-preventivo-prensas]] — las 10 páginas
  wiki que usan verbos de dominio no declarados
- `sim/produccion/regresion.md` — confirma explícitamente la deuda (sección F1)

**Diff:**
```diff
--- sim/produccion/company.yaml (vigente)
+++ sim/produccion/company.yaml (propuesto)
@@ después de taxonomy: @@
+
+# Verbos de dominio permitidos fuera del núcleo {usa, depende_de, contradice, reemplaza}.
+# Declarados según gen-frontmatter-obligatorio v3; LINT valida contra núcleo ∪ estos.
+relation_types:
+  producido_en:    "lote producido en máquina"
+  bajo_orden:      "lote o NCR bajo orden de producción"
+  de_producto:     "lote/OP de producto (SKU)"
+  insumo_de:       "lote/OP usa insumo de proveedor"
+  afectado_por:    "lote afectado por evento de calidad"
+  afecta_a:        "NCR afecta a lote"
+  viola:           "NCR viola SOP de calidad"
+  causa_en:        "NCR tiene causa en máquina"
+  mitiga_con:      "NCR mitigada con intervención de mantenimiento"
+  ubicada_en:      "máquina ubicada en línea"
+  produjo_lote:    "máquina produjo lote"
+  intervenida_por: "máquina intervenida por evento de mantenimiento"
+  mantiene_a:      "evento de mantenimiento mantiene a máquina"
+  resuelve:        "evento de mantenimiento resuelve NCR"
+  genero_lote:     "OP generó lote"
+  aplica_a:        "SOP aplica a máquina o entidad"
+  reforzado_por:   "SOP reforzado por evento que lo confirma o detecta brecha"
```

**Nota de aprobación:** cambio en manifiesto ONBOARD (`company.yaml`). Toca la configuración
del sandbox pero no el genoma base. Se aplica directo + commit. Si la empresa usa el
genoma nuevo con [[gen-frontmatter-obligatorio]] v3, pasar también por
[[gen-migracion-genoma]] para re-validar páginas.

**status:** approved

---

## P3 — Añadir campo `clase:` explícito en frontmatter de páginas de evento

**id:** P3
**fecha:** 2026-06-25
**candidato_origen:** C3
**clase:** vacío (campo obligatorio ausente)
**severidad:** 2
**alcance:** 4
**score (impacto):** 24

**Motivo:**
[[gen-clase-temporal]] (activo en el genoma nuevo, verificado en regresion.md F2) exige que
toda página de `wiki/` declare `clase: estable | evento`. Las cuatro páginas afectadas tienen
`decay_rate` y `fecha_evento` correctos, pero el campo literal `clase:` no aparece en ningún
frontmatter. Sin él, LINT debe inferir la clase a partir de tags o decay_rate (campos menos
formales), lo que introduce ambigüedad y dependencia de heurísticas de fallback.

**Evidencia:**
- [[NCR-2026-031]] — `decay_rate: high`, `fecha_evento` presente, pero sin `clase:`
- [[MTTO-PR-200-2026-06]] — `decay_rate: high`, `fecha_evento` presente, pero sin `clase:`
- [[OP-2026-0417]] — `decay_rate: medium`, `fecha_evento` presente, pero sin `clase:`
- [[LOTE-SM45-2606]] — `decay_rate: low`, sin `clase:` (debería ser `clase: estable`)
- `sim/produccion/regresion.md` — "Mejora menor: añadir el campo explícito `clase:` al
  frontmatter de NCR y MTTO para que LINT lo lea sin inferir."

**Diff:**
```diff
--- wiki/semantic/calidad/NCR-2026-031.md (frontmatter, vigente)
+++ wiki/semantic/calidad/NCR-2026-031.md (propuesto)
@@ frontmatter @@
 decay_rate: high
+clase: evento

--- wiki/semantic/maquinas/MTTO-PR-200-2026-06.md (frontmatter, vigente)
+++ wiki/semantic/maquinas/MTTO-PR-200-2026-06.md (propuesto)
@@ frontmatter @@
 decay_rate: high
+clase: evento

--- wiki/semantic/lotes/OP-2026-0417.md (frontmatter, vigente)
+++ wiki/semantic/lotes/OP-2026-0417.md (propuesto)
@@ frontmatter @@
 decay_rate: medium
+clase: evento

--- wiki/semantic/lotes/LOTE-SM45-2606.md (frontmatter, vigente)
+++ wiki/semantic/lotes/LOTE-SM45-2606.md (propuesto)
@@ frontmatter @@
 decay_rate: low
+clase: estable
```

**Nota de aprobación:** cambios en frontmatter de 4 páginas wiki. Se aplican directo +
línea en `log.md` + commit. No requieren [[gen-compuerta-mutacion]].

**status:** approved

---

## Reserva (no incluida en top-3)

| id | candidato | score | motivo de exclusión del top-3 |
|---|---|---|---|
| P4 | C4 — MTTO verbo `usa` semántica incorrecta | 22 | menor impacto; parcialmente bloqueado por P2 (requiere `relation_types` declarados antes de renombrar el verbo) |

---

## Checklist de completitud del run

- [x] `00-snapshot.md` — presente
- [x] `10-maker.md` — presente
- [x] `20-auditor.md` — presente
- [x] `30-proposals.md` — este documento
- [ ] Línea en `log.md` — pendiente (requiere gate humano)
- [ ] Commit — pendiente (requiere aprobación de al menos una propuesta)
