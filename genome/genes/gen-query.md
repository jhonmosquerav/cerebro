---
id: gen-query
trigger: operación QUERY sobre un tema
status: active
version: 3
---

QUERY responde navegando el grafo, no leyendo todo, en dos pasos sancionados:

**Paso 1 — navegación (siempre primero).** Empieza en `index.md`, baja por el hub del área
si existe ([[gen-jerarquizacion-indice]]), sigue las relaciones `[[...]]` relevantes y abre
solo las páginas necesarias (presupuesto de contexto).

**Paso 2 — fallback léxico (solo tras agotar el paso 1).** Si la navegación no halla el
tema (2-3 saltos desde `index.md` — secciones/hubs plausibles y sus relaciones — sin
resultado), busca por CONTENIDO sobre `wiki/`: grep de los términos del tema y sus
variantes, incluido el `glossary` del manifiesto (en Obsidian equivale al buscador). Abre
SOLO las páginas que matchean y cítalas igual que en el paso 1 — el fallback localiza
candidatos, no lee todo, y respeta TODAS las reglas de abajo (confidencialidad incluida).
**Transparencia obligatoria:** declara en la respuesta "hallado por búsqueda léxica, no
por navegación" y deja línea en `log.md` (`QUERY fallback-lexico: <tema> → [[página]]`) —
es la señal para [[gen-lint]] de que a esas páginas les faltan relaciones o ancla.

En ambos pasos: cita las páginas-fuente consultadas y su `confidence`, **excepto las
`sensibilidad: confidencial`** ([[gen-confidencialidad]]): de esas no revela contenido
sensible ni las cita textualmente — responde con referencia indirecta o ID seudonimizado.
Advierte **siempre** lo vencido por `valido_hasta` ([[gen-vigencia-temporal]]), lo
contradictorio (`relations.contradice`) y la baja `confidence`, en vez de afirmar con
falsa seguridad. Si ni la navegación ni la búsqueda léxica encuentran, dilo — "no hay
información" significa que TAMPOCO el contenido lo contiene, no solo que el grafo no
llegó. No inventes.
