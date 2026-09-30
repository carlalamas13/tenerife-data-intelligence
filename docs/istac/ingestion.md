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
