with tourism as (
    select
        ingestion_batch_id,
        source_version,
        snapshot_date,
        period_code,
        period_start_date,
        territory_code,
        nationality_code,
        accommodation_type_code,

        travelers_entered,
        travelers_entered_status,

        travelers_hosted,
        travelers_hosted_status,

        overnights,
        overnights_status,

        average_stay_status,

        measure_count,
        observed_measure_count
    from {{ ref('int_istac_tourism_monthly') }}
),

joined as (
    select
        date_dim.date_key,
        tourism.territory_code,
        tourism.nationality_code,
        tourism.accommodation_type_code,

        tourism.ingestion_batch_id,
        tourism.source_version,
        tourism.snapshot_date,

        tourism.travelers_entered,
        tourism.travelers_entered_status,

        tourism.travelers_hosted,
        tourism.travelers_hosted_status,

        tourism.overnights,
        tourism.overnights_status,

        case
            when tourism.average_stay_status = 'observed'
              and tourism.travelers_entered is not null
              and tourism.overnights is not null
              and tourism.travelers_entered <> 0
                then round(
                    tourism.overnights / tourism.travelers_entered,
                    10
                )::numeric(20,10)
            else null
        end as average_stay,

        tourism.average_stay_status,

        tourism.measure_count,
        tourism.observed_measure_count

    from tourism
    left join {{ ref('dim_date') }} as date_dim
        on date_dim.month_start_date = tourism.period_start_date

    left join {{ ref('dim_territory') }} as territory_dim
        on territory_dim.territory_code = tourism.territory_code

    left join {{ ref('dim_nationality') }} as nationality_dim
        on nationality_dim.nationality_code = tourism.nationality_code

    left join {{ ref('dim_accommodation') }} as accommodation_dim
        on accommodation_dim.accommodation_type_code = tourism.accommodation_type_code
)

select *
from joined