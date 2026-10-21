{{ config(materialized='view') }}
select fecha, region, precipitacion_mm, temperatura_media_c, temperatura_min_c,
       temperatura_max_c, humedad_relativa_pct, condicion_clima
from {{ source('raw', 'clima_zonas_cafetaleras') }}
