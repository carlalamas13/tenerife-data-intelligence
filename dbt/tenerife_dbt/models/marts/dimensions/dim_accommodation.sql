with accommodations as (
    select distinct
        accommodation_type_code,
        accommodation_type_name_es
    from {{ ref('stg_istac_tourism') }}
)

select
    accommodation_type_code,
    accommodation_type_name_es
from accommodations