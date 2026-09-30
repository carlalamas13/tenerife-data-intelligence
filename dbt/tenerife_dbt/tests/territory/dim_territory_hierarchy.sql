select
    territory_code,
    territory_name_es,
    territory_level,
    island_code,
    island_name_es,
    is_residual
from {{ ref('dim_territory') }}
where
    (
        territory_level = 'region'
        and (
            island_code is not null
            or island_name_es is not null
            or is_residual
        )
    )
    or (
        territory_level = 'island'
        and (
            island_code is null
            or island_name_es is null
            or is_residual
        )
    )
    or (
        territory_level = 'municipality'
        and (
            island_code is null
            or island_name_es is null
            or is_residual
        )
    )
    or (
        territory_level = 'residual'
        and (
            island_code is null
            or island_name_es is null
            or not is_residual
        )
    )