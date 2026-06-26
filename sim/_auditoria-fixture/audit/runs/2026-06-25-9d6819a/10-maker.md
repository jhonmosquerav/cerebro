---
run_id: 2026-06-25-9d6819a
role: maker
gen_auto_auditoria_version: 2
date: 2026-06-25
candidatos: 8
---

# Maker — AUDIT 2026-06-25-9d6819a

Metodología: esqueleto (frontmatter + relaciones de las 8 páginas y 4 genes) → drill-down
sobre los objetos marcados por los detectores (LINT + CONSOLIDATE + redundancia/obsolescencia
de genoma). Cada defecto produce UN candidato; fusiones explicitadas donde aplican.
`impacto = severidad×10 + alcance`. Alcance contado según la regla explícita de la clase (v2).

---

## C1 — Contradicción entre genes activos

| Campo | Valor |
|---|---|
| Clase | contradicción entre genes activos |
| Severidad | 5 |
| Alcance | 2 (ambos genes en conflicto) |
| Impacto | **52** |

**Objetos afectados:**
- `genome-applied/gen-fix-precio-abierto.md` (status: active)
- `genome-applied/gen-fix-precio-vigencia.md` (status: active)

**Evidencia:**
Los dos genes comparten el mismo `trigger`: *"la fuente menciona un precio"* y ambos tienen
`status: active`. Sus reglas son directamente opuestas:
- `gen-fix-precio-abierto`: *"cita SIEMPRE tal cual, sin importar su fecha de vigencia"*
- `gen-fix-precio-vigencia`: *"NUNCA se cita un precio cuya fecha de vigencia ya pasó"*

El propio `gen-fix-precio-vigencia` declara en su cuerpo: *"Contradice directamente a
[[gen-fix-precio-abierto]]"*. Ambos activos con trigger idéntico → detector de
redundancia/obsolescencia de genoma los captura; también cumple la clase "contradicción entre
genes activos".

**Diff propuesto:**
```diff
- genome-applied/gen-fix-precio-abierto.md: status: active
+ genome-applied/gen-fix-precio-abierto.md: status: deprecated
+ # deprecated_by: gen-fix-precio-vigencia
+ # motivo: regla subsumida y contradicha; gen-fix-precio-vigencia es la norma vigente
```

---

## C2 — Info vencida en dominio de seguridad

| Campo | Valor |
|---|---|
| Clase | info vencida en dominio de seguridad |
| Severidad | 5 |
| Alcance | 2 (página vencida + 1 página que la cita operativamente) |
| Impacto | **52** |

**Objetos afectados:**
- `wiki/semantic/seguridad/protocolo-bloqueo-loto.md` — vencido (`valido_hasta: 2026-01-01`; hoy 2026-06-25)
- `wiki/semantic/maquinas/prensa-p1.md` — la cita vía relación tipada `tratada_segun: ["[[protocolo-bloqueo-loto]]"]`

**Evidencia:**
`valido_hasta: 2026-01-01 < 2026-06-25` → caducado hace 176 días. El campo `tags: [seguridad,
protocolo]` y el contenido ("intervenir la prensa de forma segura") encuadran esto en dominio
de **seguridad física** → califica la clase sev-5. `prensa-p1` lo cita operativamente (relación
tipada `tratada_segun` de primer nivel), por lo que suma al alcance.

**Diff propuesto:**
```diff
# wiki/semantic/seguridad/protocolo-bloqueo-loto.md
- valido_hasta: 2026-01-01
+ valido_hasta: 2026-01-01   # VENCIDO — revalidar antes de usar
+ estado: requiere-revalidacion
+ advertencia: "Protocolo vencido 2026-01-01; no citar como vigente hasta nueva validación"
```

---

## C3 — Contradicción entre páginas wiki

| Campo | Valor |
|---|---|
| Clase | contradicción entre páginas wiki |
| Severidad | 4 |
| Alcance | 2 (ambas páginas en conflicto) |
| Impacto | **42** |

**Objetos afectados:**
- `wiki/semantic/clientes/cliente-acme.md` — `estado: activo`, prosa: *"cliente activo, con contrato vigente"*
- `wiki/semantic/casos/caso-acme.md` — registra la baja en mayo 2026; declara `contradice: ["[[cliente-acme]]"]`

