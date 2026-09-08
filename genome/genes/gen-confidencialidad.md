---
id: gen-confidencialidad
trigger: ingesta o consulta de información sensible (PII, secreto profesional, datos de cliente/paciente)
status: active
version: 4
---

Eje de sensibilidad sobre toda página: `sensibilidad: publico | interno | confidencial`
(default tomado de `default_sensibilidad` del manifiesto si lo declara —dominios sensibles como
legal/salud suelen fijar `confidencial`—; si no existe, `interno`). Las páginas `confidencial`: (1) no se anclan en `index.md`; (2) no se
promueven de tier ni se fusionan por CONSOLIDATE; (3) QUERY no las cita textualmente ni
revela su contenido sensible sin autorización explícita — responde con referencia indirecta
o ID seudonimizado, sin exponer tampoco sus metadatos reidentificadores (título, nombre de
archivo, tags, relaciones): el seudónimo cubre también el enlace o mención. Regla práctica
de nombrado: una página `confidencial` no lleva el nombre de la persona en el título ni en
el nombre de archivo — usa el ID seudonimizado. Además, INGEST **se detiene y pregunta** si detecta PII real sin
anonimizar (nombre + identificador de una persona física). Regla práctica: el conocimiento
clínico/legal/comercial estable es `publico` o `interno`; los datos de la persona concreta
son `confidencial`. Complementa [[gen-frontmatter-obligatorio]] y la privacidad de toda empresa.

**Nada que no sea `publico` sale del vault, por ningún canal.** El campo nativo `publish`
(declarado por este gen; es el que Obsidian Publish y cualquier exportador que lo respete
usan para decidir qué se publica) solo puede ser `true` en páginas `sensibilidad: publico`.
En `interno`, `confidencial` o sin campo (hereda el default del manifiesto, que nunca es
`publico` por omisión) es **error SEN-02 de LINT, mecánico** — no aviso: publicar por
descuido no se deshace. Misma regla que ya rige la lente de grafo y su render nativo
([[gen-graph-lens]]: allowlist fail-closed) y la CLI (`ops/runbook-obsidian-cli.md`).
