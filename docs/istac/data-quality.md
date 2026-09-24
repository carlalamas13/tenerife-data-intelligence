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

### 4.3. Valores no publicados (sin código)

Existen 148.520 filas con `OBS_VALUE` ausente que no tienen código de estado ni de confidencialidad.

Todas ellas corresponden exclusivamente a las nacionalidades `CH`, `IE`, `IT`, `NO` y `PL`:

| Granularidad | Años sin publicar |
|---|---|
| Mensual | 2009–2020 |
| Anual | 2009–2020, 2023 y 2024 |

Además:

- Afectan por igual a las 4 medidas.
- Afectan por igual a todos los territorios (3.160 filas por territorio).
- Nunca afectan a `NACIONALIDAD_CODE = _T`.

Por tanto, no son valores perdidos aleatorios: son combinaciones que ISTAC no publicaba con ese desglose. Durante esos periodos, los viajeros de estas nacionalidades están incluidos en `5000_XES_O` ("Otros países o territorios del mundo"), como confirma la validación de la jerarquía de nacionalidades (apartado 7.2).

En el proyecto, estas observaciones se clasifican como `not_published`.

### 4.4. Clasificación resultante

Cada observación queda clasificada en una de estas categorías, que son excluyentes:

| Estado | Criterio | Filas |
|---|---|---:|
| `observed` | `OBS_VALUE` informado | 486.026 |
| `not_published` | `OBS_VALUE` ausente sin códigos | 148.520 |
| `not_available` | `ESTADO_OBSERVACION_CODE = O` | 48.091 |
| `confidential` | `CONFIDENCIALIDAD_OBSERVACION_CODE = C` | 3.187 |

No existe ninguna fila con `OBS_VALUE` informado que tenga a la vez un código de estado o de confidencialidad, ni ninguna fila con ambos códigos.

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

### 7.2. Jerarquía de nacionalidades

Se ha validado sobre observaciones mensuales de `PERNOCTACIONES` y `VIAJEROS_ENTRADOS`:

| Relación | Comprobaciones | Diferencia máxima |
|---|---:|---:|
| `_T = ES + 5000_XES` | 19.397 | 0 |
| `5000_XES = países + 5000_XES_O` | 18.976 | 0 |

Los países son `BE`, `CH`, `DE`, `DK`, `FR`, `GB`, `IE`, `IT`, `NL`, `NO`, `PL` y `SE`. Los países no publicados en un periodo se han tratado como incluidos en `5000_XES_O`.

Consecuencia: `5000_XES_O` presenta una **ruptura de serie en 2021**, ya que a partir de ese año deja de incluir `CH`, `IE`, `IT`, `NO` y `PL`. No es comparable antes y después de 2021.

### 7.3. Jerarquía territorial de Tenerife

El cubo solo publica **9 de los 31 municipios de Tenerife**. El resto de la isla se agrega en `ES709_O` ("Resto de Tenerife"):

| Código | Municipio |
|---|---|
| `38001` | Adeje |
| `38006` | Arona |
| `38017` | Granadilla de Abona |
| `38019` | Guía de Isora |
| `38023` | San Cristóbal de La Laguna |
| `38028` | Puerto de la Cruz |
| `38035` | San Miguel de Abona |
| `38038` | Santa Cruz de Tenerife |
| `38040` | Santiago del Teide |

Se ha validado `ES709 = 9 municipios + ES709_O` en 414 observaciones mensuales completas (`_T`, `PERNOCTACIONES` y `VIAJEROS_ENTRADOS`), con diferencia máxima 0.

### 7.4. Observaciones anuales frente a suma de meses

Se han comparado las observaciones anuales con la suma de sus 12 meses cuando los 12 están informados:

| Medida | Comprobaciones | Discrepancias |
|---|---:|---:|
| `PERNOCTACIONES` | 7.432 | 92 |
| `VIAJEROS_ENTRADOS` | 7.352 | 89 |
| `VIAJEROS_ALOJADOS` | 7.432 | 7.394 |

Interpretación:

- `VIAJEROS_ALOJADOS` **no es aditiva en el tiempo**: el valor anual es habitualmente inferior a la suma mensual (mediana ≈ -14%). Un viajero cuya estancia abarca dos meses cuenta en ambos meses, pero solo una vez en el año. No debe agregarse sumando meses.
- En `PERNOCTACIONES` y `VIAJEROS_ENTRADOS` las discrepancias se concentran en:
  - `5000_XES_O` en 2023 y 2024: los anuales vuelven a incluir `CH`, `IE`, `IT`, `NO` y `PL`, que en esos años no se publican en anual, pero sí en mensual.
  - `_T` y `ES` en 2024, en 5 territorios, con diferencias pequeñas (decenas o centenas), probablemente revisiones de los datos mensuales no trasladadas al anual.

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
7. Cada observación debe conservar su estado: `observed`,
   `not_published`, `not_available` o `confidential`.
8. Las observaciones anuales no se utilizan en el modelo. Los totales
   anuales se calculan a partir de los mensuales.
9. `VIAJEROS_ALOJADOS` no debe sumarse entre meses.
10. `ESTANCIA_MEDIA` no debe sumarse ni promediarse: se recalcula como
    `PERNOCTACIONES / VIAJEROS_ENTRADOS` tras agregar.
11. Los niveles agregados (`ES70`, islas, `_T`, `5000_XES`) no deben
    sumarse junto con sus componentes para evitar dobles conteos.
12. `ES709_O` se trata como un territorio residual, no como un
    municipio.
13. `5000_XES_O` no es comparable antes y después de 2021.

## 9. Decisiones pendientes

- Confirmar con la metadata oficial de ISTAC el cambio de desglose de
  nacionalidades en 2021.
- Confirmar el origen de las pequeñas discrepancias anual/mensual de
  2024.
- Evaluar si existe otra fuente oficial con los 31 municipios de
  Tenerife (probablemente no, por secreto estadístico).
- La metadata oficial completa del dataset.
- Las definiciones oficiales de las dimensiones y medidas utilizadas.