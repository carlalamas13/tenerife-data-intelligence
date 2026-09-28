# Modelo de staging del dataset ISTAC C00065A_000036

## 1. Objetivo

Este documento define la estructura de la capa de staging para el dataset ISTAC `C00065A_000036`.

El staging tiene como objetivo normalizar nombres, tipos de datos y atributos temporales de la fuente original manteniendo la trazabilidad respecto al fichero RAW.

La capa de staging no pretende todavía construir el modelo analítico final. Las dimensiones y tablas de hechos se definirán en una fase posterior.

## 2. Principios de diseño

El modelo de staging seguirá los siguientes principios:

* Mantener la información procedente de la fuente original siempre que resulte relevante para la trazabilidad.
* Normalizar los nombres de las columnas al inglés y utilizar `snake_case`.
* Mantener los códigos oficiales de ISTAC sin modificarlos.
* Separar las etiquetas descriptivas de los códigos.
* Conservar las observaciones mensuales y anuales de la fuente.
* No sustituir valores ausentes de `OBS_VALUE` por cero.
* Mantener los estados de observación y confidencialidad.
* Añadir atributos derivados que faciliten el tratamiento temporal y la calidad del dato.
* Evitar transformaciones específicas del modelo analítico en esta capa.

## 3. Grano

El grano de `stg_istac_tourism` es una observación de una medida para una combinación concreta de:

* periodo;
* territorio;
* tipo de alojamiento;
* nacionalidad;
* medida.

La clave natural de una observación es:

```text
period_code
+ territory_code
+ accommodation_type_code
+ nationality_code
+ measure_code
```

La unicidad de esta combinación se ha comprobado sobre el dataset analizado.

## 4. Estructura

| Columna staging              | Origen                              | Tipo PostgreSQL  | Nulo | Descripción                               |
| ---------------------------- | ----------------------------------- | ---------------- | ---- | ----------------------------------------- |
| `measure_name_es`            | `MEDIDAS#es`                        | `text`           | Sí   | Nombre de la medida publicado por ISTAC   |
| `measure_code`               | `MEDIDAS_CODE`                      | `text`           | No   | Código oficial de la medida               |
| `territory_name_es`          | `TERRITORIO#es`                     | `text`           | Sí   | Nombre del territorio publicado por ISTAC |
| `territory_code`             | `TERRITORIO_CODE`                   | `text`           | No   | Código oficial del territorio             |
| `period_label_es`            | `TIME_PERIOD#es`                    | `text`           | Sí   | Etiqueta descriptiva del periodo          |
| `period_code`                | `TIME_PERIOD_CODE`                  | `text`           | No   | Código temporal oficial                   |
| `period_granularity`         | Derivado                            | `text`           | No   | Granularidad: `monthly` o `annual`        |
| `period_start_date`          | Derivado                            | `date`           | No   | Fecha de inicio del periodo               |
| `accommodation_type_name_es` | `ALOJAMIENTO_TURISTICO_TIPO#es`     | `text`           | Sí   | Nombre del tipo de alojamiento            |
| `accommodation_type_code`    | `ALOJAMIENTO_TURISTICO_TIPO_CODE`   | `text`           | No   | Código oficial del tipo de alojamiento    |
| `nationality_name_es`        | `NACIONALIDAD#es`                   | `text`           | Sí   | Nombre de la nacionalidad                 |
| `nationality_code`           | `NACIONALIDAD_CODE`                 | `text`           | No   | Código oficial de la nacionalidad         |
| `value`                      | `OBS_VALUE`                         | `numeric(20,10)` | Sí   | Valor numérico de la observación          |
| `observation_note_es`        | `NOTAS_OBSERVACION#es`              | `text`           | Sí   | Notas asociadas a la observación          |
| `observation_status_name_es` | `ESTADO_OBSERVACION#es`             | `text`           | Sí   | Descripción del estado de la observación  |
| `observation_status_code`    | `ESTADO_OBSERVACION_CODE`           | `text`           | Sí   | Código del estado de la observación       |
| `confidentiality_name_es`    | `CONFIDENCIALIDAD_OBSERVACION#es`   | `text`           | Sí   | Descripción de la confidencialidad        |
| `confidentiality_code`       | `CONFIDENCIALIDAD_OBSERVACION_CODE` | `text`           | Sí   | Código de confidencialidad                |
| `observation_status`         | Derivado                            | `text`           | No   | Clasificación normalizada del estado      |

