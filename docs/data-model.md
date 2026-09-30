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

La dimensión `dim_date` se genera a partir del rango temporal mensual disponible en `int_istac_tourism_monthly`.

El modelo crea una fila por cada mes comprendido entre el primer y el último `period_start_date` disponible. La clave `date_key` utiliza el formato `YYYYMM`.

La dimensión incluye:

- `date_key`: clave numérica del mes.
- `month_start_date`: primer día del mes.
- `year`: año.
- `quarter`: trimestre.
- `month_number`: número de mes.
- `month_name_es`: nombre del mes en español.
- `year_month`: etiqueta `YYYY-MM`.

La generación dinámica evita mantener manualmente un calendario y permite que la dimensión se adapte a la cobertura temporal disponible en los datos.

Para el snapshot ISTAC actual, la dimensión cubre desde enero de 2009 hasta julio de 2026.

### 5.2. `dim_territory`

### Clasificación territorial

La dimensión `dim_territory` clasifica los 47 territorios publicados por ISTAC en cuatro niveles:

* `region`: Canarias.
* `island`: las 7 islas con información publicada.
* `municipality`: los 35 municipios presentes en el dataset.
* `residual`: territorios agregados identificados por los códigos con sufijo `_O`.

Los territorios residuales `ES705_O`, `ES706_O`, `ES707_O` y `ES709_O` representan respectivamente el resto de Gran Canaria, La Gomera, La Palma y Tenerife. Estos registros no se consideran municipios y se asocian a su correspondiente `island_code`.

La dimensión mantiene además:

* `island_code`: código de la isla a la que pertenece el territorio.
* `island_name_es`: nombre de la isla.
* `is_residual`: indicador booleano de territorio residual.

Esta clasificación se basa exclusivamente en los códigos y nombres territoriales presentes en el snapshot ISTAC `C00065A_000036`, versión `2.17`, y no pretende inferir territorios que no estén publicados por la fuente.


### 5.3. `dim_nationality`

La dimensión `dim_nationality` representa la jerarquía estadística de nacionalidades publicada por ISTAC para el dataset `C00065A_000036`.

La estructura publicada se modela de la siguiente forma:

* `_T`: total de nacionalidades.
* `ES`: España.
* `5000_XES`: Mundo, excluida España.
* códigos de países: desgloses individuales dentro de `5000_XES`.
* `5000_XES_O`: otros países o territorios del mundo, excluida España.

Los códigos `ES` y `5000_XES` se consideran agregados dentro de la jerarquía estadística, ya que son componentes directos de `_T`. Los códigos de países se consideran niveles de detalle de `5000_XES`, mientras que `5000_XES_O` se trata explícitamente como un territorio residual.

La dimensión incorpora:

* `nationality_code`: código publicado por ISTAC.
* `nationality_name_es`: descripción en español.
* `nationality_level`: nivel estadístico (`total`, `aggregate`, `country` o `residual`).
* `parent_nationality_code`: agregado estadístico padre.
* `is_total`: indicador del total.
* `is_residual`: indicador de categoría residual.

La clasificación se basa exclusivamente en los 16 códigos presentes en el snapshot ISTAC analizado y no pretende establecer una jerarquía geopolítica adicional.

Además, la disponibilidad temporal de algunas nacionalidades puede variar. En el snapshot analizado, `CH`, `IE`, `IT`, `NO` y `PL` presentan datos a partir de 2021; su ausencia en periodos anteriores no se interpreta como una ausencia de la nacionalidad en la población, sino como una característica de publicación del conjunto de datos.


### 5.4. `dim_accommodation`

La dimensión `dim_accommodation` representa los tipos de alojamiento turístico publicados por ISTAC.

En el snapshot `C00065A_000036`, versión `2.17`, solo aparece el código `_T`, correspondiente a `Total`. Por este motivo, la dimensión contiene actualmente una única fila.

