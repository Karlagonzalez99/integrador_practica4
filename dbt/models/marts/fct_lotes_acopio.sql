{{ config(materialized='table') }}

with proceso_final as (
    select
        id_lote,
        id_beneficio,
        etapa,
        row_number() over (
            partition by id_lote
            order by fecha_inicio desc, id_proceso desc
        ) as rn
    from {{ ref('stg_procesamiento_beneficio') }}
)
select
    l.id_lote,
    l.id_finca,
    l.id_variedad,
    l.id_cuadrilla,
    l.fecha_corte as fecha,
    pf.id_beneficio as id_beneficio_final,
    pf.etapa as etapa_final,
    l.peso_cereza_kg,
    l.humedad_porcentaje,
    l.puntaje_catacion_scaa,
    l.costo_recoleccion_nio,
    l.certificacion,
    l.estado_lote,
    c.precipitacion_mm,
    c.temperatura_media_c,
    c.temperatura_min_c,
    c.temperatura_max_c,
    c.humedad_relativa_pct,
    c.condicion_clima
from {{ ref('stg_lotes_acopio') }} l
left join proceso_final pf
    on pf.id_lote = l.id_lote and pf.rn = 1
left join {{ ref('stg_fincas') }} f
    on f.id_finca = l.id_finca
left join {{ ref('stg_clima_zonas_cafetaleras') }} c
    on c.fecha = l.fecha_corte and c.region = f.region
