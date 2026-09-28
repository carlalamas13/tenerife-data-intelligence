with monthly_data as (

    select
        ingestion_batch_id,
        source_version,
        snapshot_date,
        period_code,
        period_start_date,
        territory_code,
        territory_name_es,
        nationality_code,
        nationality_name_es,
        accommodation_type_code,
        accommodation_type_name_es,
        measure_code,
        value,
        observation_status

    from {{ ref('stg_istac_tourism') }}

    where period_granularity = 'monthly'

),

aggregated as (

    select
        ingestion_batch_id,
        source_version,
        snapshot_date,

        period_code,
        period_start_date,

        territory_code,
        territory_name_es,

        nationality_code,
        nationality_name_es,

        accommodation_type_code,
        accommodation_type_name_es,

        max(value) filter (
            where measure_code = 'VIAJEROS_ENTRADOS'
        ) as travelers_entered,

        max(observation_status) filter (
            where measure_code = 'VIAJEROS_ENTRADOS'
        ) as travelers_entered_status,

        max(value) filter (
            where measure_code = 'VIAJEROS_ALOJADOS'
        ) as travelers_hosted,

        max(observation_status) filter (
            where measure_code = 'VIAJEROS_ALOJADOS'
        ) as travelers_hosted_status,

        max(value) filter (
            where measure_code = 'PERNOCTACIONES'
        ) as overnights,

        max(observation_status) filter (
            where measure_code = 'PERNOCTACIONES'
        ) as overnights_status,

        max(value) filter (
            where measure_code = 'ESTANCIA_MEDIA'
        ) as average_stay,

        max(observation_status) filter (
            where measure_code = 'ESTANCIA_MEDIA'
        ) as average_stay_status,

        count(*) as measure_count,
        count(value) as observed_measure_count

    from monthly_data

    group by
        ingestion_batch_id,
        source_version,
        snapshot_date,
        period_code,
        period_start_date,
        territory_code,
        territory_name_es,
        nationality_code,
        nationality_name_es,
        accommodation_type_code,
        accommodation_type_name_es

)

select *
from aggregated