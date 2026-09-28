# Modelo de datos analítico

## 1. Objetivo

Este documento define la arquitectura del modelo analítico del proyecto Tenerife Data Intelligence.

El modelo separa las capas de ingesta, transformación y consumo para mantener la trazabilidad de las fuentes y facilitar el análisis turístico de Tenerife.

La arquitectura se diseña inicialmente a partir del dataset ISTAC `C00065A_000036`, pero debe permitir incorporar posteriormente otras fuentes, como los datos del Cabildo de Tenerife.

## 2. Arquitectura de capas

El flujo general del dato será:

```text
Fuentes
  ↓
RAW
  ↓
STAGING
  ↓
INTERMEDIATE
  ↓
MODELO ANALÍTICO
  ↓
CONSUMO
```

Para ISTAC:

```text
raw.istac_c00065a_000036
        ↓
stg_istac_tourism
        ↓
int_istac_tourism_monthly
        ↓
dim_date
dim_territory
dim_nationality
dim_accommodation
        ↓
fct_tourism
```

## 3. Responsabilidad de cada capa

### 3.1. RAW

Conserva los datos de la fuente y la información necesaria para identificar cada snapshot.

No aplica transformaciones de negocio.

### 3.2. STAGING

Normaliza nombres, tipos y atributos básicos de la fuente.

Mantiene la estructura de las observaciones y conserva las granularidades disponibles en ISTAC.

### 3.3. INTERMEDIATE

Aplica transformaciones orientadas al negocio que todavía no pertenecen al modelo dimensional final.

En la primera implementación se utilizará para:

* seleccionar las observaciones mensuales;
* pivotar las medidas de ISTAC a una estructura analítica;
* preparar las métricas turísticas;
* conservar la trazabilidad respecto al snapshot activo.

### 3.4. MODELO ANALÍTICO

Está formado por dimensiones y tablas de hechos diseñadas para análisis y consumo.

## 4. Grano del hecho

La tabla `fct_tourism` tendrá una fila por combinación de:

* periodo mensual;
* territorio;
* nacionalidad;
* tipo de alojamiento.

La granularidad temporal será mensual.

La clave natural conceptual será:

```text
period
+ territory
+ nationality
+ accommodation_type
```

Las cuatro medidas de ISTAC se almacenarán como columnas del hecho.

## 5. Dimensiones

### 5.1. `dim_date`

Representa el periodo temporal utilizado por el modelo.

El hecho turístico será mensual y utilizará como referencia la fecha de inicio del mes.

Atributos previstos:

* `date_key`
* `date`
* `year`
* `month`
* `month_number`
* `month_name`
* `quarter`
* `year_month`

La dimensión se diseñará de forma que pueda reutilizarse posteriormente con otras fuentes y modelos.

### 5.2. `dim_territory`

Representa los territorios geográficos publicados por las fuentes.

Se utilizará como dimensión general porque las fuentes pueden contener diferentes niveles territoriales.

Atributos previstos:

* `territory_key`
* `territory_code`
* `territory_name`
* `territory_level`
* `parent_territory_code`

Los códigos oficiales de ISTAC se conservarán.

Los territorios agregados y residuales no se tratarán como municipios.

En particular, `ES709_O` se conservará como territorio residual de Tenerife.

La creación de una dimensión específica de municipios podrá realizarse posteriormente a partir de una fuente de referencia territorial independiente.

### 5.3. `dim_nationality`

Representa la nacionalidad del viajero.

Atributos previstos:

* `nationality_key`
* `nationality_code`
* `nationality_name`
* `parent_nationality_code`

Se conservarán las jerarquías publicadas por ISTAC.

La ruptura de serie de `5000_XES_O` alrededor de 2021 deberá mantenerse como una característica de los datos y no se corregirá mediante una recodificación artificial.

### 5.4. `dim_accommodation`

Representa el tipo de alojamiento turístico.

Atributos previstos:

* `accommodation_key`
* `accommodation_type_code`
* `accommodation_type_name`

