select
    date_key,
    territory_code,
    nationality_code,
    accommodation_type_code,
    travelers_entered,
    overnights,
    average_stay
from {{ ref('fct_tourism') }}
where average_stay is not null
  and travelers_entered is not null
  and overnights is not null
  and travelers_entered <> 0
  and average_stay <> round(
      overnights / travelers_entered,
      10
  )::numeric(20,10)