Se mantiene la dimensión aunque el snapshot actual no publique un desglose por tipos de alojamiento. Esta decisión permite conservar un modelo dimensional estable y preparado para futuras versiones de la fuente en las que puedan aparecer nuevas categorías de alojamiento.

No se introduce ninguna jerarquía adicional, ya que ISTAC no publica niveles de alojamiento adicionales en el snapshot analizado.

## 6. `fct_tourism`

`fct_tourism` constituye la tabla de hechos principal del modelo analítico de turismo.

Su grano es:

`mes + territorio + nacionalidad + tipo de alojamiento`

Cada fila representa una combinación única de estas cuatro dimensiones para un mes determinado.

La fact table se construye a partir de `int_istac_tourism_monthly` y se relaciona con:

* `dim_date`
* `dim_territory`
* `dim_nationality`
* `dim_accommodation`

El modelo conserva todas las filas del modelo intermedio mediante `LEFT JOIN`, evitando perder observaciones por ausencia de correspondencia dimensional.

Las medidas incluidas son:

* `travelers_entered`: viajeros entrados.
* `travelers_hosted`: viajeros alojados.
* `overnights`: pernoctaciones.
* `average_stay`: estancia media.

`average_stay` se calcula como:

`overnights / travelers_entered`

cuando ambas medidas están disponibles y `travelers_entered` es distinto de cero. El resultado se redondea a 10 decimales.

No se convierten valores no publicados, no disponibles o confidenciales en cero. Los valores permanecen como `NULL` y se conserva su correspondiente campo de estado de observación.

Los datos anuales se mantienen en RAW y STAGING, pero no se incorporan a `fct_tourism`, cuyo grano es exclusivamente mensual. Esto evita mezclar distintas granularidades en una misma tabla de hechos.

La fact table se valida mediante tests de unicidad del grano, conservación del número de filas, coherencia de `average_stay` y relaciones con las cuatro dimensiones.

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

## 15. Organización física de los modelos en PostgreSQL

Las capas de transformación se separan físicamente en distintos esquemas de PostgreSQL:

```text
raw
staging
intermediate
marts
```

La correspondencia con dbt es:

| Capa         | Schema PostgreSQL | Materialización                 |
| ------------ | ----------------- | ------------------------------- |
| RAW          | `raw`             | tablas gestionadas fuera de dbt |
| STAGING      | `staging`         | `view`                          |
| INTERMEDIATE | `intermediate`    | `view`                          |
| MARTS        | `marts`           | `table`                         |

La configuración de los modelos se realiza mediante `+schema` en `dbt_project.yml`.

Se utiliza una implementación propia de `generate_schema_name` para que el nombre del schema personalizado se utilice directamente, evitando que dbt lo combine automáticamente con el schema definido en el perfil.

Esta separación permite mantener responsabilidades diferenciadas entre las capas y facilita la trazabilidad, el mantenimiento y la futura incorporación de nuevas fuentes.

Los schemas `intermediate` y `marts` se crearán cuando dbt ejecute por primera vez un modelo en dichas capas.

## 16. Validación integral del modelo analítico

La primera versión completa del modelo dimensional se valida mediante `dbt build`, ejecutando de forma integrada los modelos y sus tests respetando el grafo de dependencias.

En el snapshot ISTAC `C00065A_000036`, versión `2.17`, la ejecución completa produce:

* 7 modelos dbt.
* 2 modelos de tipo `view`: `stg_istac_tourism` e `int_istac_tourism_monthly`.
* 5 modelos de tipo `table`: las cuatro dimensiones y `fct_tourism`.
* 89 ejecuciones de modelos y tests completadas correctamente.
* 0 errores y 0 warnings.

La tabla de hechos `fct_tourism` contiene 158.672 filas, correspondientes al producto:

`211 meses × 47 territorios × 16 nacionalidades × 1 tipo de alojamiento`.

La unicidad del grano y las relaciones con las cuatro dimensiones se validan mediante tests de dbt.

