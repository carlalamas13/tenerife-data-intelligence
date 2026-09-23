# Tenerife Data Intelligence

Plataforma de datos de extremo a extremo para analizar y predecir la actividad turística de Tenerife.

## Estado

**V0 — Diseño + primera ingesta ISTAC**

## Objetivo

Integrar fuentes públicas heterogéneas de Tenerife (turismo, movilidad, meteorología, población y geografía), construir un modelo analítico reproducible, medir la calidad del dato y desarrollar modelos de forecasting y detección de anomalías.

## Arquitectura inicial

```text
ISTAC / Cabildo / AEMET / INE / GIS
                |
             Ingestion
                |
              RAW
                |
        PostgreSQL / PostGIS
                |
               dbt
                |
         Data Quality + ML
                |
        Power BI / FastAPI
```

## Primera fuente

ISTAC — Encuesta de Alojamiento Turístico, cubo `C00065A_000036` (viajeros alojados, viajeros entrados, pernoctaciones y estancia media).

El recurso actual es la versión 2.17 y contiene datos mensuales y anuales desde 2009, desagregados por islas y municipios y según principales nacionalidades. La documentación de ISTAC indica que los cubos estadísticos de e-Cubos son accesibles mediante API.

## Estructura

```text
.
├── docs/
├── src/
│   ├── ingestion/
│   ├── quality/
│   └── ml/
├── dags/
├── dbt/
├── notebooks/
├── api/
├── tests/
├── data/
│   ├── raw/
│   └── processed/
├── .github/workflows/
├── .env.example
├── .gitignore
├── pyproject.toml
└── README.md
```

## Próximo objetivo

1. Descargar el cubo ISTAC en RAW.
2. Inspeccionar su esquema real.
3. Identificar dimensiones, métricas y códigos territoriales.
4. Crear `stg_istac_tourism` en dbt.
5. Cargar PostgreSQL.
6. Añadir tests de calidad.
