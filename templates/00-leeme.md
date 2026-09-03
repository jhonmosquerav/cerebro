---
title: Plantillas de página — léeme
type: meta
---

# Plantillas de página (capa Obsidian, opcional)

Una plantilla por `type` del esquema de [[gen-frontmatter-obligatorio]], para que una
persona pueda crear a mano una página que **pase LINT** sin memorizar el frontmatter.
Las usa el plugin core **Templates** (ya activo en el preset: `Ctrl/Cmd + P` → *Insertar
plantilla*). Fuera de Obsidian son markdown de referencia; ningún agente las lee como
conocimiento (viven fuera de `wiki/` y no resuelven `[[wikilinks]]`).

| Plantilla | `type` | Tier donde aterriza |
|---|---|---|
| [[concepto]] | concepto | `wiki/semantic/<categoría>/` |
| [[entidad]] | entidad | `wiki/semantic/<categoría>/` (con `estado` opcional) |
| [[fuente]] | fuente | `wiki/semantic/fuentes/` |
| [[sintesis]] | sintesis | `wiki/semantic/sintesis/` |
| [[sop]] | sop | `wiki/procedural/<categoría>/` |
| [[hub]] | hub | raíz del tier (`hub-<área>.md`) |
| [[observacion]] | observacion | `wiki/working/` |
| [[sesion]] | sesion | `wiki/episodic/` |

Reglas que la plantilla no puede cumplir por ti:

- `id_pagina` = `<tier>/<categoría>/<slug>` y debe coincidir con la ruta del archivo
  ([[gen-identidad-de-pagina]]). Rellénalo tras decidir dónde guardas la página.
- Los enlaces dentro de propiedades van **entre comillas**: `sucede_a: "[[otra-pagina]]"`.
- `sensibilidad: confidencial` → la página no se ancla ni se cita textual
  ([[gen-confidencialidad]]); no pongas nombres de personas en título ni archivo.
- Tras crear páginas a mano, corre `python tools/cerebro.py lint --as-of <hoy>`.

> Las variables `{{date}}` y `{{title}}` las sustituye Obsidian al insertar. Van entre
> comillas para que el YAML sea válido también antes de la sustitución.
