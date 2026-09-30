with nationalities as (
    select distinct
        nationality_code,
        nationality_name_es
    from {{ ref('stg_istac_tourism') }}
)

select
    nationality_code,
    nationality_name_es,

    case
        when nationality_code = '_T' then 'total'
        when nationality_code in ('ES', '5000_XES') then 'aggregate'
        when nationality_code = '5000_XES_O' then 'residual'
        else 'country'
    end as nationality_level,

    case
        when nationality_code = '_T' then null
        when nationality_code in ('ES', '5000_XES') then '_T'
        when nationality_code = '5000_XES_O' then '5000_XES'
        else '5000_XES'
    end as parent_nationality_code,

    nationality_code = '_T' as is_total,

    nationality_code = '5000_XES_O' as is_residual

from nationalities