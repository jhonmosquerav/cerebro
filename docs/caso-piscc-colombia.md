# Un plan de seguridad que no acepta cifras sin fecha: el caso colombiano de CEREBRO

**Publicado el 2026-10-23.** Cierra la Fase 4 del roadmap (distribución). CEREBRO es una
base de conocimiento hecha de archivos de texto, que un agente de IA mantiene bajo reglas
escritas. Este es el caso de su blueprint `seguridad-territorial` y del caso trabajado
`worked/piscc-demo`: el primer sector que no sale de una simulación sino de la ley
colombiana. Lo escribo para quien
formula o audita un plan de seguridad en una alcaldía. También para quien trabaja con datos
públicos en América Latina y sospecha que el problema no es la falta de datos.

## La escena

La llamaré Marcela, y la escena es compuesta: no es una persona real, es la suma de varias
conversaciones con funcionarios de municipios pequeños de Santander. Marcela es secretaria de
gobierno de un municipio de sexta categoría. Su alcalde se posesionó el 1 de enero y la ley le
da seis meses para presentar el PISCC, el Plan Integral de Seguridad y Convivencia Ciudadana
[1][2]. Ese plan es el documento donde el municipio dice qué delitos va a atacar, dónde y con
qué plata.

Marcela tiene un Excel con tres pestañas. Una viene de la Policía, otra de Medicina Legal y la
tercera la armó un practicante con lo que encontró en internet. En la diapositiva del consejo
de seguridad dice que el hurto "viene bajando". Nadie en la sala sabe de qué fecha es el dato,
ni si la cifra es un conteo de casos o una tasa por cada cien mil habitantes. El plan se aprueba
igual. *"Es que si no lo presentamos, nos sancionan"*, me dijo una funcionaria real que no voy a
nombrar.

Ese es el problema que este caso ataca. No la falta de datos. La falta de **reglas sobre qué
cuenta como dato**.

## ¿Qué exige la ley, y por qué eso importa para una base de conocimiento?

El PISCC no es una buena práctica. Es una obligación del alcalde como primera autoridad de
policía del municipio, escrita en el Código Nacional de Seguridad y Convivencia Ciudadana [1].
La plata para ejecutarlo sale en buena parte del FONSET, el fondo de seguridad que cada
municipio y departamento debe tener por ley [3]. Y ese fondo no se gasta a voluntad: el gasto lo
estudia, aprueba y vigila el Comité Territorial de Orden Público, el CTOP, según el decreto que
organiza esos fondos [5]. Cada año, además, el municipio debe informar al Ministerio del
Interior cómo ejecutó el FONSET [4].

Léalo como economista y verá cuatro reglas de datos escondidas en cuatro normas:

1. Una cifra de seguridad solo sirve si trae fuente, periodo y fecha de corte. Sin eso no se
   puede comparar con el año anterior ni con el municipio vecino.
2. Una intervención sin unidad territorial (comuna, barrio, cuadrante) no se puede focalizar,
   y el PISCC se evalúa justamente por focalización.
3. Un objetivo sin línea base, indicador y meta no es un objetivo. Es una intención.
4. Un gasto del FONSET sin acta del CTOP que lo respalde no está justificado, aunque la plata
   ya se haya girado.

Ninguna de las cuatro es opinión mía. Son consecuencias directas de las normas, que verificamos
en fuente primaria el 27 de julio de 2026 contra el Gestor Normativo de Función Pública,
SUIN-Juriscol y la Secretaría del Senado [1][3][4][5]. La guía metodológica del DNP, el
Departamento Nacional de Planeación, pide lo mismo desde el lado técnico: diagnóstico con línea
base, indicadores, metas y focalización [6][7].

## ¿Qué hace distinto a CEREBRO aquí?

CEREBRO es una base de conocimiento hecha solo de archivos de texto, que un agente de
inteligencia artificial lee y mantiene bajo reglas escritas, los *genes*. No tiene servidor
ni base de datos: una alcaldía la clona en una carpeta y la opera con el agente que ya use.

Lo normal sería escribir las cuatro reglas en un manual de buenas prácticas y confiar en que
alguien las lea. Aquí se hizo otra cosa: cada regla es un gen que el agente debe cumplir cada
vez que ingiere un documento o responde una pregunta. El blueprint `seguridad-territorial`
siembra cuatro:

