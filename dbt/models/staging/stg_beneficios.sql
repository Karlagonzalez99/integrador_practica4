{{ config(materialized='view') }}
select id_beneficio, nombre_beneficio, tipo_beneficio, municipio, latitud, longitud,
       capacidad_quintales_dia, costo_procesamiento_qq
from {{ source('raw', 'beneficios') }}
