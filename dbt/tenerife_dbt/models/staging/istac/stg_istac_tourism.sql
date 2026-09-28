with source_data as (

    select
        measure_name_es,
        measure_code,
        territory_name_es,
        territory_code,
        period_label_es,
        period_code,
        accommodation_type_name_es,
        accommodation_type_code,
        nationality_name_es,
        nationality_code,
        value,
        observation_note_es,
        observation_status_name_es,
        observation_status_code,
        confidentiality_name_es,
        confidentiality_code
    from {{ source('istac', 'istac_c00065a_000036') }}

),

staged as (

    select
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
            when observation_status_code is not null
                then 'not_available'
            when confidentiality_code is not null
                then 'confidential'
            else 'not_published'
        end as observation_status

    from source_data

)

select *
from staged