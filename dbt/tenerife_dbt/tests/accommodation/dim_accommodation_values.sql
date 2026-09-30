select
    accommodation_type_code,
    accommodation_type_name_es
from {{ ref('dim_accommodation') }}
where accommodation_type_code is null
   or accommodation_type_name_es is null