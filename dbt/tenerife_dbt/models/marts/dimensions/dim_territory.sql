with territories as (
    select distinct
        territory_code,
        territory_name_es
    from {{ ref('stg_istac_tourism') }}
),

classified as (
    select
        territory_code,
        territory_name_es,

        case
            when territory_code = 'ES70' then 'region'
            when territory_code ~ '^ES[0-9]{3}$' then 'island'
            when territory_code ~ '^ES[0-9]{3}_O$' then 'residual'
            else 'municipality'
        end as territory_level,

        case
            when territory_code in ('ES703', 'ES703_O')
              or territory_code in ('38013_2007', '38048', '38901')
                then 'ES703'

            when territory_code in ('ES704', 'ES704_O')
              or territory_code in ('35003', '35014', '35015', '35017', '35030')
                then 'ES704'

            when territory_code in ('ES705', 'ES705_O')
              or territory_code in ('35012', '35016', '35019')
                then 'ES705'

            when territory_code in ('ES706', 'ES706_O')
              or territory_code in ('38003', '38036', '38049', '38050')
                then 'ES706'

            when territory_code in ('ES707', 'ES707_O')
              or territory_code in (
                  '38009',
                  '38014',
                  '38024',
                  '38027',
                  '38037',
                  '38045'
              )
                then 'ES707'

            when territory_code in ('ES708', 'ES708_O')
              or territory_code in ('35004', '35010', '35024', '35028', '35034')
                then 'ES708'

            when territory_code in ('ES709', 'ES709_O')
              or territory_code in (
                  '38001',
                  '38006',
                  '38017',
                  '38019',
                  '38023',
                  '38028',
                  '38035',
                  '38038',
                  '38040'
              )
                then 'ES709'

            else null
        end as island_code

    from territories
)

select
    territory_code,
    territory_name_es,
    territory_level,
    island_code,

    case island_code
        when 'ES703' then 'El Hierro'
        when 'ES704' then 'Fuerteventura'
        when 'ES705' then 'Gran Canaria'
        when 'ES706' then 'La Gomera'
        when 'ES707' then 'La Palma'
        when 'ES708' then 'Lanzarote'
        when 'ES709' then 'Tenerife'
        else null
    end as island_name_es,

    territory_code ~ '^ES[0-9]{3}_O$' as is_residual

from classified