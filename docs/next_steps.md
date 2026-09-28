# Próximos pasos

## Estado actual

La primera faes de trabajo con el dataset ISTAC `C00065A_000036`se encuentra completada.

Se ha realizado la descarga del recurso, la inspección de su estructura, el análisis de cobertura y valores ausentes, la identificación de jerarquías territoriales y de nacionalidad y varias validaciones sobre las medidas publicadas.

También se han automatizado y testeado parte de las reglas de calidad identificadas durante el análisis.

## Siguiente bloque: modelado y persistencia

### 1. Diseña la capa de staging de ISTAC

- Definir el grano de la tabla de staging.
- Seleccionarlas columnas que se conservarán.
- Definir nombres y tipos de datos.
- Definir claves y restricciones.
- Definir el tratamiento de observaciones ausentes y metadatos.
- Definir qué dimensiones se mantendrán en el modelo analítico.

### 2. Preparar PostgreSQL

- Definir la estructura de esquemas.
- Crear la tabla RAW para el dataset ISTAC.
- Cargar el snapshot descargado.
- Comprobar recuentos, tipos y unicidad.

### 3. Crear la capa de staging

- Crear `stg_istac_tourism`.
- Trabajar exclusivamente con observaciones mensuales.
- Mantener la trazabilidad respecto al dato RAW.
- Aplicar las reglas de transformación documentadas.

### 4. Incorporar dbt

- Configurar la fuente RAW.
- Crear el modelo de staging.
- Añadir tests de unicidad, valores nulos y relaciones válidas.
- Documentar columnas y modelos.

## Bloques posteriores

### Integración de fuentes
- Incorporar datos del portal de Datos Abiertos de Tenerife.
- Incorporar el cubo ISTAC de capacidad y ocupación.
- Analizar la complementariedad y posibles reconciliaciones entre fuentes.

### Modelo analítico
- Crear `dim_date`.
- Crear `dim_municipality`.
- Diseñar las tablas de hechos necesarias.
- Definir métricas derivadas y reglas de agregación.


### Análisis e inteligencia
- Realizar análisis exploratorio.
- Analizar tendencias y estacionalidad.
- Detectar anomalías.
- Construir modelos de predicción.
- Evaluar escenarios y evolución de la demanda turística.

### Exposición de resultados
- Crear visualizaciones analíticas.
- Preparar el modelo para Power BI.
- Evaluar la creación de una API.
- Documentar los principales resultados y decisiones del proyecto.

## Principio de trabajo

Cada nueva fuente deberá seguir, siempre que sea posible, el flujo:

`ingesta → validación → documentación → RAW → staging → modelo analítico → análisis`