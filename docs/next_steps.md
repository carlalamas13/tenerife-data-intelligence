# Próximos pasos

## Sprint 1

1. Ejecutar la descarga del cubo ISTAC.
2. Inspeccionar el CSV y documentar columnas.
3. Identificar el código/label de Tenerife y sus municipios.
4. Determinar el grano real del recurso.
5. Seleccionar las variables que formarán `stg_istac_tourism`.
6. Crear el esquema PostgreSQL.
7. Cargar RAW y staging.

## Sprint 2

- añadir Cabildo turismo como fuente de reconciliación;
- crear `dim_date` y `dim_municipality`;
- comenzar dbt;
- añadir tests de unicidad, not-null y valores válidos.
