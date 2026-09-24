# Fuentes de datos

## ISTAC — Encuesta de Alojamiento Turístico

- Organización: Instituto Canario de Estadística (ISTAC)
- Operación: `C00065A`
- Cubo inicial: `C00065A_000036`
- Recurso: CSV vía API e-Cubos
- Cobertura: datos mensuales y anuales desde 2009
- Nivel territorial: islas y municipios
- Uso en el proyecto: viajeros alojados, viajeros entrados, pernoctaciones y estancia media por municipio, periodo y nacionalidad

URL base configurada en `.env.example`. La versión actual del recurso es `2.17`.

**Limitación:** para Tenerife solo se publican 9 de los 31 municipios. El resto se agrega en `ES709_O` ("Resto de Tenerife"). El análisis municipal del proyecto se limita a esos 9 municipios más el territorio residual. Ver `docs/istac/dataset-c00065a-000036.md`.

## Fuente complementaria Cabildo

El portal de Datos Abiertos de Tenerife publica, entre otros, el conjunto "Número de turistas alojados en Tenerife por municipios". Actualmente cubre Adeje, Arona, Puerto de la Cruz y Santa Cruz de Tenerife, por lo que se utilizará como fuente complementaria y para reconciliación, no como fuente turística única.

## ISTAC — capacidad y ocupación

- Cubo: `C00065A_000001`
- Uso: establecimientos abiertos, plazas, habitaciones ofertadas y tasas de ocupación
- Se incorporará en una segunda ingesta para complementar la demanda turística.
