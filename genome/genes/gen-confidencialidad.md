---
id: gen-confidencialidad
trigger: ingesta o consulta de información sensible (PII, secreto profesional, datos de cliente/paciente)
status: active
version: 1
---

Eje de sensibilidad sobre toda página: `sensibilidad: publico | interno | confidencial`
(default `interno`). Las páginas `confidencial`: (1) no se anclan en `index.md`; (2) no se
promueven de tier ni se fusionan por CONSOLIDATE; (3) QUERY no las cita textualmente ni
revela su contenido sensible sin autorización explícita — responde con referencia indirecta
o ID seudonimizado. Además, INGEST **se detiene y pregunta** si detecta PII real sin
anonimizar (nombre + identificador de una persona física). Regla práctica: el conocimiento
clínico/legal/comercial estable es `publico` o `interno`; los datos de la persona concreta
son `confidencial`. Complementa [[gen-frontmatter-obligatorio]] y la privacidad de toda empresa.
