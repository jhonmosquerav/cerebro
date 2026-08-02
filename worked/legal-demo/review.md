# Review honesto — legal-demo

## Qué salió bien

- **El caso sensible funciona igual de determinista**: `default_sensibilidad:
  confidencial` queda sembrado en el perfil y los umbrales del dominio
  (source_trust con `doctrina: 0.6`) se conservan exactos.
- **Hash-chain desde el nacimiento**: las 3 líneas `gene_added` de este caso
  quedan encadenadas (`prev` = sha256 de la anterior). Adulterar la primera
  siembra rompería la cadena de forma detectable — en un bufete eso no es
  cosmética, es defendibilidad.
- **Coherencia entre blueprint y genoma base, verificada**: la regla de
  `gen-vigencia-normativa` usa el enum `{vigente|en-revision|derogada}` que
  el gen base `gen-vigencia-temporal` v2 ya reconoce — el validador de
  esquema (`schema.py`) los tiene y LINT los acepta. Antes esa coherencia
  era fe; ahora es un test.

## Qué falló o rechinó durante la construcción

1. **El glosario con tildes en las claves** (`cláusula-tipo:`) obligó a que
   el parser aceptara claves unicode. Trivial, pero es el tipo de detalle
   que un parser "estricto" mal diseñado habría rechazado — y el dominio
   legal en español está lleno de ellos.
2. **`source_trust.doctrina` no es un tipo estándar** (oficial/interna/blanda).
   El validador lo acepta (cualquier tipo con valor 0–1 es legal según
   gen-confianza-por-fuente y el delta conservador de gen-ciclo-de-vida v4),
   pero vale dejar dicho que el scanner de CONSOLIDATE aplica el delta del
   tipo estándar inferior para tipos custom — tal como manda el gen.

## Qué NO cubre lo mecánico (frontera honesta)

- **El secreto profesional en operación**: sembrar `confidencial` como
  default es mecánico; RESPETARLO al ingerir, citar y anclar es del agente
  bajo gen-confidencialidad (y LINT lo vigila con SEN-01 tras cada corrida).
- **El chequeo de conflicto de interés** (gen-conflicto-interes) es una regla
  sembrada que el agente ejecutará al ingerir clientes; la herramienta solo
  la instala.
- **Contenido**: cero expedientes ingeridos. El piloto con corpus real y sus
  20 preguntas doradas (B-01…B-06) sigue pendiente — este caso NO lo sustituye.

## Regeneración de la salida esperada (2026-07-29)

`taxonomia.txt` se regeneró porque la ENTRADA cambió: `company.yaml` ganó la carpeta
`wiki/semantic/sintesis`. El motivo viene del aviso que introdujo `gen-onboard` v6
(F0-11): el manifiesto declaraba `sintesis_umbral: 3` y no tenía destino para las
síntesis que se compromete a producir. El hueco estaba en **9 de los 10 manifiestos** del
repo.

**El `state-hash` NO cambió**: el genoma resultante es byte-idéntico y solo crece la
taxonomía de `wiki/`. Regenerado con la herramienta, como manda `worked/README.md`.
