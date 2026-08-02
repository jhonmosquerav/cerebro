# Corrida — piscc-demo

- **Entidad sintética**: Alcaldía Municipal de Peñas Blancas (municipio ficticio;
  el marco normativo que codifican los genes SÍ es real y verificado).
- **Entrada**: `company.yaml` = blueprint `onboard/blueprints/seguridad-territorial.yaml`
  con el bloque `company` rellenado. Nada más se tocó.
- **Fecha determinista**: `2026-07-12` (parte de la entrada).
- **Herramienta**: `tools/cerebro.py onboard apply` (mecánico, 0 LLM).

## Comandos exactos

```bash
# sobre un clon limpio del template:
cp worked/piscc-demo/company.yaml onboard/company.yaml
python tools/cerebro.py onboard apply --date 2026-07-12
python tools/cerebro.py verify
python tools/cerebro.py hash --scope genome
```

## Salida esperada

22 acciones: perfil renderizado, 13 carpetas de taxonomía/entidades, 4 genes
sembrados (`gen-dato-con-corte`, `gen-territorializacion`, `gen-linea-base-y-meta`,
`gen-trazabilidad-fonset`, todos v1 en `semantic`), 4 líneas `gene_added`
encadenadas por hash en `genome/events.jsonl`, bloque `## Estado` configurado.

Verificación byte a byte: `resultado-esperado/` + `state-hash.txt`
(automática en CI; re-aplicar es no-op).

## Marco normativo que codifican los genes

Verificado en fuente primaria el 2026-07-27 — ver `review.md` para el detalle
de qué se comprobó y qué no.

| Norma | Qué establece | Gen que lo codifica |
|---|---|---|
| Ley 1801 de 2016, art. 205 nº 4 | El alcalde debe *elaborar y ejecutar el Plan Integral de Seguridad y Convivencia*; es la primera autoridad de policía | motiva todo el blueprint |
| Ley 62 de 1993 | Primer referente normativo que da vida a los PISCC | contexto |
| Ley 418 de 1997, art. 119 | Todo municipio y departamento crea su FONSET | `gen-trazabilidad-fonset` |
| Ley 1421 de 2010, art. 8 | Informe anual de ejecución del FONSET al Ministerio del Interior | `gen-trazabilidad-fonset` |
| Decreto 399 de 2011 | El Comité Territorial de Orden Público estudia, aprueba y hace seguimiento a la destinación del FONSET | `gen-trazabilidad-fonset` |
| Guía metodológica DNP | Línea base, indicadores, metas y focalización | `gen-linea-base-y-meta`, `gen-territorializacion` |
