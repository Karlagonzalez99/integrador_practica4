{{ config(materialized='table') }}

with limites as (
    select
        least(
            (select min(fecha_corte) from {{ ref('stg_lotes_acopio') }}),
            (select min(fecha_embarque) from {{ ref('stg_embarques_exportacion') }})
        ) as fecha_min,
        greatest(
            (select max(fecha_corte) from {{ ref('stg_lotes_acopio') }}),
            (select max(fecha_embarque) from {{ ref('stg_embarques_exportacion') }})
        ) as fecha_max
)
select
    d::date as fecha,
    extract(year from d)::int as anio,
    extract(quarter from d)::int as trimestre,
    extract(month from d)::int as mes,
    to_char(d, 'TMMonth') as nombre_mes,
    extract(isodow from d)::int as dia_semana,
    (extract(isodow from d) in (6, 7)) as es_fin_semana
from limites,
     generate_series(fecha_min, fecha_max, interval '1 day') as d
