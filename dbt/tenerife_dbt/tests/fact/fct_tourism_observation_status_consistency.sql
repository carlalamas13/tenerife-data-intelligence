select
    'travelers_entered' as measure,
    date_key,
    territory_code,
    nationality_code,
    accommodation_type_code
from {{ ref('fct_tourism') }}
where
    (travelers_entered_status = 'observed' and travelers_entered is null)
    or
    (travelers_entered_status <> 'observed' and travelers_entered is not null)

union all

select
    'travelers_hosted' as measure,
    date_key,
    territory_code,
    nationality_code,
    accommodation_type_code
from {{ ref('fct_tourism') }}
where
    (travelers_hosted_status = 'observed' and travelers_hosted is null)
    or
    (travelers_hosted_status <> 'observed' and travelers_hosted is not null)

union all

select
    'overnights' as measure,
    date_key,
    territory_code,
    nationality_code,
    accommodation_type_code
from {{ ref('fct_tourism') }}
where
    (overnights_status = 'observed' and overnights is null)
    or
    (overnights_status <> 'observed' and overnights is not null)

union all

select
    'average_stay' as measure,
    date_key,
    territory_code,
    nationality_code,
    accommodation_type_code
from {{ ref('fct_tourism') }}
where
    (average_stay_status = 'observed' and average_stay is null)
    or
    (average_stay_status <> 'observed' and average_stay is not null)