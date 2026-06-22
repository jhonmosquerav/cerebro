---
id: gen-sintesis-de-volumen
trigger: acumulación de eventos del mismo tipo con clave común
status: active
version: 1
---

Cuando ≥ N páginas `clase: evento` ([[gen-clase-temporal]]) comparten una clave (mismo
SKU+motivo, misma máquina+falla, mismo cliente+objeción), CONSOLIDATE crea o actualiza una
página `type: sintesis` (`decay_rate: low`) que las **agrega** (relación `agrega`) y destila
el patrón. N es configurable por empresa en `onboard/company.yaml` (`sintesis_umbral`, default 3).
Si el patrón señala riesgo (defecto sistémico, objeción recurrente que tumba ventas), la
síntesis **deriva a [[gen-evolve]]** para proponer una mutación o acción. Así, señales que
sueltas serían invisibles se vuelven conocimiento accionable.
