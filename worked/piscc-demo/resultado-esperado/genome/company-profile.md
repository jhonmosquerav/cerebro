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
- Nombre: **Alcaldía Municipal de Peñas Blancas**
- Sector / industria: seguridad y convivencia ciudadana territorial — formulación y seguimiento del PISCC
- Idioma principal: es
- Sitio / dominios: penasblancas.gov.co

## Conocimiento que maneja
- Tipos de documento: piscc, acta-comite-orden-publico, acta-consejo-seguridad, boletin-estadistico, norma, encuesta-percepcion, plan-de-desarrollo, informe-fonset, proyecto-inversion
- Entidades clave: unidades-territoriales (0 declaradas) · delitos (0 declaradas) · indicadores (0 declaradas) · fuentes-de-datos (0 declaradas) · actores (0 declaradas) · programas (0 declaradas)
- Glosario / siglas internas:
  - **CTOP**: Comité Territorial de Orden Público — aprueba y hace seguimiento a la destinación del FONSET (Decreto 399/2011)
  - **FONSECON**: Fondo Nacional de Seguridad y Convivencia Ciudadana, del orden nacional
  - **FONSET**: Fondo de Seguridad y Convivencia Ciudadana de la entidad territorial (Ley 418/1997 art. 119)
  - **PISCC**: Plan Integral de Seguridad y Convivencia Ciudadana — instrumento de planeación obligatorio para alcaldes y gobernadores
  - **SIEDCO**: Sistema de Información Estadístico, Delincuencial, Contravencional y Operativo de la Policía Nacional
  - **focalizacion**: priorización de territorio, población o delito sobre la que se concentra la intervención
  - **linea-base**: valor del indicador al inicio del periodo, con fuente y corte explícitos
  - **percepcion**: medición subjetiva de inseguridad por encuesta; no es medida de ocurrencia
  - **tasa**: casos por cada 100.000 habitantes — NO es lo mismo que el conteo absoluto

## Roles y equipo
- Roles que consultan/alimentan: secretaría de gobierno, observatorio del delito, planeación, enlace de policía
- Aprueba mutaciones del genoma: secretario de gobierno

## Configuración sembrada
- Verbos de dominio (`relation_types`): reglamenta, financia, mide, focaliza_en, reporta_a
- Sensibilidad por defecto: `interno`
- Confianza por fuente (`source_trust`): blanda 0.3, interna 0.7, oficial 0.9, percepcion 0.5
- Umbrales: síntesis 3 · hub 7
- Genes de sector sembrados: [[gen-dato-con-corte]], [[gen-territorializacion]], [[gen-linea-base-y-meta]], [[gen-trazabilidad-fonset]]
- Lente de grafo: deshabilitada
