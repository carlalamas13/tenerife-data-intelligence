# V0 — Definición del proyecto

## 1. Problema

Construir una plataforma reproducible que permita integrar, analizar y predecir la actividad turística de Tenerife a partir de fuentes públicas heterogéneas.

## 2. Preguntas principales

- ¿Cómo evoluciona la actividad turística por municipio y mes?
- ¿Qué patrones estacionales aparecen?
- ¿Cómo se relaciona la actividad turística con movilidad y meteorología?
- ¿Qué municipios presentan comportamientos similares?
- ¿Podemos predecir la demanda turística mensual?
- ¿Podemos detectar meses con comportamiento anómalo?

## 3. Alcance MVP

### Fuentes

- ISTAC — turismo.
- Cabildo de Tenerife — tráfico.
- Cabildo de Tenerife — meteorología.
- INE — población.
- Cabildo de Tenerife — geometrías municipales.

### Plataforma

- Python
- Airflow
- PostgreSQL/PostGIS
- dbt
- pytest
- Power BI

### ML

- baseline estacional
- forecasting con árbol de boosting
- detección de anomalías

## 4. Principios

1. Mantener los datos originales en RAW.
2. No modificar los datos fuente de forma destructiva.
3. Definir el grano de cada tabla antes de modelarla.
4. Toda transformación importante debe ser reproducible.
5. Toda métrica de negocio debe tener una definición documentada.
6. Los modelos deben compararse contra un baseline.
7. La validación de ML será temporal, no aleatoria.