| Regla de la ley | Gen | Qué hace el agente |
|---|---|---|
| Cifra con fuente, periodo y corte | `gen-dato-con-corte` | Una cifra sin esos tres campos no entra como dato. Prohíbe mezclar SIEDCO (el sistema estadístico de la Policía) con Medicina Legal en una misma serie. |
| Sin territorio no hay focalización | `gen-territorializacion` | Toda intervención queda ligada a una unidad territorial o se marca como no focalizada. |
| Objetivo con línea base y meta | `gen-linea-base-y-meta` | Un objetivo sin línea base, indicador, meta y fuente se marca como *intención*, no como objetivo. |
| Gasto del FONSET con acta del CTOP | `gen-trazabilidad-fonset` | Un gasto sin acta queda en estado `sin-respaldo` y el agente lo advierte siempre que alguien pregunte por él. |

El blueprint también declara los verbos del sector: *reglamenta*, *financia*, *mide*,
*focaliza_en*, *reporta_a*. Sin ellos, la relación entre una norma, un fondo y un indicador
se aplasta en un genérico "usa", y ahí se pierde justo lo que hace auditable un PISCC.

Y toma una decisión que va al revés que en el blueprint del sector legal: la sensibilidad por
defecto es `interno`, no `confidencial`. El PISCC es un documento público y la rendición de
cuentas es parte del mandato. Lo reservado, como víctimas identificables o información de
inteligencia, se marca página por página. Sembrar todo como confidencial habría sido más cómodo
y habría contradicho el deber de publicidad.

## ¿Qué se probó de verdad, con fecha?

Aquí es donde un caso deja de ser un folleto. Esto es lo que se ejecutó y se puede repetir:

- **27 de julio de 2026.** Nació el blueprint y el caso `worked/piscc-demo`, con un municipio
  ficticio, Peñas Blancas, para no inventar datos de uno real. La primera corrida **abortó**: el
  manifiesto traía dos listas partidas en dos líneas, que es YAML válido pero no el subconjunto
  estricto que CEREBRO acepta. La herramienta no escribió ni un archivo a medias. Esa garantía
  estaba en los tests; ese día se vio en vivo.
- **Mismo manifiesto, mismo genoma.** Aplicar el blueprint produce 22 acciones (perfil, 13
  carpetas, 4 genes sembrados, 4 líneas en el libro de eventos) y un hash de estado que la
  integración continua regenera byte a byte en Linux y Windows [8]. Si alguien cambia una coma
  del resultado, el test falla.
- **23 de octubre de 2026.** El blueprint entró al catálogo con versión `1.0.0` y requisito
  mínimo de herramientas `0.1.0`. Un municipio que lo use sabrá de qué versión nació su
  configuración y si hay una más nueva [9].

Lo que **no** se probó, dicho sin maquillaje:

- No hay un solo boletín estadístico ingerido. El caso demuestra estructura, no operación con
  datos reales. Para eso hace falta un piloto con una secretaría de gobierno de verdad.
- La verificación normativa confirmó que las normas existen y dicen lo que el blueprint dice.
  **No** incluyó un estudio de vigencia exhaustivo: no revisé si reformas posteriores a 2016
  modificaron los artículos citados, ni sentencias de constitucionalidad. Un PISCC real exige
  ese chequeo con abogado.
- La guía del DNP no pude leerla en su fuente: el PDF original no se dejó extraer. Lo que el
  blueprint dice sobre línea base e indicadores viene de fuentes derivadas de esa guía [6][7].
  Antes de usarlo en una alcaldía, lea la guía.

## ¿Qué cambia para un municipio como el de Marcela?

Volvamos al Excel de tres pestañas. Con el blueprint aplicado, el agente que ingiere la pestaña
de la Policía no puede guardar "el hurto viene bajando". Tiene que guardar la fuente (SIEDCO),
el periodo (enero a mayo), la fecha de corte y la unidad (casos o tasa). Si falta uno, la
página queda marcada y la pregunta "¿cómo va el hurto?" recibe la cifra **y la advertencia**.
Cuando alguien proponga comparar la serie de la Policía con la de Medicina Legal, el gen lo
impide y explica por qué: miden cosas distintas.

