with intermediate_count as (
    select count(*) as row_count
    from {{ ref('int_istac_tourism_monthly') }}
),

fact_count as (
    select count(*) as row_count
    from {{ ref('fct_tourism') }}
)

select
    intermediate_count.row_count as intermediate_rows,
    fact_count.row_count as fact_rows
from intermediate_count
cross join fact_count
where intermediate_count.row_count <> fact_count.row_count