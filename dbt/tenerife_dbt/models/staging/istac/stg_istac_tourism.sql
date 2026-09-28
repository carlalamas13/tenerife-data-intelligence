with latest_batch as (

    select
        ingestion_batch_id,
        source_version,
        snapshot_date
    from {{ source('istac', 'istac_ingestion_batch') }}
    where dataset_code = 'C00065A_000036'
    order by
        snapshot_date desc,
        ingested_at desc,
        ingestion_batch_id desc
    limit 1

),

source_data as (

    select
        raw.ingestion_batch_id,
        batch.source_version,
        batch.snapshot_date,

        raw.measure_name_es,
        raw.measure_code,

        raw.territory_name_es,
        raw.territory_code,

        raw.period_label_es,
        raw.period_code,

        raw.accommodation_type_name_es,
        raw.accommodation_type_code,

        raw.nationality_name_es,
        raw.nationality_code,

        raw.value,

        raw.observation_note_es,

        raw.observation_status_name_es,
        raw.observation_status_code,

        raw.confidentiality_name_es,
        raw.confidentiality_code

    from {{ source('istac', 'istac_c00065a_000036') }} as raw
    inner join latest_batch as batch
        on raw.ingestion_batch_id = batch.ingestion_batch_id

),

staged as (

    select
        ingestion_batch_id,
        source_version,
        snapshot_date,

        measure_name_es,
        measure_code,

        territory_name_es,
        territory_code,

        period_label_es,
        period_code,

        case
            when period_code ~ '^[0-9]{4}-M[0-9]{2}$'
                then 'monthly'
            when period_code ~ '^[0-9]{4}$'
                then 'annual'
            else 'unknown'
        end as period_granularity,

        case
            when period_code ~ '^[0-9]{4}-M[0-9]{2}$'
                then to_date(
                    replace(period_code, '-M', '-'),
                    'YYYY-MM'
                )
            when period_code ~ '^[0-9]{4}$'
                then to_date(period_code || '-01-01', 'YYYY-MM-DD')
            else null
        end as period_start_date,

        accommodation_type_name_es,
        accommodation_type_code,

        nationality_name_es,
        nationality_code,

        value,

        observation_note_es,

        observation_status_name_es,
        observation_status_code,

        confidentiality_name_es,
        confidentiality_code,

        case
            when value is not null
                then 'observed'
            when observation_status_code = 'O'
                then 'not_available'
            when confidentiality_code = 'C'
                then 'confidential'
            when observation_status_code is null
                and confidentiality_code is null
                then 'not_published'
            else 'unknown'
        end as observation_status

    from source_data

)

select *
from staged