El costo de esto para un municipio de sexta categoría es cercano a cero. Es una carpeta, un
Python que ya viene en cualquier computador y el mismo agente de inteligencia artificial que la
secretaría probablemente ya usa para redactar oficios. No hay licencia ni servidor. La
capacitación que recibieron los 116 secretarios de gobierno de Cundinamarca en 2024, con el
DNP y los ministerios de Justicia e Interior [10], podría incluir un blueprint así. Como
material de trabajo, no como diapositiva.

La implicación social está en quién puede auditar. Hoy, verificar si un PISCC tiene línea base
o si un gasto del FONSET tiene acta exige leer cientos de páginas y saber dónde buscar. Con las
reglas convertidas en genes, una veeduría ciudadana, un concejal o un periodista local pueden
preguntarle al mismo agente "¿qué gastos del FONSET están sin respaldo?". Y reciben la lista
con su fuente. La transparencia deja de depender de quién tenga tiempo de leer.

Marcela sigue teniendo seis meses y tres pestañas. La pregunta para ella, y para usted si
trabaja con datos públicos, ya no es "¿qué sistema compro?". Es otra: *¿qué regla sobre sus
datos está dispuesta a convertir en una condición que nadie, ni usted, pueda saltarse?*

## Referencias

Verificación normativa en fuente primaria: 2026-07-27 (ver `worked/piscc-demo/review.md`,
que declara qué se comprobó y qué no).

1. Ley 1801 de 2016 (Código Nacional de Seguridad y Convivencia Ciudadana), art. 205 num. 4 —
   el alcalde elabora y ejecuta el PISCC. Secretaría del Senado:
   http://www.secretariasenado.gov.co/senado/basedoc/ley_1801_2016.html
2. Plazo de seis meses para que los mandatarios entrantes presenten su PISCC. El Espectador,
   "PISCC: guía para que nuevos alcaldes y gobernadores construyan sus planes de seguridad":
   https://www.elespectador.com/colombia-20/paz-y-memoria/piscc-guia-para-que-nuevos-alcaldes-y-gobernadores-construyan-sus-planes-de-seguridad-dnp/
3. Ley 418 de 1997, art. 119 (modificado por las leyes 548/1999, 782/2002, 1106/2006 y
   1421/2010) — creación del FONSET en municipios y departamentos. Secretaría del Senado:
   http://www.secretariasenado.gov.co/senado/basedoc/ley_0418_1997.html
4. Ley 1421 de 2010, art. 8 — informe anual de ejecución del FONSET al Ministerio del Interior.
   Secretaría del Senado: http://www.secretariasenado.gov.co/senado/basedoc/ley_1421_2010.html
5. Decreto 399 de 2011 — organización y funcionamiento de FONSECON y FONSET; funciones del
   Comité Territorial de Orden Público. Gestor Normativo, Función Pública (consultado 2026-07-27).
6. DNP, comunicado del 11 de diciembre de 2023: nueva Guía Metodológica para la Formulación,
   Implementación, Seguimiento y Evaluación de los PISCC:
   https://www.ambitojuridico.com/sites/default/files/2023-12/COMUNICADO-DNP-pone-a-disposicion-2023.pdf
7. DNP, noticia sobre la actualización de la guía metodológica de los PISCC:
   https://www.dnp.gov.co/Prensa_/Noticias/Paginas/en-el-marco-de-la-actualizacion-de-la-guia-metodologica-de-los-planes-integrales-de-seguridad-y-convivencia-ciudadana.aspx
8. Caso trabajado reproducible: `worked/piscc-demo/corrida.md` (comandos exactos, salida
   esperada, hash de estado) y `tests/test_worked.py` (verificación byte a byte en CI).
9. Catálogo de blueprints con versiones y requisito mínimo: `onboard/blueprints/catalog.yaml`
   y `python tools/cerebro.py blueprints` (Fase 4.3, 2026-10-23).
10. Gobernación de Cundinamarca, 2024: "Secretarios de Gobierno de los 116 municipios
    recibieron capacitación para formular los PISCC":
    https://www.cundinamarca.gov.co/noticias/SECRETARIOS%20DE%20GOBIERNO%20SE%20CAPACITARON%20EN%20PISCC
