select
    nationality_code,
    nationality_level,
    parent_nationality_code,
    is_total,
    is_residual
from {{ ref('dim_nationality') }}
where
    (
        nationality_level = 'total'
        and (
            nationality_code <> '_T'
            or parent_nationality_code is not null
            or not is_total
            or is_residual
        )
    )
    or (
        nationality_level = 'aggregate'
        and (
            nationality_code not in ('ES', '5000_XES')
            or parent_nationality_code <> '_T'
            or is_total
            or is_residual
        )
    )
    or (
        nationality_level = 'country'
        and (
            nationality_code in ('_T', 'ES', '5000_XES', '5000_XES_O')
            or parent_nationality_code <> '5000_XES'
            or is_total
            or is_residual
        )
    )
    or (
        nationality_level = 'residual'
        and (
            nationality_code <> '5000_XES_O'
            or parent_nationality_code <> '5000_XES'
            or is_total
            or not is_residual
        )
    )