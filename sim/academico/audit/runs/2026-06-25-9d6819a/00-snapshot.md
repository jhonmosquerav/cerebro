---
run_id: "2026-06-25-9d6819a"
fecha: 2026-06-25
git_sha: "9d6819a5a531a466f67f65962ac48a2444aecda3"
git_estado: "dirty — untracked: sim/_auditoria-fixture/audit/runs/2026-06-25-9d6819a/"
gen_auto_auditoria_version: 2
rol: maker
target:
  - sim/academico/genome-applied/
  - sim/academico/wiki/
  - sim/academico/company.yaml
excluido: "sim/academico/audit/runs/ (corridas previas no leídas)"
hoy: 2026-06-25
---

# 00-Snapshot — AUDIT run 2026-06-25-9d6819a (sandbox academico)

## Identidad del estado

| Campo | Valor |
|---|---|
| run_id | 2026-06-25-9d6819a |
| git SHA | 9d6819a5a531a466f67f65962ac48a2444aecda3 |
| árbol | dirty (untracked: sim/_auditoria-fixture/audit/runs/2026-06-25-9d6819a/) |
| gen-auto-auditoria | version 2 |
| fecha auditoría | 2026-06-25 |

## Alcance auditado

### Genome-applied (genes sembrados)
- `genome-applied/gen-cita-trazable.md` — v1, active
- `genome-applied/gen-version-paper.md` — v1, active

### Wiki — páginas ingresadas (14 páginas + índice)

**Papers/preprints (3)**
- `wiki/semantic/papers/wp-2024-07.md` — working-paper, tier:semantic, tags:[supersedido], confidence:0.5
- `wiki/semantic/papers/giea-2025-03.md` — paper-publicado, tier:semantic, confidence:0.9; supersede:[[wp-2024-07]]
- `wiki/semantic/papers/preprint-replica-rios-2023.md` — preprint, tier:semantic, confidence:0.4, tags:[cita-pendiente]; cita:[[metodologia-iva-2016]] (página inexistente)

**Datasets (2)**
- `wiki/semantic/datasets/enph-2022-giea.md` — dataset, tier:semantic, confidence:0.85; cita:[[dane-fuente-oficial]] (página inexistente)
- `wiki/semantic/datasets/enph-2022-v2-giea.md` — dataset, tier:semantic, confidence:0.85; deriva_de:[[enph-2022-giea]]; cita:[[dane-fuente-oficial]] (página inexistente); sin relación `supersede`

**Revisiones (1, confidencial)**
- `wiki/semantic/revisiones/revision-par-giea-2025-03.md` — revision-par, sensibilidad:confidencial, confidence:0.95

**Investigadores (3)**
- `wiki/semantic/investigadores/valentina-rios.md`
- `wiki/semantic/investigadores/carlos-mendoza.md`
- `wiki/semantic/investigadores/sofia-paredes.md`

**Proyectos (1)**
- `wiki/semantic/proyectos/proyecto-fp-044-2023.md` — valido_hasta:2026-12-31 (vigente)

**Índice**
- `wiki/index.md`

### Categorías declaradas en manifiesto vs existentes

| Categoría (taxonomy.semantic) | Carpeta existe | Páginas |
|---|---|---|
| investigadores | sí | 3 |
| papers | sí | 3 |
| datasets | sí | 2 |
| proyectos | sí | 1 |
| revisiones | sí | 1 |
| convenios | no | 0 |

### Relaciones tipadas — resumen de integridad

| Relación | Origen | Destino | ¿Página existe? |
|---|---|---|---|
| cita | enph-2022-giea | [[dane-fuente-oficial]] | NO |
| cita | enph-2022-v2-giea | [[dane-fuente-oficial]] | NO |
| cita | preprint-replica-rios-2023 | [[metodologia-iva-2016]] | NO |
| replica | preprint-replica-rios-2023 | [[metodologia-iva-2016]] | NO |
| supersede | giea-2025-03 | [[wp-2024-07]] | sí |
| deriva_de | enph-2022-v2-giea | [[enph-2022-giea]] | sí |
| revisado_por | giea-2025-03 | [[revision-par-giea-2025-03]] | sí (confidencial) |

### Datos cuantitativos en conflicto potencial

| Página | Campo | Valor |
|---|---|---|
| wp-2024-07 | elasticidad CP | −0.8 |
| giea-2025-03 | elasticidad CP | −0.5 |
| raw/wp-2024-07 | elasticidad CP | −0.8 (fuente original) |

### Confidencialidad

- `revision-par-giea-2025-03.md` — sensibilidad:confidencial. El cuerpo de la página
  transcribe explícitamente la identidad del revisor y su recomendación inicial (campos
  sensibles). Identificado como violación de invariante [[gen-confidencialidad]].
  Referenciado en este documento solo por [[revision-par-giea-2025-03]], campo `sensibilidad`.

## Notas de exclusión

- Corrida previa `sim/academico/audit/runs/2026-06-25-f5c6000/` — NO leída (barrera de rol).
- `sim/academico/findings.md` — no leído (potencial oracle).
- `sim/academico/raw/` — leído solo para contrastar afirmaciones empíricas (permitido).
