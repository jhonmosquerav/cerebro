---
run_id: 2026-06-25-f5c6000
scenario: salud
role: orquestador
date: 2026-06-25
gen_version: gen-auto-auditoria v1
proposals: 3
status_global: approved
---

# 30-proposals — Propuestas de mejora (Clínica Vida Serena)

> N = min(3, confirmadas por auditor) = 3.
> Todas con `status: pending`. Requieren aprobación del `mutation_approver: director-medico`
> antes de aplicar. Ninguna se aplica sola.

---

## P1 — Protocolo clínico vencido sin reemplazo: hoja de ruta de cierre

| campo | valor |
|---|---|
| **id** | P1 |
| **fecha** | 2026-06-25 |
| **origen** | CAND-01 |
| **clase** | info vencida en dominio de seguridad |
| **score** | 55 |
| **status** | approved |

### Motivo

[[protocolo-anafilaxia]] tiene `valid_until: 2026-03-01` (vencido hace 116 días a fecha
2026-06-25), `status: vencido`, `reemplaza: []` (sin v4 publicada) y `confidence: 0.55`.
`gen-vigencia-protocolo` establece que un protocolo vencido sin reemplazo es "hallazgo de
seguridad prioritario". Cinco páginas del grafo referencian este protocolo como si fuera
la fuente de verdad, de las cuales [[adrenalina]] no contiene ninguna advertencia de
caducidad (`confidence: 0.92` sin degradar). Existe un incidente abierto [[INC-2026-014]]
vinculado al mismo defecto, con acciones correctivas sin responsable asignado ni fecha
de cierre.

### Evidencia

- [[protocolo-anafilaxia]] — `valid_until: 2026-03-01`, `status: vencido`, `reemplaza: []`
- [[anafilaxia]] — `tratada_segun` apunta a protocolo vencido; advertencia parcial inline
- [[adrenalina]] — `indicado_por` apunta a protocolo vencido; **sin ninguna advertencia**
- [[PAC-7731]] — `segun_protocolo` apunta a protocolo vencido (id+campo únicamente; `confidential: true`)
- [[INC-2026-014]] — `afecta_a` protocolo vencido; `estado: abierto`; acciones sin responsable ni fecha

### Diff

```diff
# --- ACCIÓN 1: publicar protocolo-anafilaxia-v4.md (nueva página) ---
+ wiki/procedural/protocolos-clinicos/protocolo-anafilaxia-v4.md
+   valid_until: 2028-03-01          # revisión bienal
+   status: vigente
+   version_doc: 4
+   reemplaza: ["[[protocolo-anafilaxia]]"]
+   confidence: 0.9
+   decay_rate: high

# --- ACCIÓN 2: deprecar v3 tras publicar v4 ---
# wiki/procedural/protocolos-clinicos/protocolo-anafilaxia.md
- status: vencido
+ status: deprecado
+ reemplazado_por: ["[[protocolo-anafilaxia-v4]]"]

# --- ACCIÓN 3: añadir advertencia de caducidad en adrenalina.md ---
# wiki/semantic/farmacos/adrenalina.md — cuerpo
+ > ⚠️ Nota: `indicado_por` apunta a [[protocolo-anafilaxia]] v3 (status: vencido
+ > al 2026-03-01). Confirmar dosis con [[protocolo-anafilaxia-v4]] cuando se publique.

# --- ACCIÓN 4: cerrar acciones correctivas de INC-2026-014 ---
# wiki/semantic/incidentes/INC-2026-014.md — cuerpo (acciones 2 y 3)
+ accion_2_responsable: "director-medico"
+ accion_2_fecha_limite: "2026-07-31"
+ accion_3_responsable: "calidad-seguridad"
+ accion_3_fecha_limite: "2026-08-31"
```

> Nota: las acciones 4 son extensión del cuerpo de [[INC-2026-014]], no campos de
> frontmatter del schema actual. Requieren ajuste de schema o registro en cuerpo como
> tabla. El `mutation_approver` decide el formato al aprobar.
> La ACCIÓN 1 (creación de v4) es prerequisito de las demás; sin v4, las acciones 2 y 3
> no se aplican. El orquestador debe aplicar en secuencia.

---

## P2 — Eliminar relación `tratamiento_de` invertida en anafilaxia.md

| campo | valor |
|---|---|
| **id** | P2 |
| **fecha** | 2026-06-25 |
| **origen** | CAND-02 |
| **clase** | contradicción entre páginas wiki |
| **score** | 42 |
| **status** | approved |

### Motivo

[[anafilaxia]] contiene `relations.tratamiento_de: ["[[adrenalina]]"]` en su frontmatter.
`gen-trazabilidad-clinica` define el schema canónico: el verbo `tratamiento_de` pertenece
al **fármaco** (apunta a la patología), no a la patología (que usa `tratada_segun` para
apuntar al protocolo). La presencia de `tratamiento_de` en la patología crea una relación
semántica invertida: el mismo verbo aparece en ambas direcciones del grafo entre el mismo
par de nodos, haciendo ambigua cualquier query que filtre por `tratamiento_de` sin
diferenciar tipo de nodo.