**Evidencia:**
`caso-acme` tiene la relación explícita `contradice: ["[[cliente-acme]]"]` → el detector de
contradicciones la captura directamente. `cliente-acme` mantiene `estado: activo` pese al
evento de baja. La entidad `cliente-acme` no fue actualizada in-place tras el evento (violación
de [[gen-entidad-con-estado]]). El defecto es una contradicción entre páginas wiki (sev 4);
si se quisiera elevar a "entidad con estado inconsistente" (sev 4 también) se fusionan en un
único candidato — clase elegida la de mayor o igual severidad. Se elige la clase de sev 4
"contradicción entre páginas wiki" por ser la detectada por el detector explícito (`contradice`).

**Diff propuesto:**
```diff
# wiki/semantic/clientes/cliente-acme.md
- estado: activo
+ estado: inactivo
+ fecha_baja: 2026-05-20
+ motivo_baja: "cierre de cuenta registrado en [[caso-acme]]"
```

---

## C4 — Regla obsoleta/deprecable (gen del genoma)

| Campo | Valor |
|---|---|
| Clase | regla obsoleta/deprecable (gen del genoma) |
| Severidad | 3 |
| Alcance | 2 (ambos genes del solape) |
| Impacto | **32** |

**Objetos afectados:**
- `genome-applied/gen-fix-clasifica-v1.md` (status: active) — trigger: *"la fuente es una ficha de producto"*
- `genome-applied/gen-fix-clasifica-v2.md` (status: active) — mismo trigger; regla superset

**Evidencia:**
Ambos genes tienen `status: active` y trigger idéntico. El cuerpo de `gen-fix-clasifica-v2`
declara explícitamente: *"Cubre por completo el caso de [[gen-fix-clasifica-v1]], que queda
obsoleto (mismo trigger, regla subsumida)"*. El detector de redundancia/obsolescencia de
genoma los captura: trigger solapado + regla de v1 subsumida por v2. Diferencia con C1: aquí
no hay contradicción lógica sino subsunción (v2 amplía v1), por lo que la clase aplicable es
"regla obsoleta/deprecable" (sev 3), no "contradicción entre genes activos" (sev 5).

**Diff propuesto:**
```diff
# genome-applied/gen-fix-clasifica-v1.md
- status: active
+ status: deprecated
+ deprecated_by: gen-fix-clasifica-v2
+ motivo: "Regla completamente subsumida por gen-fix-clasifica-v2 (mismo trigger, superset de requisitos)"
```

---

## C5 — Vacío (link roto)

| Campo | Valor |
|---|---|
| Clase | vacío (link roto / categoría sin cobertura) |
| Severidad | 2 |
| Alcance | 1 (página afectada) |
| Impacto | **21** |

**Objeto afectado:**
- `wiki/semantic/maquinas/prensa-p1.md`

**Evidencia:**
`prensa-p1` contiene en sus relaciones `usa: ["[[manual-inexistente]]"]` y en el cuerpo
*"Para el detalle de operación, ver [[manual-inexistente]]"*. No existe ningún archivo
`manual-inexistente.md` bajo `wiki/` → link roto (vacío por link roto).

**Diff propuesto:**
```diff
# wiki/semantic/maquinas/prensa-p1.md
  relations:
-   usa: ["[[manual-inexistente]]"]
+   usa: []
+   # TODO: localizar o crear el manual de operación de Prensa P-1
```

---

## C6 — Vacío (categoría sin cobertura)

| Campo | Valor |
|---|---|
| Clase | vacío (link roto / categoría sin cobertura) |
| Severidad | 2 |
| Alcance | 1 (categoría afectada) |
| Impacto | **21** |

**Objeto afectado:**
- `company.yaml` → `taxonomy.semantic: [..., proveedores]`

**Evidencia:**
La taxonomía en `company.yaml` declara la categoría `proveedores` bajo `semantic`. No existe
ninguna página bajo `wiki/semantic/proveedores/` ni ningún archivo indexado para esa categoría.
El detector de vacíos (LINT) la marca como categoría declarada sin cobertura.

**Diff propuesto:**
```diff
# Opción A — crear página stub:
+ wiki/semantic/proveedores/proveedores-index.md  (stub con frontmatter mínimo)

# Opción B — retirar la categoría si no hay proveedores a documentar:
# company.yaml → taxonomy.semantic: eliminar "proveedores"
```

---

## C7 — Redundancia (duplicado)

