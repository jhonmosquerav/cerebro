---
title: Perfil de la empresa
type: meta
status: configurado
updated: 2026-07-12
---

# Perfil de la empresa

> Generado mecánicamente por ONBOARD desde `onboard/company.yaml` el 2026-07-12.
> Mismo manifiesto → mismo perfil. No editar a mano: re-corre ONBOARD.

## Identidad
- Nombre: **Bufete Río de Oro**
- Sector / industria: bufete legal — litigio civil y mercantil
- Idioma principal: es
- Sitio / dominios: riodeoro.legal

## Conocimiento que maneja
- Tipos de documento: contrato, escrito-de-caso, jurisprudencia, normativa, dictamen, minuta-cliente
- Entidades clave: clientes (0 declaradas) · casos (0 declaradas) · contrapartes (0 declaradas) · juzgados (0 declaradas) · abogados (0 declaradas)
- Glosario / siglas internas:
  - **EXP**: número de expediente interno del caso
  - **SP**: secreto profesional / información amparada por confidencialidad abogado-cliente
  - **cláusula-tipo**: cláusula contractual reutilizable de la biblioteca interna
  - **contraparte**: parte adversa en un litigio o negociación
  - **dictamen**: opinión jurídica formal emitida por el bufete
  - **jurisprudencia**: doctrina sentada por sentencias que sirve de precedente

## Roles y equipo
- Roles que consultan/alimentan: socios, asociados, paralegales
- Aprueba mutaciones del genoma: socio-director

## Configuración sembrada
- Verbos de dominio (`relation_types`): cita, se_apoya_en, fundamenta, instancia, deroga
- Sensibilidad por defecto: `confidencial`
- Confianza por fuente (`source_trust`): blanda 0.4, doctrina 0.6, interna 0.7, oficial 0.9
- Umbrales: síntesis 3 · hub 7
- Genes de sector sembrados: [[gen-vigencia-normativa]], [[gen-conflicto-interes]], [[gen-version-clausula]]
- Lente de grafo: deshabilitada
