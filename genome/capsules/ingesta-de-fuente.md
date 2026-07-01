---
id: cap-ingesta-de-fuente
status: active
version: 2
composes: [gen-raw-inmutable, gen-frontmatter-obligatorio, gen-confidencialidad, gen-ingest]
---

# Cápsula: ingesta de fuente

Workflow completo para convertir una fuente cruda en conocimiento enlazado.
Combina genes; ejecútalos en orden y de forma idempotente.

## Pasos
1. **Leer** la fuente desde `raw/` sin modificarla ([[gen-raw-inmutable]]).
2. **Clasificar** el tipo (`concepto | entidad | fuente | sintesis | sop`) y el `tier`
   destino (normalmente `semantic/` para hechos, `procedural/` para procesos).
3. **Clasificar la sensibilidad** ([[gen-confidencialidad]]): asigna `sensibilidad`
   (default = `default_sensibilidad` del manifiesto; si no, `interno`). Si detectas PII real
   sin anonimizar (nombre + identificador de una persona física), **DETENTE y pregunta**
   antes de seguir. Lo `confidencial` no se ancla, no se fusiona ni se cita textual.
4. **Crear/actualizar** la página con frontmatter válido ([[gen-frontmatter-obligatorio]]).
   Si ya existe, actualízala y sube `last_reinforced` en vez de duplicar.
5. **Extraer** conceptos y entidades clave; crea sus páginas si no existen.
6. **Enlazar** con `relations` tipadas (`usa`, `depende_de`, `contradice`, `reemplaza`)
   y `[[wiki-links]]` hacia páginas relacionadas.
7. **Registrar**: añade ancla en `index.md` **solo si `sensibilidad != confidencial`**
   ([[gen-confidencialidad]]) y una línea en `log.md`.

## Criterio de hecho
- La fuente quedó intacta en `raw/`.
- La nueva página tiene frontmatter, fuentes y al menos una relación entrante o saliente.
- No se duplicó conocimiento existente.