## 5. Tratamiento temporal

`TIME_PERIOD_CODE` contiene dos tipos de observaciones:

* anuales, con formato `YYYY`;
* mensuales, con formato `YYYY-MMM`.

Ejemplos:

```text
2009
2009-M01
2026-M07
```

Se conservará el código original en `period_code`.

Además, se derivarán:

* `period_granularity = annual` para periodos anuales;
* `period_granularity = monthly` para periodos mensuales;
* `period_start_date` como fecha de inicio del periodo.

El staging conservará ambas granularidades porque forman parte de la fuente original.

El modelo analítico posterior podrá seleccionar exclusivamente las observaciones mensuales cuando sea necesario aplicar las reglas de agregación definidas para el proyecto.

## 6. Tratamiento de `OBS_VALUE`

`OBS_VALUE` se almacenará como `numeric(20,10)` para conservar la precisión observada en `ESTANCIA_MEDIA` y cubrir los valores de mayor magnitud presentes en las medidas de conteo.

Los valores nulos se conservarán como `NULL`.

No se realizará una sustitución general de valores nulos por cero.

## 7. Clasificación del estado de la observación

Se añadirá `observation_status` como atributo derivado a partir de:

* `OBS_VALUE`;
* `ESTADO_OBSERVACION_CODE`;
* `CONFIDENCIALIDAD_OBSERVACION_CODE`.

Los posibles valores serán:

| `observation_status` | Significado                                                    |
| -------------------- | -------------------------------------------------------------- |
| `observed`           | La observación contiene un valor                               |
| `not_available`      | El valor está ausente y el estado es `O`                       |
| `confidential`       | El valor está ausente y la confidencialidad es `C`             |
| `not_published`      | El valor está ausente sin código de estado ni confidencialidad |

Esta clasificación procede de las reglas de calidad documentadas en `docs/istac/data-quality.md`.

## 8. Códigos oficiales

Los códigos de ISTAC se conservarán sin recodificación en staging:

* `measure_code`
* `territory_code`
* `period_code`
* `accommodation_type_code`
* `nationality_code`
* `observation_status_code`
* `confidentiality_code`

Las transformaciones semánticas adicionales se realizarán en capas posteriores.

## 9. Cobertura territorial

El staging conservará todos los territorios publicados por ISTAC.

No se filtrará inicialmente a Tenerife.

Las reglas específicas de análisis de Tenerife, incluido el tratamiento de `ES709_O`, se aplicarán en capas posteriores.

## 10. Medidas

El dataset contiene actualmente cuatro medidas:

* `VIAJEROS_ENTRADOS`
* `VIAJEROS_ALOJADOS`
* `PERNOCTACIONES`
* `ESTANCIA_MEDIA`

Las reglas de agregación no se aplicarán en staging.

En capas posteriores:

* `VIAJEROS_ENTRADOS` podrá agregarse bajo las reglas definidas para el proyecto.
* `PERNOCTACIONES` podrá agregarse bajo las reglas definidas para el proyecto.
* `VIAJEROS_ALOJADOS` no se sumará entre meses.
* `ESTANCIA_MEDIA` se recalculará a partir de `PERNOCTACIONES / VIAJEROS_ENTRADOS`.

## 11. Trazabilidad

La capa de staging deberá permitir identificar el origen de cada observación respecto al RAW.

El snapshot original permanecerá sin modificar en:

```text
data/raw/istac/C00065A_000036/
```

La metadata de la descarga se conserva mediante el `manifest.json` asociado a cada snapshot.

## 12. Fuera del alcance del staging

No forman parte de esta fase:

