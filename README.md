# 🧠 CEREBRO

> Sistema de documentación **agéntico, mutagénico y reproducible**, construido 100% sobre
> markdown + JSONL. Cualquier empresa lo clona, corre `ONBOARD` y opera su conocimiento.
> **Sin RAG, sin vectores, sin servidores.**

CEREBRO convierte la documentación de una empresa en un *cerebro vivo* hecho solo de archivos.
Un agente de IA (Claude Code, Cursor, OpenClaw…) lo lee y lo escribe como si fuera su memoria:
clasifica lo que entra, lo conecta con lo que ya sabe y —lo más importante— **detecta patrones
y propone mejoras a sus propias reglas**, que tú apruebas. Recuerda entre sesiones y deja cada
cambio auditado y reversible.

---

## ✨ Por qué es distinto

- **🧬 Mutagénico** — no es un wiki estático. Observa cómo se usa y propone reescribir sus
  propias reglas (sus *genes*), siempre con tu visto bueno.
- **♾️ Memoria infinita (v1, hooks reales)** — al arrancar, un hook carga `index.md` y la
  bitácora reciente; antes de compactar el contexto, otro vuelca un snapshot mecánico de la
  sesión a `wiki/working/`; al cerrar, un tercero exige el resumen episódico si la sesión
  tocó el cerebro. El destilado inteligente lo hace el agente, guiado por esos hooks
  (`.claude/hooks/README.md` documenta el detalle y sus límites). Memoria por capas, como
  el cerebro humano.
- **🔁 Reproducible y auditable** — reproducible **en estructura** (manifiesto declarativo +
  genoma versionado), **ejecutado por un LLM** —no por un script determinista— y con
  **registro auditable**: cada mutación queda con su fecha, su porqué y su diff en
  `genome/events.jsonl`. Es *git para el conocimiento*.
- **🔌 Portable** — todo es markdown; corre con cualquier agente que lea archivos. `AGENTS.md`
  espeja a `CLAUDE.md`.
- **🪶 Sin infraestructura** — son tus archivos, en tu disco. Ni servidor, ni base vectorial,
  ni suscripción.

---

## 🌱 Génesis — cómo surgió CEREBRO

