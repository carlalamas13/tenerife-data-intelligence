select
    period_code,
    territory_code,
    nationality_code,
    accommodation_type_code,
    travelers_entered,
    overnights,
    average_stay
from {{ ref('int_istac_tourism_monthly') }}
where average_stay is not null
  and travelers_entered is not null
  and overnights is not null
  and travelers_entered <> 0
  and abs(
      average_stay
      - overnights / travelers_entered
  ) > 0.0000001