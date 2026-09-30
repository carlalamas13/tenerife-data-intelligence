# Próximos pasos

## Estado actual

La primera fase de trabajo con el dataset ISTAC `C00065A_000036` se encuentra completada y cuenta con un pipeline reproducible de extremo a extremo.

Se ha realizado la descarga versionada del recurso, la inspección de su estructura, el análisis de cobertura y valores ausentes, la identificación y validación de jerarquías territoriales y de nacionalidad y distintas comprobaciones sobre las medidas publicadas.

Se ha implementado una arquitectura de datos por capas:

`fuente → RAW → STAGING → INTERMEDIATE → MARTS`

La capa RAW conserva snapshots versionados e independientes, con trazabilidad mediante `ingestion_batch_id`, versión, fecha, URL, tamaño y SHA-256.

La capa STAGING selecciona automáticamente el snapshot activo y aplica las transformaciones iniciales y reglas de calidad documentadas.

La capa INTERMEDIATE reorganiza las medidas mensuales del cubo para facilitar su utilización analítica.

La capa MARTS contiene el modelo dimensional:

* `dim_date`
* `dim_territory`
* `dim_nationality`
* `dim_accommodation`
* `fct_tourism`

La tabla `fct_tourism` utiliza como grano:

`mes + territorio + nacionalidad + tipo de alojamiento`

La fact table contiene actualmente 159.424 filas para el snapshot ISTAC 2.18, correspondiente a 212 meses, 47 territorios, 16 nacionalidades y un tipo de alojamiento.

También se ha implementado un pipeline automatizado mediante:

`python -m scripts.istac.run_pipeline --version <version>`

que coordina descarga, validación, carga RAW y `dbt build`.

La actualización de ISTAC 2.17 a 2.18 ha sido validada como una extensión mensual sin modificaciones retroactivas del histórico compartido.

## Siguiente bloque: robustez y automatización

### 1. Consolidar el pipeline de ingesta

* [x] Automatizar la descarga del dataset.
* [x] Generar `manifest.json`.
* [x] Validar integridad mediante tamaño y SHA-256.
* [x] Ejecutar el quality gate antes de cargar RAW.
* [x] Utilizar un loader RAW reutilizable.
* [x] Garantizar la idempotencia de la carga.
* [x] Mantener snapshots históricos independientes.
* [ ] Mejorar la interfaz entre la descarga y el pipeline para devolver directamente el snapshot generado.
* [ ] Añadir pruebas automatizadas específicas para el pipeline de ingesta.
* [x] Evaluar la detección automática de nuevas versiones disponibles del dataset.

### 2. Automatizar la ejecución

* [ ] Diseñar la ejecución periódica del pipeline.
* [ ] Evaluar GitHub Actions como mecanismo de automatización.
* [ ] Separar correctamente las tareas que requieren infraestructura local de las que pueden ejecutarse en CI.
* [ ] Definir gestión de errores y criterios de fallo del pipeline.
* [ ] Documentar el proceso de ejecución desde un entorno limpio.

## Integración de nuevas fuentes

### 3. Datos del portal de Datos Abiertos de Tenerife

* [ ] Identificar conjuntos de datos relevantes para el análisis turístico.
* [ ] Analizar estructura, granularidad, cobertura temporal y calidad.
* [ ] Diseñar la ingesta y persistencia en RAW.
* [ ] Definir transformaciones y modelo analítico.
* [ ] Analizar la complementariedad con ISTAC.
* [ ] Evaluar posibles reconciliaciones entre fuentes cuando existan conceptos o métricas comparables.

### 4. Nuevos cubos ISTAC

* [ ] Incorporar el cubo de capacidad y ocupación turística.
* [ ] Analizar su relación con `C00065A_000036`.
* [ ] Identificar dimensiones y métricas compartidas.
* [ ] Determinar qué información puede integrarse en el modelo analítico actual.
* [ ] Documentar diferencias de definición, granularidad y cobertura entre cubos.

Cada nueva fuente deberá seguir, siempre que sea posible, el mismo patrón:

`ingesta → validación → documentación → RAW → STAGING → INTERMEDIATE → MARTS`

## Modelo analítico

### 5. Evolución del modelo dimensional

* [x] Crear `dim_date`.
* [x] Crear `dim_territory`.
* [x] Crear `dim_nationality`.
* [x] Crear `dim_accommodation`.
* [x] Crear `fct_tourism`.
* [x] Definir y validar el grano de la fact table.
* [x] Definir medidas derivadas y reglas de cálculo.
* [ ] Evaluar la necesidad de dimensiones o tablas de hechos adicionales al incorporar nuevas fuentes.
* [ ] Revisar la evolución de las dimensiones cuando aparezcan nuevos códigos o categorías en futuras versiones de ISTAC.
* [ ] Definir estrategias de gestión de cambios de dimensiones si el modelo lo requiere.

## Calidad y observabilidad

### 6. Consolidar las reglas de calidad

* [x] Automatizar tests de estructura y unicidad.
* [x] Validar jerarquías territoriales.
* [x] Validar jerarquías de nacionalidad.
* [x] Validar coherencia de `ESTANCIA_MEDIA`.
* [x] Validar consistencia entre valores y estados de observación.
* [x] Validar relaciones entre fact table y dimensiones.
* [x] Validar conservación del número de filas entre INTERMEDIATE y MARTS.
* [ ] Ampliar las pruebas unitarias y de integración del pipeline.
* [ ] Definir controles específicos para cambios estructurales de nuevas versiones.
* [ ] Evaluar métricas de observabilidad de la ingesta y de las transformaciones.

## Análisis e inteligencia

### 7. Análisis exploratorio

* [ ] Realizar un análisis exploratorio del modelo analítico.
* [ ] Estudiar evolución temporal y estacionalidad.
* [ ] Analizar diferencias entre territorios y municipios.
* [ ] Analizar composición y evolución de las nacionalidades.
* [ ] Identificar patrones asociados a las distintas medidas turísticas.

### 8. Análisis avanzado

* [ ] Detectar anomalías y cambios significativos.
* [ ] Diseñar variables derivadas para el análisis.
* [ ] Construir modelos de predicción de demanda turística.
* [ ] Evaluar diferentes horizontes temporales de predicción.
* [ ] Medir y comparar el rendimiento de los modelos.
* [ ] Evaluar escenarios de evolución de la demanda turística.

## Exposición de resultados

### 9. Capa de consumo

* [ ] Diseñar un conjunto de consultas analíticas sobre `marts`.
* [ ] Preparar el modelo para Power BI.
* [ ] Definir métricas y KPIs de consumo.
* [ ] Crear visualizaciones analíticas.
* [ ] Diseñar un dashboard de inteligencia turística.
* [ ] Evaluar la creación de una API de consulta sobre el modelo analítico.

### 10. Documentación final

* [ ] Documentar la arquitectura completa.
* [ ] Documentar el flujo de ejecución y actualización.
* [ ] Documentar las fuentes incorporadas y sus limitaciones.
* [ ] Documentar las decisiones de modelado y calidad.
* [ ] Documentar los principales resultados obtenidos.
* [ ] Preparar una descripción técnica del proyecto para su presentación como portfolio.

## Principio de trabajo

Cada nueva fuente deberá seguir, siempre que sea posible, el flujo:

`ingesta → validación → documentación → RAW → STAGING → INTERMEDIATE → modelo analítico → análisis → consumo`

Las decisiones sobre arquitectura, calidad, modelado o metodología deberán quedar documentadas junto con su justificación y reflejarse en el historial del proyecto.