* la creación de dimensiones analíticas;
* la construcción de tablas de hechos;
* la agregación definitiva de medidas;
* la reconciliación con fuentes del Cabildo;
* el tratamiento específico para visualización;
* los modelos predictivos.

Estas transformaciones se realizarán en capas posteriores.

## 13. Organización de las capas RAW y staging en PostgreSQL

La base de datos separará la representación de la fuente original de la capa de transformación mediante dos esquemas:

* `raw`: conserva los datos procedentes de las fuentes y la información necesaria para identificar cada ingesta;
* `staging`: contiene los datos normalizados y preparados para las capas posteriores del modelo.

La capa RAW del dataset `C00065A_000036` se organiza mediante:

* `raw.istac_ingestion_batch`, que identifica cada snapshot descargado;
* `raw.istac_c00065a_000036`, que conserva las observaciones correspondientes a cada lote de ingesta.

Cada lote queda identificado mediante la versión de la fuente, la fecha del snapshot, la URL y el SHA-256 del fichero descargado.

El diseño es acumulativo: nuevas versiones del dataset no deben sobrescribir las anteriores. Esto permite conservar la trazabilidad y comparar snapshots cuando la fuente cambie.

La carga inicial se realizará desde el fichero RAW almacenado en:

```text
data/raw/istac/C00065A_000036/
```

La capa RAW no aplica las reglas de agregación ni las transformaciones específicas del modelo analítico. Estas operaciones se realizarán posteriormente en staging y en las capas de modelado.

La carga de un mismo snapshot debe ser idempotente. La tabla RAW utiliza una restricción de unicidad basada en el lote de ingesta y el grano natural de la observación para evitar duplicaciones cuando un fichero se procese más de una vez.

## 14. Implementación mediante dbt

La capa de staging se implementa mediante dbt sobre PostgreSQL.

El flujo de dependencias es:

```text
raw.istac_c00065a_000036
        ↓
dbt source: istac
        ↓
staging.stg_istac_tourism
```

`stg_istac_tourism` se materializa como una vista en el esquema `staging`.

El modelo mantiene las observaciones mensuales y anuales de la fuente y aplica únicamente transformaciones de normalización y enriquecimiento del periodo y del estado de observación.

La configuración del modelo se encuentra en:

```text
dbt/tenerife_dbt/models/staging/istac/
```

Los tests de datos se utilizan para comprobar valores no nulos, categorías permitidas y el cumplimiento del grano natural del modelo.

### 14.1. Incidencia con dbt Fusion

Durante la configuración inicial se utilizó dbt Fusion `2.0.0-preview.173` en Windows.

La conexión contra PostgreSQL produjo el error:

`LoadLibraryExW failed`

Se optó por utilizar dbt Core `1.12.5` junto con `dbt-postgres` `1.11.0`, instalados como dependencias del entorno virtual del proyecto.

La conexión con PostgreSQL se validó correctamente mediante dbt Core y el modelo `stg_istac_tourism` se ejecuta correctamente sobre la base de datos `tenerife`.

Las credenciales permanecen fuera del repositorio en el perfil local de dbt.

## 15. Selección del lote activo

La capa RAW conserva distintos snapshots del dataset para mantener la trazabilidad y permitir comparar versiones de la fuente.

`stg_istac_tourism` representa únicamente el último lote disponible del dataset `C00065A_000036`.

El lote activo se determina ordenando los registros de `raw.istac_ingestion_batch` por:

1. fecha del snapshot;
2. fecha de ingesta;
3. identificador del lote.

Se selecciona el registro más reciente.

De esta forma, la acumulación histórica de snapshots en RAW no provoca duplicaciones ni mezcla de versiones en la capa de staging.

El modelo mantiene además:

* `ingestion_batch_id`;
* `source_version`;
* `snapshot_date`.

Estos atributos permiten identificar el snapshot concreto del que procede cada observación.

Cuando se incorpore una nueva versión del dataset, el nuevo lote podrá almacenarse en RAW sin modificar el snapshot anterior, mientras que staging pasará a utilizar automáticamente el nuevo lote como activo.
