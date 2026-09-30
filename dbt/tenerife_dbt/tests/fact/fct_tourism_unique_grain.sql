select
    date_key,
    territory_code,
    nationality_code,
    accommodation_type_code
from {{ ref('fct_tourism') }}
group by
    date_key,
    territory_code,
    nationality_code,
    accommodation_type_code
having count(*) > 1