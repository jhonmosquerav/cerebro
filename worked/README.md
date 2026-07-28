# worked/ — casos trabajados reproducibles

La respuesta a la pregunta incómoda de la evaluación externa: *"un sistema
auditable sin auditoría publicada es una contradicción"*. Cada caso de esta
carpeta es una corrida real de la herramienta mecánica que **cualquier
tercero puede re-correr y verificar byte a byte** — y el CI lo hace en cada
push (`tests/test_worked.py`).

## Contrato de un caso

```
worked/<caso>/
├── company.yaml          # la ENTRADA: manifiesto completo (blueprint + datos)
├── corrida.md            # los comandos exactos para reproducirlo
├── review.md             # revisión HONESTA: qué cubre, qué no, qué falló
└── resultado-esperado/   # la SALIDA esperada, byte a byte
    ├── genome/genes/*.md         # genes de sector sembrados
    ├── genome/company-profile.md # perfil renderizado
    ├── genome/events.jsonl       # 1 línea gene_added por gen, con hash-chain
    ├── taxonomia.txt             # carpetas creadas
    └── state-hash.txt            # hash sha256 del genoma resultante
```

**La fecha es parte de la entrada.** Los casos se generan con
`--date 2026-07-12`; reproducirlos exige la misma fecha (por eso el
determinismo es honesto: no hay reloj escondido).

## Reproducir un caso (5 minutos, cero dependencias)

```bash
git clone <este-repo> cerebro-caso && cd cerebro-caso
cp worked/agencia-demo/company.yaml onboard/company.yaml
python tools/cerebro.py onboard apply --date 2026-07-12
python tools/cerebro.py hash --scope genome
# compara: worked/agencia-demo/resultado-esperado/ y su state-hash.txt
```

> Nota: el hash de `state-hash.txt` corresponde al esqueleto mínimo que usa
> el test (ver `tests/test_worked.py`); sobre un clon completo del template
> los archivos delta (genes, perfil, events) son idénticos byte a byte,
> pero el hash global incluye además los genes base del template.

## Casos disponibles

| Caso | Sector | Genes sembrados | Qué demuestra |
|---|---|---|---|
| `agencia-demo` | agencia de automatización y marketing | gen-accionables, gen-objecion-transversal | onboard con taxonomía amplia (10 carpetas) y gen en tier `working` |
| `legal-demo` | bufete legal | gen-vigencia-normativa, gen-conflicto-interes, gen-version-clausula | onboard en dominio sensible (`default_sensibilidad: confidencial`) |
| `piscc-demo` | seguridad y convivencia ciudadana territorial (Colombia) | gen-dato-con-corte, gen-territorializacion, gen-linea-base-y-meta, gen-trazabilidad-fonset | **caso de dominio propio**: los genes codifican obligaciones legales reales (Ley 1801/2016 art. 205, Decreto 399/2011, Ley 1421/2010), no prácticas opinables |

## Límite declarado (no vender humo)

Estos casos prueban la **estructura** (Fase 0 del roadmap): mismo
manifiesto → mismo genoma, verificado en CI. **No** son el piloto con
datos reales — ingesta de corpus, QUERY con preguntas doradas, medición de
idempotencia sobre 50–200 documentos (Fase B del backlog, B-01…B-06) sigue
pendiente y no se marca cumplido con esto.
