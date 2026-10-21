{{ config(materialized='table') }}

select
    id_finca,
    nombre_finca,
    id_productor,
    nombre_productor,
    region,
    municipio,
    latitud,
    longitud,
    altitud_msnm,
    case 
        when altitud_msnm >= 1200 then 'Estrictamente Altura (SHG)'
        when altitud_msnm >= 900 then 'Altura (HG)'
        else 'Estándar Central'
    end as clasificacion_altura,
    area_manzanas
from {{ ref('stg_fincas') }}
