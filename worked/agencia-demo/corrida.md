# Corrida — agencia-demo

- **Empresa sintética**: Automatiza Andina SAS (agencia de automatización y marketing).
- **Entrada**: `company.yaml` = blueprint `onboard/blueprints/agencia.yaml` con el
  bloque `company` rellenado. Nada más se tocó.
- **Fecha determinista**: `2026-07-12` (parte de la entrada).
- **Herramienta**: `tools/cerebro.py onboard apply` (mecánico, 0 LLM).

## Comandos exactos

```bash
# sobre un clon limpio del template:
cp worked/agencia-demo/company.yaml onboard/company.yaml
python tools/cerebro.py onboard apply --date 2026-07-12
python tools/cerebro.py verify
python tools/cerebro.py hash --scope genome
```

## Salida esperada

16 acciones: perfil renderizado, 10 carpetas de taxonomía/entidades
(`taxonomia.txt`), 2 genes sembrados (`gen-accionables` v1 en `working`,
`gen-objecion-transversal` v1 en `semantic`), 2 líneas `gene_added` en
`genome/events.jsonl` (la segunda con `prev` = hash-chain), bloque
`## Estado` de `index.md` configurado.

Verificación byte a byte: `resultado-esperado/` + `state-hash.txt`
(automática en CI vía `tests/test_worked.py`; re-aplicar es no-op).