### Evidencia

- [[anafilaxia]] — `relations.tratamiento_de: ["[[adrenalina]]"]` (campo no canónico para patología)
- [[adrenalina]] — `relations.tratamiento_de: ["[[anafilaxia]]"]` (canónico — fármaco apunta a patología)
- [[gen-trazabilidad-clinica]] — schema canónico: patología usa `tratada_segun`, no `tratamiento_de`

### Diff

```diff
# wiki/semantic/patologias/anafilaxia.md — frontmatter relations
  relations:
    usa: []
    depende_de: []
    tratada_segun: ["[[protocolo-anafilaxia]]"]
-   tratamiento_de: ["[[adrenalina]]"]
    contradice: []
    reemplaza: []
```

> Cambio mínimo e idempotente. No afecta relaciones en [[adrenalina]].
> El conocimiento "adrenalina trata anafilaxia" sigue navegable desde
> [[adrenalina]].`tratamiento_de` → [[anafilaxia]], que es el sentido canónico.

---

## P3 — Crear páginas wiki para las 7 entidades del manifiesto sin cobertura

| campo | valor |
|---|---|
| **id** | P3 |
| **fecha** | 2026-06-25 |
| **origen** | CAND-03 |
| **clase** | vacío (link roto / categoría sin cobertura) |
| **score** | 27 |
| **status** | approved |

### Motivo

`company.yaml` declara 7 entidades que no tienen página en `sim/salud/wiki/`: dos
protocolos (`sepsis-adulto`, `dolor-toracico`), dos patologías (`sepsis`,
`neumonia-adquirida-comunidad`), dos fármacos (`amoxicilina-clavulanico`, `noradrenalina`)
y un profesional (`dr-nunez-mi`). La ausencia viola `gen-trazabilidad-clinica` (que
requiere que toda ficha de fármaco enlace patología o protocolo — imposible de verificar
sin la ficha). [[INC-2026-014]] acción 4 menciona explícitamente que los protocolos de
dolor torácico y sepsis requieren auditoría de vigencia, que tampoco es posible sin sus
páginas.

### Evidencia

- `company.yaml` — `entities.protocolos: ["sepsis-adulto", "dolor-toracico", "anafilaxia"]`; solo `anafilaxia` tiene página
- `company.yaml` — `entities.farmacos: ["adrenalina", "amoxicilina-clavulanico", "noradrenalina"]`; solo `adrenalina` tiene página
- `company.yaml` — `entities.patologias: ["sepsis", "anafilaxia", "neumonia-adquirida-comunidad"]`; solo `anafilaxia` tiene página
- `company.yaml` — `entities.profesionales: ["dr-nunez-mi", "dra-soto-urg", "enf-rivas"]`; `dr-nunez-mi` sin página
- [[INC-2026-014]] — acción 4: "Auditar otros protocolos con revisión vencida (dolor torácico, sepsis)"

### Diff

```diff
# Crear mediante operación INGEST o ONBOARD las páginas siguientes con frontmatter mínimo:
+ wiki/semantic/patologias/sepsis.md
+   type: concepto, decay_rate: low, tratada_segun→[[sepsis-adulto]] (cuando exista)
+ wiki/semantic/patologias/neumonia-adquirida-comunidad.md
+   type: concepto, decay_rate: low
+ wiki/semantic/farmacos/amoxicilina-clavulanico.md
+   type: entidad, decay_rate: low, tratamiento_de→(patología a determinar)
+ wiki/semantic/farmacos/noradrenalina.md
+   type: entidad, decay_rate: low
+ wiki/semantic/profesionales/dr-nunez-mi.md
+   type: entidad, decay_rate: low
+ wiki/procedural/protocolos-clinicos/protocolo-sepsis-adulto.md
+   type: sop, decay_rate: high, valid_until→(verificar en raw/)
+ wiki/procedural/protocolos-clinicos/protocolo-dolor-toracico.md
+   type: sop, decay_rate: high, valid_until→(verificar en raw/)
```

> ADVERTENCIA: los dos protocolos (`sepsis-adulto`, `dolor-toracico`) deben ingresarse
> con `valid_until` verificado contra su fuente en `raw/`. Si están vencidos, generarían
> candidatos adicionales de clase sev-5 en la siguiente auditoría (posible cadena CAND-01
> adicional). El `mutation_approver` debe solicitar las fuentes antes de aprobar P3 para
> esos dos protocolos.

---

## Tabla resumen

| id | origen | clase | score | status |
|---|---|---|---|---|
| P1 | CAND-01 | info vencida en dominio de seguridad | **55** | approved |
| P2 | CAND-02 | contradicción entre páginas wiki | **42** | approved |
| P3 | CAND-03 | vacío (link roto / categoría sin cobertura) | **27** | approved |

Gate humano: `mutation_approver: director-medico` aprueba/rechaza cada propuesta de
forma independiente. P1 acción 1 (publicar v4) es prerequisito de P1 acciones 2 y 3.
P3 requiere verificación de `valid_until` en fuentes `raw/` para los dos protocolos
antes de aplicar. Ninguna propuesta toca `raw/` (principio `gen-raw-inmutable`).
