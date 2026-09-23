# Calidad y validación de datos ISTAC

## 1. Objetivo

Este documento recoge las comprobaciones de calidad realizadas sobre los datos procedentes de ISTAC antes de aplicar transformaciones o construir las capas procesadas del proyecto.

El objetivo es conocer la estructura del dato, identificar valores ausentes, detectar patrones de ausencia y validar relaciones entre variables antes de definir reglas de transformación.

## 2. Dataset analizado

- Código ISTAC: `C00065A_000036`
- Fuente: ISTAC
- Fichero analizado: `dataset.csv`
- Última versión analizada: `2026-09-23`

## 3. Estructura del dato

El dataset contiene:

- 685.824 filas
- 16 columnas
- 4 medidas
- 1 categoría de tipo de alojamiento
- Múltiples niveles territoriales
- Múltiples categorías de nacionalidad
- Observaciones mensuales y anuales

Las principales medidas son:

- `VIAJEROS_ENTRADOS`
- `VIAJEROS_ALOJADOS`
- `PERNOCTACIONES`
- `ESTANCIA_MEDIA`

Las principales dimensiones analizadas son:

- `TERRITORIO_CODE`
- `NACIONALIDAD_CODE`
- `ALOJAMIENTO_TURISTICO_TIPO_CODE`
- `TIME_PERIOD_CODE`

## 4. Valores ausentes

El dataset contiene valores ausentes en varias columnas.

Los principales valores ausentes son:

| Columna | Valores ausentes | Porcentaje |
|---|---:|---:|
| `OBS_VALUE` | 199.798 | 29,13% |
| `ESTADO_OBSERVACION_CODE` | 637.733 | 92,99% |
| `CONFIDENCIALIDAD_OBSERVACION_CODE` | 682.637 | 99,54% |
| `NOTAS_OBSERVACION#es` | 685.824 | 100% |

Los valores ausentes de `OBS_VALUE` no deben interpretarse automáticamente como valores cero.

El dataset contiene campos de metadatos que permiten identificar determinados tipos de ausencia.

### 4.1. Estado de la observación

El valor:

`ESTADO_OBSERVACION_CODE = O`

corresponde a "Valor no disponible" en la clasificación de estado de observación utilizada por ISTAC.

En el dataset analizado:

- 48.091 filas tienen `ESTADO_OBSERVACION_CODE = O`.
- Todas estas filas tienen `OBS_VALUE` ausente.

Por tanto, estas observaciones deben mantenerse como valores ausentes y no deben convertirse en cero.

### 4.2. Observaciones confidenciales

El valor:

`CONFIDENCIALIDAD_OBSERVACION_CODE = C`

corresponde a "Información estadística confidencial".

En el dataset analizado:

- 3.187 filas tienen `CONFIDENCIALIDAD_OBSERVACION_CODE = C`.
- Todas estas filas tienen `OBS_VALUE` ausente.

Estas observaciones deben mantenerse como valores ausentes y no deben convertirse en cero.

## 5. Cobertura temporal

El dataset contiene observaciones desde 2009 hasta 2026.

El número de filas por año se mantiene estable en 39.104 desde 2009 hasta 2025. El año 2026 contiene menos filas porque se trata de un año incompleto.

El porcentaje de filas que contienen un `OBS_VALUE` disponible es:

| Año | Cobertura |
|---|---:|
| 2009 | 62,57% |
| 2010 | 63,79% |
| 2011 | 64,34% |
| 2012 | 64,10% |
| 2013 | 64,05% |
| 2014 | 64,71% |
| 2015 | 64,87% |
| 2016 | 65,05% |
| 2017 | 65,21% |
| 2018 | 64,88% |
| 2019 | 64,68% |
| 2020 | 44,06% |
| 2021 | 85,37% |
| 2022 | 89,92% |
| 2023 | 87,47% |
| 2024 | 88,71% |
| 2025 | 90,49% |
| 2026 | 90,32% |

La reducción de la cobertura en 2020 y el posterior incremento a partir de 2021 representan un patrón temporal relevante que debe conservarse durante el análisis.

La cobertura de 2026 debe interpretarse teniendo en cuenta que el año todavía está incompleto.

## 6. Patrones de ausencia

Los valores ausentes presentan patrones estructurados y no se distribuyen de forma uniforme por todo el dataset.

Un patrón especialmente relevante aparece en la dimensión de nacionalidad.

Las siguientes categorías de nacionalidad no presentan observaciones con valores antes de 2021 y comienzan a presentar observaciones a partir de 2021:

- `CH`
- `IE`
- `IT`
- `NO`
- `PL`

A partir de 2021 presentan observaciones con una cobertura significativa.

Estas ausencias anteriores a 2021 no deben interpretarse como valores cero.

Hasta confirmar su significado mediante los metadatos correspondientes de ISTAC, estas observaciones se tratarán como datos ausentes y no se aplicará ninguna imputación.

## 7. Validaciones realizadas

### 7.1. ESTANCIA_MEDIA

Se ha validado la relación entre las siguientes medidas:

`ESTANCIA_MEDIA = PERNOCTACIONES / VIAJEROS_ENTRADOS`

La validación se realizó para:

- `TERRITORIO_CODE = ES709`
- `NACIONALIDAD_CODE = _T`
- `ALOJAMIENTO_TURISTICO_TIPO_CODE = _T`
- Observaciones mensuales

Resultados:

- Observaciones válidas: 210
- Diferencia absoluta máxima: `4.9387161027425464e-11`
- Tolerancia utilizada: `1e-9`
- Observaciones fuera de tolerancia: 0

Los valores publicados de `ESTANCIA_MEDIA` son, por tanto, consistentes
con la relación:

`PERNOCTACIONES / VIAJEROS_ENTRADOS`

Las pequeñas diferencias detectadas se consideran atribuibles a la
precisión de los números en coma flotante.

## 8. Reglas de transformación

A partir de las comprobaciones realizadas se establecen las siguientes
reglas:

1. Los valores ausentes de `OBS_VALUE` no deben sustituirse
   automáticamente por cero.
2. Las observaciones con `ESTADO_OBSERVACION_CODE = O` deben mantenerse
   como valores ausentes.
3. Las observaciones con `CONFIDENCIALIDAD_OBSERVACION_CODE = C` deben
   mantenerse como valores ausentes.
4. Las nacionalidades que no presentan observaciones antes de 2021 no
   deben convertirse a cero para esos años.
5. El periodo correspondiente a 2026 no debe tratarse como un año
   completo.
6. `ESTANCIA_MEDIA` puede validarse mediante la relación:
   `PERNOCTACIONES / VIAJEROS_ENTRADOS`.

## 9. Decisiones pendientes

Antes de definir nuevas reglas de transformación, es necesario
investigar:

- El significado de las observaciones donde `OBS_VALUE` es ausente pero
  tanto el estado de observación como el estado de confidencialidad son
  nulos.
- El significado de todas las categorías de `NACIONALIDAD_CODE`.
- La razón por la que `CH`, `IE`, `IT`, `NO` y `PL` comienzan a presentar
  observaciones a partir de 2021.
- La metadata oficial completa del dataset.
- Las definiciones oficiales de las dimensiones y medidas utilizadas.