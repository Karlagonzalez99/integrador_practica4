{{ config(materialized='table') }}

select
    e.id_embarque,
    e.id_lote,
    l.id_finca,
    l.id_variedad,
    l.id_beneficio_final,
    e.fecha_embarque as fecha,
    e.puerto_salida,
    e.pais_destino,
    e.cliente_comprador,
    e.peso_oro_quintales,
    e.precio_quintal_usd,
    e.flete_transporte_usd,
    e.total_usd,
    e.flete_transporte_usd / nullif(e.peso_oro_quintales, 0) as flete_por_quintal_usd
from {{ ref('stg_embarques_exportacion') }} e
left join {{ ref('fct_lotes_acopio') }} l
    on l.id_lote = e.id_lote
