# Review honesto — piscc-demo

## Qué salió bien

- **El primer blueprint que no sale de una simulación.** Los otros cinco se
  destilaron de sandboxes sintéticos; este codifica obligaciones legales
  colombianas verificadas en fuente primaria. `gen-trazabilidad-fonset` no
  dice "conviene documentar el gasto": dice que sin acta del Comité
  Territorial de Orden Público la página queda `estado: sin-respaldo` y QUERY
  lo advierte siempre, porque el Decreto 399 de 2011 pone esa aprobación como
  condición. Es la diferencia entre una buena práctica y un requisito.
- **Los `relation_types` del dominio ganan su sitio.** Sin
  `reglamenta / financia / mide / focaliza_en / reporta_a`, la semántica del
  sector se aplasta en `usa` y se pierde justo lo que hace auditable un PISCC:
  qué norma reglamenta a cuál, qué fuente financia qué programa, qué indicador
  mide qué delito. Mismo patrón que resolvió la fricción del blueprint legal.
- **La decisión de sensibilidad es al revés que en legal, y a propósito.**
  `default_sensibilidad: interno`, no `confidencial`: el PISCC es un documento
  público y la rendición de cuentas es parte del mandato. Lo reservado
  (víctimas identificables, inteligencia) se marca página a página. Sembrar
  `confidencial` por defecto habría sido cómodo y habría contradicho el deber
  de publicidad.
- **Cuatro genes de sector**, más que cualquier otro blueprint. No es
  inflación: el genoma base cubre vigencia, clase temporal y confianza por
  fuente, pero no tiene nada que diga que una cifra sin corte no es un dato,
  ni que un objetivo sin línea base es una intención.

## Qué falló o rechinó durante la construcción

1. **La primera corrida abortó**: `manifiesto ilegible: línea 27: lista flow
   sin cerrar`. Yo había escrito `document_types` y `taxonomy.semantic` como
   listas `[a, b, c]` partidas en dos líneas — **YAML válido que `miniyaml` no
   soporta**. Dos lecturas, ambas ciertas: (a) la herramienta se comportó
   exactamente como promete —abortó *sin escribir nada*, no dejó un vault a
   medias—, y eso quedó probado en vivo y no en un test; (b) hay una brecha
   real entre "YAML" y "el subconjunto de YAML que parsea CEREBRO", y un
   usuario que copie un manifiesto de otra herramienta la va a encontrar. No
   la arreglé aquí: es un hallazgo para EVOLVE/backlog, no algo que se cuela
   en un caso trabajado.
2. **Me equivoqué generando `taxonomia.txt` a mano.** Calculé la ruta relativa
   restando longitudes de string y Windows me dio la ruta corta (`JHONAL~1`)
   en una punta y la larga en la otra: salieron rutas mutiladas
   (`d/piscc-gen/wiki/...`). Error mío, no del producto — pero ilustra
   justamente por qué el contrato de `worked/` exige que la salida esperada la
   genere la herramienta y la valide el test: si me hubiera fiado de mi propia
   inspección, el caso habría entrado roto.
3. **`source_trust.percepcion` no es un tipo estándar** (oficial/interna/blanda),
   igual que `doctrina` en legal-demo. El validador lo acepta y CONSOLIDATE le
   aplica el delta del tipo estándar inferior, tal como manda el gen. Lo dejo
   dicho para que nadie lo descubra como sorpresa.

## Sobre la verificación normativa (frontera importante)

Las normas se verificaron el **2026-07-27** contra fuentes públicas: el
Gestor Normativo de Función Pública, SUIN-Juriscol, el articulado en
Secretaría del Senado y material derivado de la guía metodológica del DNP.
Lo que eso **sí** sostiene: que las normas citadas existen, con ese número y
año, y que establecen lo que el blueprint dice que establecen.

Lo que **no** sostiene, y conviene decirlo antes de que alguien lo use en una
alcaldía real:

- **No hice un estudio de vigencia exhaustivo.** No verifiqué si reformas
  posteriores (p. ej. la Ley 2197 de 2022) modifican alguno de los artículos
  citados, ni revisé sentencias de constitucionalidad. Un PISCC real exige
  ese chequeo con abogado, y es precisamente lo que `gen-vigencia-normativa`
  del blueprint legal automatizaría si se combinaran.
- **No pude leer la guía del DNP en su fuente.** El PDF de
  `osc.dnp.gov.co/guia_total.pdf` excede el límite de descarga y el de
  `colaboracion.dnp.gov.co` no se pudo extraer como texto. Lo referente a
  línea base, indicadores y focalización viene de fuentes derivadas, no del
  documento original. Antes de usar esto en producción: leer la guía.

## Qué NO cubre lo mecánico

- **La herramienta instala los genes; no los cumple.** Que una cifra llegue
  con `fuente`, `periodo` y `fecha_corte` es trabajo del agente al ingerir,
  bajo `gen-dato-con-corte`. `onboard apply` solo garantiza que la regla esté
  sembrada, versionada y registrada en el ledger.
- **Municipio ficticio, cero datos ingeridos.** Peñas Blancas no existe y no
  hay un solo boletín estadístico en este caso. Este artefacto prueba
  **estructura** (Fase 0/1 del roadmap): mismo manifiesto → mismo genoma.
- **No es el piloto.** B-01…B-06 —corpus real de 50–200 documentos, 20
  preguntas doradas, medición de idempotencia y recall— sigue pendiente. Este
  caso **no** lo sustituye y no marca la Fase B como cumplida.

## Regeneración de la salida esperada (2026-07-29)

`taxonomia.txt` se regeneró porque la ENTRADA cambió: `company.yaml` ganó la carpeta
`wiki/semantic/sintesis`. El motivo viene del aviso que introdujo `gen-onboard` v6
(F0-11): este manifiesto declaraba `sintesis_umbral: 3` —con el comentario "3 hechos del
mismo tipo en el mismo territorio ya es un patrón que mirar"— y no tenía dónde poner esas
síntesis. El hueco estaba en **9 de los 10 manifiestos** del repo, así que no fue un
descuido de este caso.

**El `state-hash` NO cambió**: el genoma resultante es byte-idéntico y solo crece la
taxonomía de `wiki/`. Regenerado con la herramienta, como manda `worked/README.md`.
