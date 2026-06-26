---
title: Adrenalina (epinefrina)
type: entidad
tier: semantic
tags: [farmaco, vademecum, urgencia, anafilaxia, paro]
confidence: 0.92
created: 2026-06-22
last_reinforced: 2026-06-22
decay_rate: low
sources:
  - "[[raw/PROT-ANAFILAXIA-v3-2024]]"
  - "[[raw/HC-EP-2026-0488-anonimizada]]"
relations:
  usa: []
  depende_de: []
  tratamiento_de: ["[[anafilaxia]]"]
  indicado_por: ["[[protocolo-anafilaxia-v4]]"]
  contradice: []
  reemplaza: []
---

# Adrenalina (epinefrina)

Catecolamina de uso urgente; primera línea en anafilaxia y soporte en paro/shock.

## Dosis en anafilaxia (adulto)
- **0,5 mg IM** (0,5 mL de solución 1:1000) en cara anterolateral del muslo.
- Repetir cada 5–15 min si no hay respuesta. Fuente: [[protocolo-anafilaxia-v4]].

> ⚠️ Nota: `indicado_por` apuntaba a [[protocolo-anafilaxia]] v3 (status: deprecado,
> vencido al 2026-03-01). Actualizado a [[protocolo-anafilaxia-v4]] (vigente hasta 2028-03-01).

## Trazabilidad clínica ([[gen-trazabilidad-clinica]])
- `tratamiento_de` → [[anafilaxia]]
- `indicado_por` → [[protocolo-anafilaxia-v4]]
- Administrada en el episodio [[PAC-7731]] (`tratado_con`).

> Nota: la dosis IM de 0,5 mg no cambió entre v3 y la futura v4 del protocolo; por eso el
> manejo del episodio [[PAC-7731]] fue correcto pese a usarse una guía vencida.
