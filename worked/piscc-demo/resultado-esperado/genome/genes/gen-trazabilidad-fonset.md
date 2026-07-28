---
id: gen-trazabilidad-fonset
trigger: "se ingiere o actualiza una acción, proyecto o rubro financiado con FONSET"
status: active
version: 1
---

Toda acción con cargo al FONSET se enlaza con 'financia' a su fuente y con 'reporta_a' al acta del Comité Territorial de Orden Público que aprobó la destinación (Decreto 399 de 2011: el CTOP estudia, aprueba y hace seguimiento a los recursos). Sin acta referenciada la página queda 'estado: sin-respaldo' y QUERY lo advierte SIEMPRE, porque el gasto sin aprobación del comité es un hallazgo de control fiscal, no un detalle administrativo. El informe anual de ejecución al Ministerio del Interior (Ley 1421 de 2010, art. 8) se arma navegando estas relaciones.

> Gen de sector sembrado mecánicamente por ONBOARD desde `onboard/company.yaml` (2026-07-12).
> Mutarlo pasa por [[gen-compuerta-mutacion]] como cualquier gen.