Actualmente el dataset `C00065A_000036` solo publica `_T`, por lo que la dimensión tendrá inicialmente una única categoría procedente de esta fuente.

La estructura se mantiene para permitir incorporar posteriormente otras categorías o fuentes.

## 6. `fct_tourism`

La tabla de hechos contendrá las principales métricas turísticas.

### Claves

* `date_key`
* `territory_key`
* `nationality_key`
* `accommodation_key`

### Medidas

* `travelers_entered`
* `travelers_hosted`
* `overnights`
* `average_stay`

## 7. Reglas de las medidas

### `travelers_entered`

Representa los viajeros entrados.

Puede agregarse según las dimensiones permitidas por el modelo.

### `travelers_hosted`

Representa los viajeros alojados.

No debe sumarse entre meses para obtener totales anuales, ya que una misma persona puede aparecer en varios meses de una estancia.

### `overnights`

Representa las pernoctaciones.

Es una medida aditiva en el tiempo bajo las reglas definidas para el proyecto.

### `average_stay`

Representa la estancia media.

No debe sumarse ni promediarse directamente.

Cuando sea necesario agregar datos, se calculará como:

```text
overnights / travelers_entered
```

La relación se ha validado previamente sobre los datos publicados por ISTAC.

## 8. Tratamiento temporal

El modelo analítico utilizará observaciones mensuales.

Las observaciones anuales publicadas por ISTAC se conservarán en RAW y staging para trazabilidad y validación, pero no formarán parte del hecho mensual principal.

Los totales anuales requeridos por el modelo se calcularán posteriormente a partir de los datos mensuales cuando la naturaleza de la medida lo permita.

## 9. Jerarquías territoriales

La dimensión territorial debe distinguir entre:

* comunidad autónoma;
* isla;
* territorio residual;
* municipio;
* otros niveles que puedan aparecer en futuras fuentes.

No se debe sumar simultáneamente un territorio agregado y sus componentes.

Para Tenerife:

```text
ES709
├── municipios publicados
└── ES709_O
```

`ES709_O` representa los municipios no publicados individualmente por ISTAC y no se tratará como un municipio.

## 10. Jerarquías de nacionalidad

La jerarquía se conservará mediante los códigos oficiales.

La relación actualmente validada es:

```text
_T
└── ES
└── 5000_XES
    ├── países publicados
    └── 5000_XES_O
```

La categoría `5000_XES_O` presenta una ruptura de serie relacionada con el cambio de desglose de nacionalidades observado a partir de 2021.

## 11. Surrogate keys

Las dimensiones utilizarán claves sustitutas internas (`*_key`) como identificadores del modelo analítico.

Los códigos oficiales de las fuentes se conservarán como atributos de negocio.

Esto permite integrar posteriormente fuentes con códigos diferentes sin modificar las claves internas del modelo.

## 12. Integración futura de fuentes

El modelo no debe depender exclusivamente de ISTAC.

La incorporación de nuevas fuentes seguirá el flujo:

```text
nueva fuente
    ↓
RAW
    ↓
STAGING
    ↓
INTERMEDIATE
    ↓
dimensiones conformadas / hechos
```

Las dimensiones comunes, especialmente fecha y territorio, podrán utilizarse para integrar datos procedentes de otras fuentes.

La reconciliación entre fuentes se realizará en modelos intermedios o analíticos específicos, no en la capa RAW.

## 13. Alcance inicial

La primera implementación del modelo analítico se limitará a:

* datos turísticos de ISTAC;
* frecuencia mensual;
* las cuatro medidas identificadas;
* territorios publicados por ISTAC;
* nacionalidades publicadas por ISTAC;
* tipo de alojamiento disponible en `C00065A_000036`.

La integración de datos del Cabildo y otras fuentes se realizará posteriormente.

## 14. Principio de trazabilidad

Cada registro analítico debe poder relacionarse con el snapshot de la fuente del que procede mediante la trazabilidad mantenida en las capas RAW, staging e intermediate.

La selección del lote activo se realiza en staging, por lo que las capas posteriores trabajarán sobre un snapshot concreto de la fuente.
