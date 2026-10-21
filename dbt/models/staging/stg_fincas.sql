{{ config(materialized='view') }}
select id_finca, nombre_finca, id_productor, nombre_productor, region, municipio,
       latitud, longitud, altitud_msnm, area_manzanas
from {{ source('raw', 'fincas') }}
