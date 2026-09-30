with bounds as (
    select
        date_trunc('month', min(period_start_date))::date as min_month,
        date_trunc('month', max(period_start_date))::date as max_month
    from {{ ref('int_istac_tourism_monthly') }}
),

calendar as (
    select
        generate_series(
            min_month,
            max_month,
            interval '1 month'
        )::date as month_start_date
    from bounds
    where min_month is not null
      and max_month is not null
)

select
    (
        extract(year from month_start_date)::int * 100
        + extract(month from month_start_date)::int
    ) as date_key,
    month_start_date,
    extract(year from month_start_date)::int as year,
    extract(quarter from month_start_date)::int as quarter,
    extract(month from month_start_date)::int as month_number,
    case extract(month from month_start_date)::int
        when 1 then 'Enero'
        when 2 then 'Febrero'
        when 3 then 'Marzo'
        when 4 then 'Abril'
        when 5 then 'Mayo'
        when 6 then 'Junio'
        when 7 then 'Julio'
        when 8 then 'Agosto'
        when 9 then 'Septiembre'
        when 10 then 'Octubre'
        when 11 then 'Noviembre'
        when 12 then 'Diciembre'
    end as month_name_es,
    to_char(month_start_date, 'YYYY-MM') as year_month
from calendar