# Corrida — legal-demo

- **Empresa sintética**: Bufete Río de Oro (litigio civil y mercantil).
- **Entrada**: `company.yaml` = blueprint `onboard/blueprints/legal.yaml` con el
  bloque `company` rellenado. Nada más se tocó.
- **Fecha determinista**: `2026-07-12` (parte de la entrada).
- **Herramienta**: `tools/cerebro.py onboard apply` (mecánico, 0 LLM).

## Comandos exactos

```bash
# sobre un clon limpio del template:
cp worked/legal-demo/company.yaml onboard/company.yaml
python tools/cerebro.py onboard apply --date 2026-07-12
python tools/cerebro.py verify
python tools/cerebro.py hash --scope genome
```

## Salida esperada

19 acciones: perfil renderizado (con `default_sensibilidad: confidencial` a
la vista), 11 carpetas de taxonomía/entidades, 3 genes sembrados
(`gen-vigencia-normativa`, `gen-conflicto-interes`, `gen-version-clausula`,
todos v1 en `semantic`), 3 líneas `gene_added` encadenadas por hash en
`genome/events.jsonl`, bloque `## Estado` configurado.

Verificación byte a byte: `resultado-esperado/` + `state-hash.txt`
(automática en CI; re-aplicar es no-op).
