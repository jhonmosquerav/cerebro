# plugin/ — envoltorio instalable de CEREBRO (Fase 4.2)

Un plugin de Claude Code **mínimo** que no sustituye al repo: trae una sola skill
(`skills/cerebro/SKILL.md`) que enseña a clonar CEREBRO, elegir perfil con
`python tools/cerebro.py init --profile <p> [--blueprint <s>]`, aplicar el manifiesto con
`onboard apply` y operar el vault con los verbos de su `CLAUDE.md`. No contiene genes,
reglas ni hooks: la fuente de verdad sigue siendo la carpeta clonada.

## Instalar el plugin

```
/plugin marketplace add jhonmosquerav/cerebro
/plugin install cerebro@cerebro
```

El marketplace vive en `.claude-plugin/marketplace.json` (raíz del repo) y apunta a esta
carpeta como `source: ./plugin`. Si lo pruebas desde un clon local:
`/plugin marketplace add <ruta-del-clon>`.

## Qué NO hace

- No instala CEREBRO: para eso está `git clone` + `init` + `onboard apply` (la skill lo guía).
- No replica el genoma: si una regla cambia en `genome/genes/`, la skill no se entera ni
  debe enterarse; por eso remite siempre al `CLAUDE.md` del vault.
- No corre en el vault por sí solo: los hooks de memoria viven en `.claude/hooks/` del repo
  clonado y se gobiernan por `genome/perfil.md` (gen-perfiles), no por este plugin.

## Mantenimiento

Versiona `plugin.json` y `marketplace.json` a la vez. `tests/test_plugin.py` comprueba que
ambos parsean, que la skill tiene frontmatter `name`/`description` y que sigue remitiendo a
`init --profile`, `onboard apply` y `CLAUDE.md`.
