# Review honesto — agencia-demo

## Qué salió bien

- **Reproducibilidad real**: la corrida produce los mismos bytes en Windows y
  Linux (CI corre ambos). El hash del genoma coincide corrida tras corrida.
- **Idempotencia probada**: re-aplicar el mismo manifiesto = 0 acciones, 0
  eventos nuevos. No es prosa, es un assert.
- **El blueprint sobrevivió intacto**: no hubo que tocar nada del blueprint
  de agencia para mecanizarlo — la estructura que Jhon destiló de la
  simulación era ya aplicable por máquina.

## Qué falló durante la construcción (y cómo se resolvió)

1. **El validador rechazó al blueprint, no al revés.** La primera versión del
   validador de manifiestos asumió que `seed_genes[].target_tier` solo podía
   ser `semantic|procedural`. Este blueprint declara `gen-accionables` con
   `target_tier: working` — decisión correcta (los accionables son memoria
   corta) que obligó a corregir el validador, no el blueprint
   (`tools/cerebro_core/manifest.py`). Lección: el corpus manda.
2. **Los bloques `>` del YAML.** Las reglas largas de otros blueprints usan
   *folded scalars* que el parser inicial rechazaba; hubo que ampliarlo
   (`miniyaml.py`). Sin casos worked esto habría explotado en manos del
   primer usuario real.

## Qué NO cubre lo mecánico (frontera honesta)

- **La entrevista**: generar este `company.yaml` desde una conversación con
  el fundador sigue siendo juicio del agente. Aquí partió de un blueprint.
- **Las recomendaciones**: gen-visualizacion pide que ONBOARD *recomiende*
  vistas según el perfil (pipeline de leads para una agencia). Eso es
  juicio; la herramienta no lo intenta.
- **`graph_lens.backend` vacío con lente activa**: la herramienta ABORTA con
  error en vez de preguntar — preguntar es del agente (gen-graph-lens:
  se pregunta UNA vez y se registra). El error ruidoso es el comportamiento
  correcto del núcleo mecánico.
- **Contenido**: cero ingesta. Este caso valida estructura (Fase 0), no el
  ciclo de conocimiento con datos reales (Fase B del backlog, pendiente).
