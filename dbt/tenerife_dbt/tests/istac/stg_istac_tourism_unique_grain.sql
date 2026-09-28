select
    period_code,
    territory_code,
    accommodation_type_code,
    nationality_code,
    measure_code,
    count(*) as row_count
from {{ ref('stg_istac_tourism') }}
group by
    period_code,
    territory_code,
    accommodation_type_code,
    nationality_code,
    measure_code
having count(*) > 1