CEREBRO nace de una idea simple y poderosa: la **"LLM Wiki"** popularizada por
**[Andrej Karpathy](https://github.com/karpathy/llm-wiki)** — una wiki de markdown que un LLM
consulta y actualiza, sin RAG ni vectores. Una guía de la comunidad mostró cómo montarla con
Claude Code + Obsidian en minutos.

Pero la pregunta que lo disparó todo fue otra: *¿y si en vez de una wiki estática fuera un
sistema que **evoluciona sus propias reglas**, recuerda sin límite y cualquier empresa puede
reproducir?*

De ahí, en co-construcción con **Claude Code**, se extendió la idea base:
- El genoma se partió en **genes** atómicos y **cápsulas** versionables (en vez de un
  `CLAUDE.md` monolítico).
- Se añadió **memoria por capas con decaimiento**, **confidencialidad**, **vigencia temporal**
  y **relaciones tipadas**.
- `ONBOARD` se hizo **reproducible por manifiesto** (`onboard/company.yaml`).
- Cada mutación pasa por una **compuerta** (modo híbrido: se propone → apruebas → se aplica →
  se audita).

Y luego se **puso a prueba en simulación multi-sector** (producción, agencia de marketing,
bufete legal, clínica y e-commerce) con agentes en paralelo. Las fricciones que aparecían en
varios sectores a la vez se convirtieron en **mutaciones del genoma base** —cada una
propuesta, aprobada y **registrada paso a paso en `genome/events.jsonl`**—, endureciendo las
reglas corrida a corrida. Lo probado en vivo hasta hoy es el meta-sistema (EVOLVE y AUDIT
operando sobre el propio genoma); el piloto con datos reales de una empresa es el siguiente
paso del backlog.

---

## 🏗️ Arquitectura

```
cerebro/
├── CLAUDE.md / AGENTS.md     # manual del agente (AGENTS.md espeja a CLAUDE.md → portabilidad)
├── index.md / log.md         # mapa principal + bitácora operativa
├── genome/
│   ├── genes/                # reglas atómicas (los "genes")
│   ├── capsules/             # combinaciones de genes para un workflow
│   ├── company-profile.md    # identidad de la empresa (lo llena ONBOARD)
│   └── events.jsonl          # auditoría append-only de mutaciones (replay/rollback)
├── onboard/                  # manifiesto reproducible (company.yaml) + blueprints
├── raw/                      # fuentes crudas, INMUTABLES
├── wiki/
│   ├── working/              # observaciones recientes (decae rápido)
│   ├── episodic/             # resúmenes por sesión
│   ├── semantic/             # conocimiento consolidado
│   └── procedural/           # SOPs y procesos
├── dashboards/               # paneles Dataview + lente de grafo (visualización opcional)
├── audit/                    # corridas de AUDIT y evaluaciones (con sus propuestas)
├── ops/                      # runbooks de operación segura: git seguro + backup cifrado
├── .obsidian/                # preset Obsidian (opcional, removible)
└── .claude/                  # hooks reales del loop de memoria + permisos endurecidos
```

---

## 🚀 Inicio rápido

1. **Clona** este repo (o úsalo como template).
2. **Abre la carpeta** con Claude Code (o Cursor / OpenClaw — leen el mismo `CLAUDE.md`).
3. Corre **`ONBOARD`** → te entrevista y genera `onboard/company.yaml`, luego siembra el
   genoma de tu sector a partir de ese manifiesto (reproducible en estructura).
4. Suelta fuentes en **`raw/`** y corre **`BULK INGEST`**.
5. Consulta con **`QUERY <tema>`**. Mantén con **`LINT`** y **`CONSOLIDATE`** cada 1–2 semanas.

> ¿Quieres el tablero visual? Abre la carpeta como Vault en Obsidian e instala el plugin
> **Dataview** (ya viene declarado en el preset). Ver `dashboards/00-leeme.md`.

---

## ⚙️ Operaciones

| Verbo | Qué hace |
|---|---|
| `ONBOARD` | Aplica el manifiesto `onboard/company.yaml` → siembra perfil + genes del sector (reproducible en estructura). |
| `INGEST <X>` | Clasifica una fuente, crea su página con frontmatter, extrae conceptos y la enlaza. |
| `BULK INGEST` | Corre `INGEST` sobre todo `raw/`. |
| `QUERY <X>` | Navega el grafo desde `index.md` y responde citando las páginas-fuente. |
| `LINT` | Detecta huérfanos, contradicciones, vencidos y relaciones inválidas; propone y aplica tras OK. |
| `CONSOLIDATE` | Promueve conocimiento confirmado, fusiona duplicados, decae lo no reforzado. |
| `EVOLVE` | Detecta patrones y **propone** mutaciones del genoma (solo se aplican con tu OK). |
| `AUDIT` | Se auto-audita con **maker≠auditor**: busca contradicciones, vacíos y reglas obsoletas, y te **propone** ≤3 mejoras de mayor impacto bajo tu gate. Corridas reproducibles en `audit/runs/`, ancladas al SHA de git. |
| `GRAPH` | Lente de grafo externa (opcional) sobre una copia *staging* de `wiki/` filtrada por allowlist (solo páginas explícitamente `publico`/`interno`); deriva señales (hubs, comunidades, caminos, islas) y las **propone** a las operaciones de mantenimiento. Salida derivada, no es fuente de verdad. |

---

## 🔁 Reproducibilidad y replay

CEREBRO es **reproducible en estructura, ejecutado por LLM y con registro auditable** —
no un script determinista. En concreto:

- **Onboarding reproducible** — el genoma de una empresa se siembra desde un manifiesto
  declarativo (`onboard/company.yaml`): mismo manifiesto → misma estructura de genoma y
  perfil. Quien lo aplica es un LLM siguiendo reglas versionadas, así que la garantía es de
  estructura y protocolo, no de bit exacto. Hay [blueprints de sector](onboard/blueprints/)
  listos para copiar y aplicar (producción, agencia, legal, salud, e-commerce).
- **Evolución auditable** — cada mutación del genoma queda como una línea en
  `genome/events.jsonl` (con fecha, señal y diff) más su commit de git (norma de la casa:
  una mutación = un commit). Puedes **reconstruir o revertir** cómo llegó el genoma a su
  estado actual. Es *git para el conocimiento*.
- **Enforcement, honesto** — hoy los invariantes se protegen con las reglas del genoma, los
  permisos del agente (`.claude/settings.json` **deniega** las herramientas de escritura
  sobre `raw/` y **pide confirmación** para `genome/`) y la auditoría maker≠auditor. Los
  validadores mecánicos (frontmatter, enlaces, integridad del ledger) están **en el
  backlog**: todavía no existen.

Arranque reproducible: **clona → elige un blueprint → rellena tus datos → `ONBOARD`.**

---

## ✅ Buenas prácticas

- **Navega desde `index.md`**; nunca cargues toda la wiki (presupuesto de contexto).
- **`raw/` es inmutable**: solo se lee. El conocimiento derivado vive en `wiki/`.
- **Toda mutación del genoma pasa por la compuerta** y deja una línea en `events.jsonl`.
- **Frontmatter obligatorio** en cada página de `wiki/` (Obsidian/Dataview-friendly).
- **Cada mutación = 1 commit** → permite replay y rollback.
- **Tu `ONBOARD` real va en un clon**, no en este template (manténlo neutro y reutilizable).
- **Git seguro en el clon con datos reales**: remoto **privado desde el día cero** (o
  ninguno) + checklist pre-push → `ops/runbook-git-seguro.md`.
- **Backup cifrado off-site** con prueba de restauración (`backup.sh --verify-restore`) →
  `ops/backup/`.
- **Hooks en bash POSIX**: entrecomilla los comandos (caracteres como `()` rompen la sintaxis).
- **Lo confidencial** (PII, secreto profesional) no se ancla en index, no se fusiona ni se
  cita textual.
- Tras cualquier cambio del genoma, re-sincroniza `AGENTS.md` con `CLAUDE.md`.

---

## 🙏 Agradecimientos

CEREBRO no existiría sin las ideas y herramientas de otros:

- **[Andrej Karpathy](https://github.com/karpathy/llm-wiki)** — por la idea original de la
  *LLM Wiki*: una wiki de markdown que el modelo lee y mantiene, sin RAG ni vectores. Es la
  semilla de todo esto.
- **[Benjamín Cordero](https://www.youtube.com/watch?v=p5YgvC6yzCs)** y la comunidad de Skool
  **Imperio** — por el video *"Claude Code + Obsidian = Memoria Infinita"*, que mostró el setup
  y encendió la chispa de este proyecto.
- **[Obsidian](https://obsidian.md)** y su plugin **Dataview** — la ventana visual que
  convierte el grafo y el frontmatter en algo navegable y consultable.
- **[Anthropic](https://www.anthropic.com) / Claude Code (Claude Opus 4.8)** — co-arquitecto
  de la extensión mutagénica: el genoma por genes, la compuerta de mutación, el `ONBOARD`
  reproducible y la validación en múltiples escenarios de industria.

Y a la idea de fondo de toda la comunidad de *second brain* / PKM, que lleva años explorando
cómo convertir notas sueltas en conocimiento conectado.

---

## 📄 Licencia

**MIT** — clónalo, úsalo y adáptalo libremente. Ver [`LICENSE`](LICENSE).

---

## 🤝 Contribuir

Es un sistema de archivos: clónalo, adáptalo a tu empresa y haz que evolucione. Si mejoras un
gen o una cápsula que sirva a cualquiera, un PR es bienvenido. La regla de oro: **toda mutación
del genoma se propone y se audita** — nada se aplica en silencio.
