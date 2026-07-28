---
id: gen-territorializacion
trigger: "se ingiere un hecho, cifra, programa o intervención"
status: active
version: 1
---

Toda página de este tier declara 'unidad_territorial' al mayor nivel de desagregación disponible (municipio > comuna/corregimiento > barrio > cuadrante) y se enlaza con 'focaliza_en' a la entidad territorial correspondiente. El PISCC se evalúa por focalización: un dato sin territorio no prioriza nada. Si la fuente solo trae el agregado municipal, se declara así explícitamente ('unidad_territorial: municipio') en vez de dejar el campo vacío — la ausencia de desagregación es información, el silencio no.

> Gen de sector sembrado mecánicamente por ONBOARD desde `onboard/company.yaml` (2026-07-12).
> Mutarlo pasa por [[gen-compuerta-mutacion]] como cualquier gen.
