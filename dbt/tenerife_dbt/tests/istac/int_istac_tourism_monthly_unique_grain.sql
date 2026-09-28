select
    period_code,
    territory_code,
    accommodation_type_code,
    nationality_code,
    count(*) as row_count
from {{ ref('int_istac_tourism_monthly') }}
group by
    period_code,
    territory_code,
    accommodation_type_code,
    nationality_code
having count(*) > 1