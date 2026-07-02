---
id: gen-confianza-por-fuente
trigger: asignar confidence inicial al ingerir una fuente
status: active
version: 2
---

La `confidence` inicial no es arbitraria: se ancla al tipo/credibilidad de la fuente. Fuentes
primarias u oficiales (contrato firmado, ficha técnica, protocolo aprobado, dato de sistema)
nacen altas (≥0.85). Señales blandas (reseñas, redes, rumores, opiniones sin verificar) nacen
bajas (≤0.5) y entran **solo como corroboración** (relación `usa` / `corrobora`), nunca como
hecho primario. El mapeo fuente→confianza puede declararse por empresa en `onboard/company.yaml`
(`source_trust`). Varias señales blandas concordantes pueden subir la `confidence` de un hecho,
pero no sustituyen a una fuente primaria: el **refuerzo también se ancla a la fuente** —
los deltas de subida por tipo y el techo anclado a `source_trust` viven en
[[gen-ciclo-de-vida]]; con los valores de ejemplo, una página solo-blanda topa en 0.5.
Complementa [[gen-ingest]] y [[gen-ciclo-de-vida]].
