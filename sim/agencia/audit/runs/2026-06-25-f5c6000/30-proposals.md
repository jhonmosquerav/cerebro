---
run_id: 2026-06-25-f5c6000
date: 2026-06-25
gene_version: gen-auto-auditoria v1
candidates_maker: 5
confirmed_auditor: 5
proposals_count: 3
status: pending_gate
---

# Propuestas — AUDIT 2026-06-25-f5c6000

Top-3 candidatos confirmados por el auditor, ordenados por impacto descendente.
N = min(3, 5 confirmados) = 3. Todas quedan `status: pending` hasta aprobación humana.
Evidencia: referencias por `[[link]]` — ningún valor sensible transcrito (no hay páginas
`sensibilidad: confidencial` en este escenario).

---

## P1

```
id: P1
fecha: 2026-06-25
motivo: >
  El precio de la propuesta Vértice (PROP-2026-038) lleva 11 días vencido
  (valido_hasta: 2026-06-14) pero la propuesta y el lead en negociación no
  advierten de ello. Un agente que consulte la propuesta sin leer la página
  de precio podría citar cifras expiradas en una negociación activa.
evidencia:
  - [[precio-vertice-PROP-2026-038]] — campo valido_hasta: 2026-06-14 (vencido)
  - [[propuesta-vertice-PROP-2026-038]] — relación define_precio sin advertencia
  - [[lead-inmobiliaria-vertice]] — estado: en-negociacion sin campo advertencia
diff: |
  # propuesta-vertice-PROP-2026-038.md — añadir al frontmatter:
  advertencia: "precio [[precio-vertice-PROP-2026-038]] vencido 2026-06-14; requiere recotización antes de citar cifras."

  # lead-inmobiliaria-vertice.md — añadir al frontmatter:
  advertencia: "propuesta [[propuesta-vertice-PROP-2026-038]] con precio vencido 2026-06-14; validar precio antes de avanzar en negociación."
score:
  clase: info vencida en dominio de seguridad
  severidad: 5
  alcance: 3
  impacto: 53
status: pending
```

---

## P2

```
id: P2
fecha: 2026-06-25
motivo: >
  El follow-up de Inmobiliaria Vértice lleva 40 días vencido (fecha_objetivo:
  2026-05-16) y la junta de decisión del lead (2026-05-19) ya pasó hace 37 días.
  El lead conserva estado: en-negociacion como si el proceso estuviera activo,
  sin señalizar que la ventana de cierre expiró. Un QUERY sobre el lead devuelve
  un estado operativo engañoso para el equipo de ventas.
evidencia:
  - [[followup-vertice-2026-05-16]] — fecha_objetivo: 2026-05-16, estado: vencido
  - [[lead-inmobiliaria-vertice]] — estado: en-negociacion sin propagación de vencimiento
diff: |
  # lead-inmobiliaria-vertice.md — modificar estado y añadir advertencia en frontmatter:
  estado: en-negociacion-sin-followup
  advertencia: "follow-up [[followup-vertice-2026-05-16]] vencido 2026-05-16; junta decisión 2026-05-19 ya pasó. Validar si lead sigue activo o se perdió."
score:
  clase: info vencida en dominio de seguridad
  severidad: 5
  alcance: 2
  impacto: 52
status: pending
```

---

## P3

```
id: P3
fecha: 2026-06-25
motivo: >
  gen-lead-a-cliente exige que "el historial del lead (calls, objeciones,
  propuesta origen) se enlace desde el cliente con [[wiki-links]]". El cliente
  [[cliente-dental-sonrisa]] tiene proviene_de correcto, pero su bloque de
  relations no contiene enlace estructurado hacia [[objecion-bot-malo]] ni
  hacia la propuesta origen PROP-2026-019. El cuerpo afirma que los enlaces
  existen ("historial y objeciones del lead se conservan y enlazan aquí"),
  contradiciendo lo que la estructura de relaciones materializa efectivamente.
evidencia:
  - [[gen-lead-a-cliente]] — regla: "se enlaza desde el cliente con [[wiki-links]]"
  - [[cliente-dental-sonrisa]] — relations sin historial_lead ni objeciones_lead
  - [[lead-dental-sonrisa]] — usa: [[objecion-bot-malo]]; propuesta origen PROP-2026-019
diff: |
  # cliente-dental-sonrisa.md — añadir en el bloque relations:
  historial_lead: ["[[lead-dental-sonrisa]]"]
  objeciones_lead: ["[[objecion-bot-malo]]"]
  propuesta_origen: ["PROP-2026-019"]
  # Y en el cuerpo, reemplazar la mención genérica por una sección estructurada:
  # "## Historial del lead origen"
  # - Objeción principal: [[objecion-bot-malo]] (resuelta en call 2026-01-22)
  # - Propuesta origen: PROP-2026-019 (firmada 2026-02-10)
score:
  clase: contradicción entre páginas wiki
  severidad: 4
  alcance: 2
  impacto: 42
status: pending
```

---

## Candidatos no incluidos en el top-3

| id | clase | impacto | razón de exclusión |
|---|---|---|---|
| C5 | redundancia (n8n/Make) | 22 | por debajo del top-3; N = min(3,5) = 3 |
| C3 | vacío (onboarding-cliente) | 21 | por debajo del top-3; tiebreak alfabético tras C5 |

Nota de desempate C5 vs C3: impacto 22 > 21, por lo que C5 precede a C3 antes de ser
excluido del top-3. Dentro del top-3, el desempate no fue necesario (impactos distintos).