| Campo | Valor |
|---|---|
| Clase | redundancia (duplicado) |
| Severidad | 2 |
| Alcance | 2 (ambas páginas duplicadas) |
| Impacto | **22** |

**Objetos afectados:**
- `wiki/semantic/productos/widget-a.md`
- `wiki/semantic/productos/widget-a-detalle.md`

**Evidencia:**
Ambas páginas describen la misma entidad: SKU WID-A, material acero, proveedor Norte.
`widget-a-detalle` declara en su cuerpo *"Duplica a [[widget-a]]"* pero NO declara relaciones
de exención (`deriva_de`, `supersede`, `agregado_en`) → el par NO queda exento de redundancia
por la regla de [[gen-consolidate]] v2. El detector de near-duplicados las captura.

**Diff propuesto:**
```diff
# Opción canónica: fusionar en widget-a.md y eliminar widget-a-detalle.md
# widget-a.md — agregar los campos de detalle que no estén ya presentes
- wiki/semantic/productos/widget-a-detalle.md  (eliminar o marcar supersedida)
+ widget-a-detalle.md: agregar relacion  supersede: [] o  agregado_en: [[widget-a]]
+                      y bajar tier a working o marcar deprecated
```

---

## C8 — Redundancia confidencial (duplicado)

| Campo | Valor |
|---|---|
| Clase | redundancia (duplicado) |
| Severidad | 2 |
| Alcance | 2 (ambas páginas confidenciales — contadas, no transcritas) |
| Impacto | **22** |

**Objetos afectados (por link únicamente — sensibilidad: confidencial):**
- `[[expediente-x]]` — campo `sensibilidad: confidencial`
- `[[expediente-x-copia]]` — campo `sensibilidad: confidencial`

**Evidencia (sin transcribir valores sensibles):**
El campo `title` de `[[expediente-x-copia]]` indica que se trata de una copia de
`[[expediente-x]]`. Ninguno de los dos declara relaciones de exención (`deriva_de`,
`supersede`, `agregado_en`) → el par NO queda exento. Ambas páginas tienen `sensibilidad:
confidencial`; cuentan en el alcance pero su contenido NO se transcribe en este artefacto.
La eliminación o fusión de duplicados confidenciales requiere autorización del `mutation_approver`.

**Diff propuesto:**
```diff
# [[expediente-x-copia]] — agregar relación de exención para documentar la intención
# o proceder a eliminar/fusionar con gate del mutation_approver:
+ supersede: ["[[expediente-x]]"]   # si copia es la versión más reciente
# ó
# eliminar [[expediente-x-copia]] si [[expediente-x]] es el original canónico
```

---

## Tabla resumen — ordenada por impacto desc (desempate: clase, luego ruta)

| id | clase | sev | alcance | impacto |
|---|---|---|---|---|
| C1 | contradicción entre genes activos | 5 | 2 | **52** |
| C2 | info vencida en dominio de seguridad | 5 | 2 | **52** |
| C3 | contradicción entre páginas wiki | 4 | 2 | **42** |
| C4 | regla obsoleta/deprecable (gen del genoma) | 3 | 2 | **32** |
| C8 | redundancia (duplicado) — confidencial | 2 | 2 | **22** |
| C7 | redundancia (duplicado) | 2 | 2 | **22** |
| C6 | vacío (categoría sin cobertura) | 2 | 1 | **21** |
| C5 | vacío (link roto) | 2 | 1 | **21** |

**Desempates aplicados:**
- C1 vs C2 (impacto=52): misma clase-fila? No — C1="contradicción entre genes activos" fila 1;
  C2="info vencida en dominio de seguridad" fila 2 → C1 > C2 por prioridad de clase.
- C8 vs C7 (impacto=22, misma clase "redundancia"): ruta alfabética →
  `confidencial/expediente-x` < `productos/widget-a` → C8 antes de C7.
- C6 vs C5 (impacto=21, misma clase "vacío"): ruta del objeto afectado →
  `company.yaml` < `wiki/semantic/maquinas/prensa-p1.md` → C6 antes de C5.

**Total candidatos:** 8

**Nota de confidencialidad:** los candidatos C8 cita los objetos afectados exclusivamente por
`[[link]]` y nombre de campo. Ningún valor sensible (nombre, DNI, diagnóstico, etc.) fue
transcrito en este artefacto. Confirmed: oracle files (`expected.md`, `regresion.md`,
`audit/runs/2026-06-25-dc198a0/`) NO fueron leídos.
