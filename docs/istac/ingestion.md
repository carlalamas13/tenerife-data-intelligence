# Ingesta versionada y loader RAW reutilizable

La ingesta de ISTAC se organiza en snapshots versionados por dataset y fecha de descarga. Cada snapshot contiene:

* `dataset.csv`
* `manifest.json`

El `manifest.json` registra la versión de la fuente, URL, nombre de fichero, tamaño y SHA-256.

La carga en PostgreSQL se realiza mediante un loader RAW genérico (`sql/02_load_raw_istac.sql`) y un script Python (`scripts/istac/load_raw.py`).

El script Python:

1. Lee y valida el `manifest.json`.
2. Comprueba que el CSV se encuentra dentro del directorio de datos del proyecto.
3. Verifica el tamaño del fichero.
4. Recalcula el SHA-256 y lo compara con el manifest.
5. Pasa los metadatos y la ruta del CSV al loader SQL.
6. Ejecuta la carga en PostgreSQL.

La tabla `raw.istac_ingestion_batch` mantiene un registro independiente para cada snapshot y la tabla de observaciones conserva el `ingestion_batch_id` correspondiente.

El loader utiliza una restricción única basada en dataset, versión, fecha de snapshot y SHA-256, junto con `ON CONFLICT`, para garantizar la idempotencia de la carga.

## Actualización a ISTAC 2.18

La versión `2.18` del dataset `C00065A_000036` fue descargada el `2026-09-30`.

El snapshot contiene 688.832 filas, frente a 685.824 en la versión `2.17`. Las 3.008 filas adicionales corresponden a `2026-M08`.

Se verificó que las 685.824 observaciones comunes entre las versiones `2.17` y `2.18` son idénticas. Por tanto, la actualización no introduce modificaciones retroactivas en el histórico observado.

La versión `2.18` se almacenó como un nuevo batch RAW sin eliminar el snapshot anterior. La repetición de la carga mediante el loader genérico fue validada y no produjo duplicados.

La capa STAGING selecciona automáticamente el snapshot más reciente mediante `snapshot_date`, `ingested_at` e `ingestion_batch_id`, por lo que la actualización de fuente se propaga automáticamente a INTERMEDIATE y MARTS.

El modelo analítico pasó de:

* 211 meses a 212 meses.
* 158.672 filas en `fct_tourism` a 159.424 filas.

El nuevo mes `2026-M08` aporta 752 combinaciones analíticas a `fct_tourism`.
