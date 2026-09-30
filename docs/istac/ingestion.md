# Pipeline automatizado

El proceso de ingesta de ISTAC se puede ejecutar de extremo a extremo mediante:

`python -m scripts.istac.run_pipeline --version <version>`

El pipeline coordina las siguientes etapas:

1. Descarga del dataset y generación del `manifest.json`.
2. Validación de calidad del CSV descargado.
3. Validación de integridad mediante tamaño y SHA-256 durante la carga RAW.
4. Carga del snapshot en PostgreSQL RAW mediante el loader versionado e idempotente.
5. Ejecución de `dbt build` para reconstruir STAGING, INTERMEDIATE y MARTS y ejecutar sus tests.

La carga RAW y la ejecución de dbt solo se realizan si las etapas anteriores finalizan correctamente.

El pipeline recibe explícitamente la versión del dataset y utiliza el snapshot correspondiente generado durante la ejecución.

Esta estructura permite reproducir el proceso completo con un único punto de entrada y evita depender de la ejecución manual y secuencial de varios comandos.

## Detección automática de versiones

El pipeline puede detectar automáticamente la última versión disponible del dataset ISTAC mediante la API de recursos estadísticos.

La función `get_latest_version()` consulta las versiones publicadas para el dataset y selecciona la versión numéricamente mayor. La comparación se realiza sobre los componentes numéricos de la versión, evitando problemas derivados de una comparación lexicográfica de cadenas.

El pipeline mantiene además la posibilidad de indicar explícitamente una versión mediante `--version`, lo que permite reproducir una ejecución concreta:

`python -m scripts.istac.run_pipeline --version 2.18`

Cuando no se proporciona una versión, el pipeline consulta ISTAC y utiliza automáticamente la última versión disponible.

## Control de nuevas versiones

Cuando el pipeline se ejecuta sin indicar explícitamente una versión, compara la última versión disponible publicada por ISTAC con la última versión cargada en `raw.istac_ingestion_batch`.

Si ambas versiones coinciden, el pipeline finaliza sin descargar ni procesar nuevamente el dataset.

Este comportamiento evita ejecuciones innecesarias cuando el pipeline se programa periódicamente.

La detección se basa en el número de versión publicado por ISTAC. El SHA-256 continúa utilizándose como mecanismo de integridad y trazabilidad del contenido una vez descargado.

La ejecución con `--version <version>` permite procesar explícitamente una versión concreta, manteniendo la reproducibilidad de snapshots históricos.


