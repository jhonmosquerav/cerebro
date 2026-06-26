---
title: Anafilaxia
type: concepto
tier: semantic
tags: [patologia, alergia, urgencia, anafilaxia]
confidence: 0.9
created: 2026-06-22
last_reinforced: 2026-06-22
decay_rate: low
sources:
  - "[[raw/PROT-ANAFILAXIA-v3-2024]]"
  - "[[raw/HC-EP-2026-0488-anonimizada]]"
relations:
  usa: []
  depende_de: []
  tratada_segun: ["[[protocolo-anafilaxia]]"]
  contradice: []
  reemplaza: []
---

# Anafilaxia

Reacción de hipersensibilidad sistémica grave, de inicio rápido y potencialmente mortal,
con compromiso de vía aérea, respiratorio o circulatorio tras exposición a un alérgeno.

## Manejo
- Tratamiento de elección: **[[adrenalina]] IM** (ver dosis en [[protocolo-anafilaxia]]).
- Segunda línea (coadyuvante): antihistamínico y corticoide IV.
- Observación ≥ 6 h por riesgo de reacción bifásica.

## Trazabilidad clínica ([[gen-trazabilidad-clinica]])
- `tratada_segun` → [[protocolo-anafilaxia]]  ⚠️ (vigente solo hasta 2026-03-01)
- `tratamiento_de` ← [[adrenalina]]
- Caso observado: [[PAC-7731]] (`presenta_patologia`).
